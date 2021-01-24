from uuid import UUID

from cassandra.cluster import Cluster
import cfg
from inference_helper import load_models, run_inferences
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode_outer, from_json, udf
from pyspark.sql.types import ArrayType, DoubleType, IntegerType, StringType, StructField, StructType


class RowProcessor:
    session = None
    cluster = None

    def open(self, partition_id, epoch_id):  # noqa: A003
        self.cluster = Cluster(contact_points=[cfg.cassandra_host], port=cfg.cassandra_port)
        self.session = self.cluster.connect()
        return True

    def process(self, row):
        try:
            if(row["buffer"]) != "":
                self.session.execute(" INSERT INTO videoanalysis.analysis (video_id, frame_number, video_timestamp,"
                                     " inference_model, inference_start_time, inference_results, inference_time)"
                                     " VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                     (UUID(row["video_id"]), row["frame_number"], row["video_timestamp"],
                                      row["inference_model"], row["inference_start_time"],
                                      row["inference_results"], row["inference_time"]))
            else:
                self.session.execute("UPDATE videoanalysis.videos SET status = 'Completed' WHERE video_id =%s",
                                     [UUID(row["video_id"])])

        except Exception as e:
            self.session.execute("UPDATE videoanalysis.videos SET status = 'Failed', error = %s WHERE video_id =%s",
                                 (e, UUID(row["video_id"])))

    def close(self, error):
        self.cluster.shutdown()


# ## Schemas

# **Create schema for data deserialization**

img_schema = StructType([StructField("video_id", StringType(), False),
                         StructField("frame_number", IntegerType(), False),
                         StructField("timestamp", DoubleType(), False),
                         StructField("buffer", StringType(), False),
                         StructField("models_to_run", ArrayType(StringType()), False)])

# **Model output deserialization**

analysis_schema = StructType([StructField("inference_model", StringType(), False),
                              StructField("inference_results", StringType(), False),
                              StructField("inference_start_time", DoubleType(), False),
                              StructField("inference_time", DoubleType(), False)])

spark = SparkSession \
    .builder \
    .appName("video-analysis") \
    .config("spark.cassandra.connection.host", cfg.cassandra_host) \
    .config("spark.cassandra.connection.port", cfg.cassandra_port) \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

models = load_models()
models_bc = spark._sc.broadcast(models)

predict_udf = udf(lambda frame, model, frame_number: run_inferences(
    frame, models_bc.value, model, frame_number), StringType()).asNondeterministic()

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "{}:{}".format(cfg.kafka_host, cfg.kafka_port)) \
    .option("subscribe", cfg.kafka_frames_topic) \
    .option("maxOffsetsPerTrigger", 2) \
    .load()

frame_df = df.selectExpr("CAST(value as STRING) as message") \
    .select(from_json(col('message'), img_schema).alias("json")) \
    .select("json.*")

analysis_df = frame_df.withColumn("model_to_run", explode_outer("models_to_run")) \
    .withColumn("analysis", predict_udf(col("buffer"), col("model_to_run"), col("frame_number"))) \
    .repartition(cfg.inference_job_repartition) \
    .withColumn("data", from_json("analysis", analysis_schema)) \
    .select(col("video_id"), col("frame_number"), col("buffer"), col("timestamp").alias("video_timestamp"),
            col("data.*"))

analysis_df.writeStream.foreach(RowProcessor()) \
    .option("checkpointLocation", '/tmp/check_point/analyisis/')\
    .start() \
    .awaitTermination()
