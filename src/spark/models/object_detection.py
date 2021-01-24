from base64 import b64decode
import io
import json
import time

from keras.preprocessing.image import img_to_array
import numpy as np
from numpy import expand_dims
from PIL import Image

from . import cfg

# define the labels
labels = cfg.yolo_labels


class BoundBox:
    def __init__(self, xmin, ymin, xmax, ymax, objness=None, classes=None):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.objness = objness
        self.classes = classes
        self.label = -1
        self.score = -1

    def get_label(self):
        if self.label == -1:
            self.label = np.argmax(self.classes)

        return self.label

    def get_score(self):
        if self.score == -1:
            self.score = self.classes[self.get_label()]

        return self.score

    def get_coordinates(self):
        width = self.xmax - self.xmin
        height = self.ymax - self.ymin
        return [self.xmin, self.ymin, width, height]


def _sigmoid(x):
    return 1. / (1. + np.exp(-x))


def decode_netout(netout, anchors, obj_thresh, net_h, net_w):
    grid_h, grid_w = netout.shape[:2]
    nb_box = 3
    netout = netout.reshape((grid_h, grid_w, nb_box, -1))
    boxes = []
    netout[..., :2] = _sigmoid(netout[..., :2])
    netout[..., 4:] = _sigmoid(netout[..., 4:])
    netout[..., 5:] = netout[..., 4][..., np.newaxis] * netout[..., 5:]
    netout[..., 5:] *= netout[..., 5:] > obj_thresh

    for i in range(grid_h*grid_w):
        row = i / grid_w
        col = i % grid_w
        for b in range(nb_box):
            # 4th element is objectness score
            objectness = netout[int(row)][int(col)][b][4]
            if(objectness.all() <= obj_thresh):
                continue
            # first 4 elements are x, y, w, and h
            x, y, w, h = netout[int(row)][int(col)][b][:4]
            x = (col + x) / grid_w  # center position, unit: image width
            y = (row + y) / grid_h  # center position, unit: image height
            w = anchors[2 * b + 0] * np.exp(w) / net_w  # unit: image width
            h = anchors[2 * b + 1] * np.exp(h) / net_h  # unit: image height
            # last elements are class probabilities
            classes = netout[int(row)][col][b][5:]
            box = BoundBox(x-w/2, y-h/2, x+w/2, y+h/2, objectness, classes)
            boxes.append(box)
    return boxes


def correct_yolo_boxes(boxes, image_h, image_w, net_h, net_w):
    for i in range(len(boxes)):
        boxes[i].xmin = int(boxes[i].xmin * image_w)
        boxes[i].xmax = int(boxes[i].xmax * image_w)
        boxes[i].ymin = int(boxes[i].ymin * image_h)
        boxes[i].ymax = int(boxes[i].ymax * image_h)


def _interval_overlap(interval_a, interval_b):
    x1, x2 = interval_a
    x3, x4 = interval_b
    if x3 < x1:
        if x4 < x1:
            return 0
        else:
            return min(x2, x4) - x1
    else:
        if x2 < x3:
            return 0
        else:
            return min(x2, x4) - x3


def bbox_iou(box1, box2):
    intersect_w = _interval_overlap([box1.xmin, box1.xmax], [box2.xmin, box2.xmax])
    intersect_h = _interval_overlap([box1.ymin, box1.ymax], [box2.ymin, box2.ymax])
    intersect = intersect_w * intersect_h
    w1, h1 = box1.xmax-box1.xmin, box1.ymax-box1.ymin
    w2, h2 = box2.xmax-box2.xmin, box2.ymax-box2.ymin
    union = w1*h1 + w2*h2 - intersect
    return float(intersect) / union


def do_nms(boxes, nms_thresh):
    if len(boxes) > 0:
        nb_class = len(boxes[0].classes)
    else:
        return
    for c in range(nb_class):
        sorted_indices = np.argsort([-box.classes[c] for box in boxes])
        for i in range(len(sorted_indices)):
            index_i = sorted_indices[i]
            if boxes[index_i].classes[c] == 0:
                continue
            for j in range(i+1, len(sorted_indices)):
                index_j = sorted_indices[j]
                if bbox_iou(boxes[index_i], boxes[index_j]) >= nms_thresh:
                    boxes[index_j].classes[c] = 0


# get all of the results above a threshold
def get_boxes(boxes, labels, thresh):
    v_boxes, v_labels, v_scores = [], [], []
    # enumerate all boxes
    for box in boxes:
        # enumerate all possible labels
        for i in range(len(labels)):
            # check if the threshold for this label is high enough
            if box.classes[i] > thresh:
                v_boxes.append(box)
                v_labels.append(labels[i])
                v_scores.append(box.classes[i]*100)
                # don't break, many labels may trigger for one box
    return v_boxes, v_labels, v_scores


def load_image_pixels_from_bytes(image, shape):
    img = Image.open(io.BytesIO(image))
    img = img.convert('RGB')
    width, height = img.size
    img = img.resize(shape)
    img = img_to_array(img)
    img /= 255.0
    img = expand_dims(img, 0)
    return img, width, height


def detect_objects(frame, models):
    # define the expected input shape for the model
    object_detection_model = models["object_detection_model"]
    input_w, input_h = 416, 416
    imgdata = b64decode(frame)
    image, image_w, image_h = load_image_pixels_from_bytes(imgdata, (input_w, input_h))
    # make prediction
    start = time.time()
    prediction = object_detection_model.predict(image)
    end = time.time()
    # define the anchors
    anchors = [[116, 90, 156, 198, 373, 326], [30, 61, 62, 45, 59, 119], [10, 13, 16, 30, 33, 23]]
    # define the probability threshold for detected objects
    class_threshold = 0.6
    boxes = []
    for i in range(len(prediction)):
        # decode the output of the network
        boxes += decode_netout(prediction[i][0], anchors[i], class_threshold, input_h, input_w)
    # correct the sizes of the bounding boxes for the shape of the image
    correct_yolo_boxes(boxes, image_h, image_w, input_h, input_w)
    # suppress non-maximal boxes
    do_nms(boxes, 0.5)

    # get the details of the detected objects
    v_boxes, v_labels, v_scores = get_boxes(boxes, labels, class_threshold)

    result = []

    # summarize what we found

    for i in range(len(v_boxes)):
        box_coordinates = []
        for box in v_boxes:
            box_coordinates.append(box.get_coordinates())
        result_json = {
            "label": v_labels[i],
            "probability": v_scores[i],
            "coordinates": box_coordinates[i]
        }
        result.append(json.dumps(result_json))

    elapsed_time = end - start
    output = {"inference_model": "Object Detection", "inference_results": result,
              "inference_start_time": round(start, 4), "inference_time": round(elapsed_time, 4)}

    return json.dumps(output)
