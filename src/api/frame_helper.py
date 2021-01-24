import json

import cv2


class FrameHelper:

    def draw_bounding_box(frame, coordinates, label):
        x, y, width, height = coordinates
        box_point_1 = (x, y)
        box_point_2 = (x + width, y + height)
        cv2.rectangle(frame, box_point_1, box_point_2, (0, 255, 0), 2)
        labelSize = cv2.getTextSize(label, cv2.FONT_HERSHEY_COMPLEX, 0.4, 2)
        bg_point_2 = (x + labelSize[0][0], y - int(labelSize[0][1]))
        cv2.rectangle(frame, box_point_1, bg_point_2, (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, label, box_point_1, cv2.FONT_HERSHEY_COMPLEX, 0.4, (0, 0, 1), 1)

        return frame

    def draw_results(frame_path, results):
        frame = cv2.imread(frame_path, cv2.IMREAD_UNCHANGED)
        for result in results:
            inference_model = result["inference_model"]
            inference_results = json.loads(result["inference_results"])
            if inference_model == "Object Detection":
                for inference_result in inference_results:
                    detected_object = json.loads(inference_result)
                    label = "{} {}".format(detected_object['label'], detected_object['probability'])
                    frame = FrameHelper.draw_bounding_box(frame, detected_object['coordinates'], label)
            elif inference_model == "Joy Detection":
                for inference_result in inference_results:
                    face = json.loads(inference_result)
                    label = "{} {}".format(face['gender'], face['emotion'])
                    frame = FrameHelper.draw_bounding_box(frame, face['coordinates'], label)

        retval, buffer = cv2.imencode('.jpg', frame)
        return buffer.tobytes()
