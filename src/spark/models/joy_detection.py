from base64 import b64decode
from io import BytesIO
import json
import time

import cv2
from keras.preprocessing import image
import numpy as np
from PIL import Image, ImageOps

from . import cfg


def detect_emotions(img, models):
    arr = []
    face_detection_model = models["face_detection_model"]
    emotion_detection_model = models["emotion_detection_model"]
    gender_detection_model = models["gender_detection_model"]

    emotion_target_size = emotion_detection_model.input_shape[1:3]
    gender_target_size = gender_detection_model.input_shape[1:3]

    rgb_img, gs_img = preprocess_frame(img)
    start = time.time()
    faces = face_recognition(face_detection_model, rgb_img)
    model_output = run_prediction(faces, emotion_detection_model, gender_detection_model,
                                  rgb_img, gs_img, emotion_target_size, gender_target_size, arr)

    end = time.time()
    elapsed_time = end - start
    output = {"inference_model": "Joy Detection", "inference_results": model_output,
              "inference_start_time": round(start, 4), "inference_time": round(elapsed_time, 4)}

    return json.dumps(output)


def face_recognition(detection_model, gray_image_array):
    return detection_model.detect_faces(gray_image_array)


def load_image(img, grayscale=False, target_size=None):
    pil_image = Image.open(BytesIO(b64decode(img)))
    if grayscale:
        pil_image = ImageOps.grayscale(pil_image)
    return image.img_to_array(pil_image)


def adapt_color(x, v2=True):
    x = x.astype("float32")
    x = x / 255.0
    if v2:
        x = x - 0.5
        x = x * 2.0
    return x


def apply_offsets(face_coordinates, offsets):
    x, y, width, height = face_coordinates
    x_off, y_off = offsets
    return (x - x_off, x + width + x_off, y - y_off, y + height + y_off)


def preprocess_frame(image):
    rgb_image = load_image(image, grayscale=False)
    gray_image = load_image(image, grayscale=True)
    gray_image = np.squeeze(gray_image)
    gray_image = gray_image.astype("uint8")
    return rgb_image, gray_image


def run_prediction(faces, emotion_detection_model, gender_detection_model,
                   rgb_image, gray_image, emotion_target_size, gender_target_size, arr):

    for ix, face in enumerate(faces):
        face_coordinates = face['box']
        x1, x2, y1, y2 = apply_offsets(face_coordinates, cfg.gender_offsets)
        _rgb_image = rgb_image[y1:y2, x1:x2]

        x1, x2, y1, y2 = apply_offsets(face_coordinates, cfg.emotion_offsets)
        _gray_image = gray_image[y1:y2, x1:x2]

        try:
            _rgb_image = cv2.resize(_rgb_image, (gender_target_size))
            _gray_image = cv2.resize(_gray_image, (emotion_target_size))
        except Exception:
            continue

        _rgb_image = adapt_color(_rgb_image, False)
        _rgb_image = np.expand_dims(_rgb_image, 0)
        gender_prediction = gender_detection_model.predict(_rgb_image)
        gender_label_arg = np.argmax(gender_prediction)
        gender_text = cfg.gender_labels[gender_label_arg]

        _gray_image = adapt_color(_gray_image, True)
        _gray_image = np.expand_dims(_gray_image, 0)
        _gray_image = np.expand_dims(_gray_image, -1)
        emotion_label_arg = np.argmax(emotion_detection_model.predict(_gray_image))
        emotion_text = cfg.emotion_labels[emotion_label_arg]

        det = {"face_id": ix, "coordinates": face_coordinates, "gender": gender_text, "emotion": emotion_text}
        arr.append(json.dumps(det))

    return arr
