from base64 import b64encode
import json
import math
import sys
import time
from uuid import UUID

from cassandra.cluster import Cluster
import cfg
import cv2
from kafka import KafkaProducer
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import ArrayType, IntegerType, StringType, StructField, StructType


class RowProcessor:
    session = None
    cluster = None

    def open(self, partition_id, epoch_id):  # noqa: A003
        self.cluster = Cluster(contact_points=[cfg.cassandra_host], port=cfg.cassandra_port)
        self.session = self.cluster.connect()
        return True

    def process(self, row):
        self.session.execute("UPDATE videoanalysis.videos SET status = 'Processing' WHERE video_id ={};"
                             .format(UUID(row["video_id"])))
        try:
            ingest_metrics = get_frames(row["video_id"], row["video_url"], row["models_to_run"], row["frame_step"])
            for m in ingest_metrics:
                self.session.execute(" INSERT INTO videoanalysis.metrics (video_id, metric_name, metric_value)"
                                     " VALUES ({}, '{}', {})".format(UUID(row["video_id"]), m[0], m[1]))
        except Exception as e:
            self.session.execute("UPDATE videoanalysis.videos SET status = 'Failed', error = '{}' WHERE video_id ={};"
                                 .format(e, UUID(row["video_id"])))

    def close(self, error):
        self.cluster.shutdown()


# Video message schema
video_schema = StructType([StructField("video_id", StringType(), False),
                          StructField("video_url", StringType(), False),
                          StructField("models_to_run", ArrayType(StringType()), False),
                          StructField("frame_step", IntegerType(), False)])

# Build spark session
spark = SparkSession \
    .builder \
    .appName("Video-Ingestion") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")


def frame_encode(img):
    retval, buffer = cv2.imencode('.jpg', img)
    buffer64 = b64encode(buffer)
    buffer64s = buffer64.decode('utf-8')
    return buffer64s


def calculate_resize(w, h, target_h):
    if h <= target_h:
        return w, h

    else:
        gcd = math.gcd(w, h)

        img_width = w/gcd
        img_height = h/gcd

        ratio = math.floor(target_h / img_height)

        return (int(ratio * img_width), int(ratio * img_height))


def resize_frame(img, target_h):
    height, width, _ = img.shape
    target_size = calculate_resize(width, height, target_h)
    resized_image = cv2.resize(img, target_size)
    encoded_image = frame_encode(resized_image)

    return str(encoded_image)


def get_frames(video_id, video_url, models_to_run, frame_step):
    print("Processing video_id: {} video_url: {}".format(video_id, video_url))
    start_framing = time.time()
    producer = KafkaProducer(bootstrap_servers=["{}:{}".format(cfg.kafka_host, cfg.kafka_port)],
                             value_serializer=lambda x:
                             json.dumps(x).encode('utf-8'))
    video = cv2.VideoCapture(video_url)
    if not video.isOpened():
        raise Exception("Could not capture frames from {}".format(video_url))
    counter = 0
    resize_time = 0.0
    sum_msg_size = 0
    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            video.release()
            # Send a empty frame to indicate end of video
            message = {
                'video_id': video_id,
                'frame_number': 0,
                'buffer': '',
                'timestamp': video.get(cv2.CAP_PROP_POS_MSEC) / 1000
            }
            sum_msg_size += sys.getsizeof(message)
            producer.send(cfg.kafka_frames_topic, message)

        else:
            counter += 1
            if counter % frame_step == 0:
                start_resize = time.time()
                buffer64s = resize_frame(frame, int(cfg.target_height))
                resize_time += time.time() - start_resize
                message = {
                    'video_id': video_id,
                    'frame_number': counter,
                    'buffer': buffer64s,
                    'timestamp': video.get(cv2.CAP_PROP_POS_MSEC) / 1000,
                    'models_to_run': models_to_run
                }
                sum_msg_size += sys.getsizeof(message)
                producer.send(cfg.kafka_frames_topic, message)

    end_framing = time.time()
    elapsed = end_framing - start_framing
    total_frames = float(math.floor(counter / frame_step))
    print("Processing finished after {}".format(elapsed))
    return [("Video Ingest Time", elapsed - resize_time),
            ("Frame Resize Time", resize_time),
            ("Total Frames Extracted", total_frames),
            ("Average message size (Bytes)", float(sum_msg_size / total_frames))]


def main():
    # Read video message from Kafka
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "{}:{}".format(cfg.kafka_host, cfg.kafka_port)) \
        .option("subscribe", cfg.kafka_videos_topic) \
        .load() \
        .selectExpr("CAST(value as STRING) as message") \
        .select(from_json(col('message'), video_schema).alias("json")) \
        .select("json.*")

    writer = df.repartition(cfg.ingest_job_repartition).writeStream.foreach(RowProcessor())
    writer.start().awaitTermination()


if __name__ == "__main__":
    main()
