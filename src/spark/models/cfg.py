import os

if os.path.exists("spark-jobs"):
    models_path = os.path.join('spark-jobs', 'models', 'pretrained')
else:
    models_path = os.path.join('models', 'pretrained')

gender_detection_model_path = os.path.join(models_path, 'gender_detection.hdf5')
emotion_detection_model_path = os.path.join(models_path, 'emotion_detection.hdf5')
yolo_path = os.path.join(models_path, 'yolo_v3.h5')

yolo_labels = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck",
               "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
               "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe",
               "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard",
               "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard",
               "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana",
               "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake",
               "chair", "sofa", "pottedplant", "bed", "diningtable", "toilet", "tvmonitor", "laptop", "mouse",
               "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator",
               "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"]

emotion_labels = {0: 'angry', 1: 'disgust', 2: 'fear', 3: 'happy', 4: 'sad', 5: 'surprise', 6: 'neutral'}
gender_labels = {0: 'woman', 1: 'man'}

gender_offsets = (10, 10)
emotion_offsets = (0, 0)

yolo_input_size = (416, 416)
color_detection_input_size = (128, 128)
