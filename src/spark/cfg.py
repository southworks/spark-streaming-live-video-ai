import os

# Cassandra configuration
cassandra_host = os.getenv("CASSANDRA_HOST")
cassandra_port = os.getenv("CASSANDRA_PORT")
cassandra_keyspace = os.getenv("CASSANDRA_KEYSPACE")
cassandra_analysis_table = os.getenv("CASSANDRA_ANALYSIS_TABLE")
cassandra_videos_table = os.getenv("CASSANDRA_VIDEOS_TABLE")
cassandra_metrics_table = os.getenv("CASSANDRA_METRICS_TABLE")

# Kafka configuration
kafka_host = os.getenv("KAFKA_HOST")
kafka_port = os.getenv("KAFKA_PORT")
kafka_videos_topic = os.getenv("KAFKA_VIDEOS_TOPIC")
kafka_frames_topic = os.getenv("KAFKA_FRAMES_TOPIC")

# Resize configuration
target_height = int(os.getenv("RESIZE_TARGET_HEIGHT"))

# Frame storage configuration
frame_storage_path = "/opt/bitnami/spark/frames"

# Nginx
NGINX_HOST = "nginx"

# Spark repartition
ingest_job_repartition = 1
storage_job_repartition = 1
inference_job_repartition = 2
