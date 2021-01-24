import json
import os
import uuid

from cassandra_repository import CassandraRepository
from flask import Flask, jsonify, request
from flask.helpers import make_response
from flask_cors import CORS
from frame_helper import FrameHelper
from kafka_broker import KafkaManager
from streaming_helper import StreamingHelper

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

app = Flask(__name__)
CORS(app)

# Initialize Kafka
kafka_manager = KafkaManager()

# Cassandra configuration
cassandra_host = os.getenv("CASSANDRA_HOST")
cassandra_port = os.getenv("CASSANDRA_PORT")
cassandra_keyspace = os.getenv("CASSANDRA_KEYSPACE")

cassandra = CassandraRepository(cassandra_host, cassandra_port, cassandra_keyspace)
streaming_helper = StreamingHelper()


@app.route("/", methods=["GET"])
def home():
    return "Home"


# POST send video to kafka
@app.route('/analysis/start', methods=['POST'])
def post_video_stream():
    if not (request.headers.__contains__("Content-Type") and request.headers["Content-Type"] == "application/json"):
        return "'Content-Type' must be 'application/json'", 400
    video_url = request.json['videoURL']
    models_to_run = request.json['modelsToRun']
    video_name = request.json['videoName']
    frame_step = get_frame_step()
    result = urlparse(video_url)
    if all([result.scheme, result.netloc, result.path]):
        video_id = uuid.uuid4()
        video = cassandra.insert_video(video_url, video_id, video_name, frame_step)
        video['models_to_run'] = models_to_run
        video['frame_step'] = frame_step
        kafka_manager.send_video(video)
        video["status_url"] = f'{request.host_url}analysis/{video_id}'
        return jsonify(video), 201
    else:
        return "Valid URL must be provided", 400


# GET Analysis Results
@app.route("/analysis/<video_id>/results", methods=["GET"])
def get_analysis_results(video_id):
    try:
        results = cassandra.get_results(video_id)
        if results:
            response = format_results_response(list(results))
            return jsonify(response), 200
        else:
            return "No matches found for video with ID: {}".format(video_id), 404
    except ValueError:
        return "Invalid input: ID Must be UUID", 400


# GET Analysis status
@app.route('/analysis/<video_id>', methods=['GET'])
def get_analysis(video_id):
    result = cassandra.get_video(video_id)
    if result:
        response_with_links = add_result_endpoint_link(result.one())
        response_with_max_frame = get_max_frame_number(response_with_links)

        return jsonify(response_with_max_frame), 200
    else:
        return "No matches found for video with ID: {}".format(video_id), 404


@app.route("/analysis/<video_id>/frame/<frame_number>", methods=["GET"])
def get_analysis_frames(video_id, frame_number):
    results = cassandra.get_results_by_frame_number(video_id, frame_number)
    if results:
        frame_path = "/app/frames/{}/{}.jpg".format(video_id, frame_number)
        frame = FrameHelper.draw_results(frame_path, results)
        response = make_response(frame)
        response.headers['Content-Type'] = 'image/png'
        return response
    else:
        return "No matches found for video with ID: {} and frame number: {}".format(video_id, frame_number), 404


@app.route("/analysis/<video_id>/frame/<frame_number>/results", methods=["GET"])
def get_frame_results(video_id, frame_number):
    results = cassandra.get_results_by_frame_number(video_id, frame_number)
    if results:
        return jsonify(list(results)), 200
    else:
        return "No matches found for video with ID: {} and frame number: {}".format(video_id, frame_number), 404


@app.route("/analysis/<video_id>/metrics", methods=["GET"])
def get_metrics(video_id):
    try:
        res = cassandra.get_metrics(video_id)
        if res:
            return jsonify(list(res)), 200
        else:
            return "No matches found for video with ID: {}".format(video_id), 404
    except ValueError:
        return "Invalid input: ID Must be UUID", 400


def format_results_response(result_list):
    for result in result_list:
        result["frames_url"] = f'{request.host_url}analysis/{result["video_id"]}/frame/{result["frame_number"]}'
        inference_results = json.loads(result["inference_results"])
        result["inference_results"] = []
        for inference_result in inference_results:
            result["inference_results"].append(json.loads(inference_result))
    return result_list


# POST rtmp endpoint
@app.route("/analysis/rtmp-endpoint", methods=["POST"])
def get_rtmp_endpoint():
    if not (request.headers.__contains__("Content-Type") and request.headers["Content-Type"] == "application/json"):
        return "'Content-Type' must be 'application/json'", 400

    video_id = uuid.uuid4()
    models_to_run = request.json['modelsToRun']
    video_name = request.json['videoName']
    public_rtmp_endpoint = f'rtmp://localhost/live/{video_id}'
    nginx_rtmp_endpoint = f'rtmp://{os.getenv("NGINX_HOST")}/live/{video_id}'
    frame_step = get_frame_step()

    if streaming_helper.is_streaming_available():
        video = cassandra.insert_video(nginx_rtmp_endpoint, video_id, video_name, frame_step)
        video['models_to_run'] = models_to_run
        video['frame_step'] = frame_step
        kafka_manager.send_video(video)
        video["rtmp_endpoint"] = public_rtmp_endpoint
        streaming_helper.streaming_video_id = str(video_id)
        return jsonify(video), 201
    else:
        return 'There is an active streaming video. ' \
               'At this moment we do not support processing multiple streaming videos in parallel', 503


# GET all videos
@app.route("/analysis/videos", methods=["GET"])
def get_videos():
    result = cassandra.get_completed_videos()
    if result:
        return jsonify(result), 200
    else:
        return "No videos found", 404


def add_result_endpoint_link(result):
    if result["status"] == "Completed":
        result["results_url"] = f'{request.host_url}analysis/{result["video_id"]}/results'
    return result


def get_max_frame_number(response_with_links):
    greatest_frame = cassandra.get_greatest_frame_analysed(response_with_links["video_id"])
    if greatest_frame:
        greatest_frame_number = greatest_frame.one()['greatest_frame']
        if greatest_frame_number is None:
            greatest_frame_number = 0
        response_with_links["greatest_frame_analyzed"] = greatest_frame_number
    return response_with_links


def get_frame_step():
    if 'frameStep' not in request.json or request.json['frameStep'] == '':
        frame_step = 1
    else:
        frame_step = int(request.json['frameStep'])
    return frame_step


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("API_PORT", 8000))
