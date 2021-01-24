from datetime import datetime

from keras.models import load_model
import models.cfg as cfg
import models.color_palette_detection as color_detection
import models.joy_detection as joy_detection
import models.object_detection as yolo
from mtcnn import MTCNN


def load_models():
    return {
        "face_detection_model": MTCNN(),
        "emotion_detection_model": load_model(cfg.emotion_detection_model_path, compile=False),
        "gender_detection_model": load_model(cfg.gender_detection_model_path, compile=False),
        "object_detection_model": load_model(cfg.yolo_path, compile=False)
    }


def run_inferences(frame, models, model_to_run, frame_number):
    print(f'{datetime.now()}. Running {model_to_run} for frame {frame_number}.')
    if frame == "":
        return {}
    if model_to_run == "objects_detection":
        return yolo.detect_objects(frame, models)
    if model_to_run == "emotions_detection":
        return joy_detection.detect_emotions(frame, models)
    if model_to_run == "color_detection":
        return color_detection.detect_colors(frame, models)
    return {}
