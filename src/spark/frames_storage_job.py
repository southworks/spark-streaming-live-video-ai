import base64
from pathlib import Path

import cfg
import cv2
import numpy as np
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import DoubleType, IntegerType, StringType, StructField, StructType


class RowProcessor:

    def open(self, partition_id, epoch_id):  # noqa: A003
        return True

    def process(self, row):
        if row["buffer"] != "":
            store_frame(row)

    def close(self, error):
        pass


# **Create schema for data deserialization**

img_schema = StructType([StructField("video_id", StringType(), False),
                         StructField("frame_number", IntegerType(), False),
                         StructField("timestamp", DoubleType(), False),
                         StructField("buffer", StringType(), False)])

# Build spark session
spark = SparkSession \
    .builder \
    .appName("frames-storage") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")


def store_frame(row):
    decoded_image = base64.b64decode(row["buffer"])
    np_data = np.frombuffer(decoded_image, np.uint8)
    img = cv2.imdecode(np_data, cv2.IMREAD_UNCHANGED)
    storage_path = "{}/{}".format(cfg.frame_storage_path, row["video_id"])
    Path(storage_path).mkdir(parents=True, exist_ok=True)
    save_path = "{}/{}.jpg".format(storage_path, row["frame_number"])
    cv2.imwrite(save_path, img)


def main():
    # Read video message from Kafka
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "{}:{}".format(cfg.kafka_host, cfg.kafka_port)) \
        .option("subscribe", cfg.kafka_frames_topic) \
        .load() \
        .selectExpr("CAST(value as STRING) as message") \
        .select(from_json(col('message'), img_schema).alias("json")) \
        .select("json.*")

    df.repartition(cfg.storage_job_repartition) \
      .writeStream.foreach(RowProcessor()) \
      .start().awaitTermination()


if __name__ == "__main__":
    main()
