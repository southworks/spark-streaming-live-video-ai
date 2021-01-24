#!/bin/bash

docker_compose_folder="src"
first_sleep_time=60
looped_sleep_time=20
job_submit_sleep_time=15
service_waited="api"
logs_folder="logs/"
sleep_message="until ${service_waited} is ready to submit spark jobs"
data_dir="./data/frames/"

cd $docker_compose_folder || exit 1

# Create directories and set permissions needed
mkdir -p $logs_folder
mkdir -p $data_dir
chmod 777 $data_dir

if [[ $1 == "--gpu" ]]; then
  docker-compose -f docker-compose-gpu.yml up &>"${logs_folder}"docker-compose.log &
  echo "Called docker-compose up."
else
  docker-compose up &>"${logs_folder}"docker-compose.log &
  echo "Called docker-compose up."
fi

echo "Waiting $sleep_message"
sleep $first_sleep_time

while [ -z "$(docker-compose ps -q $service_waited)" ] || [ -z $(docker ps -q --no-trunc | grep $(docker-compose ps -q $service_waited)) ]; do
  echo "Waiting for Docker network to be ready. Re-querying in $looped_sleep_time"
  sleep $looped_sleep_time
done

docker-compose exec -T spark spark-submit --master spark://spark:7077 --total-executor-cores 1 --py-files spark-jobs/cfg.zip --jars /opt/bitnami/spark/jars/spark-sql-kafka-0-10_2.12-3.0.0.jar,/opt/bitnami/spark/jars/kafka-clients-2.6.0.jar,/opt/bitnami/spark/jars/spark-streaming-kafka-0-10_2.12-3.0.0.jar,/opt/bitnami/spark/jars/spark-token-provider-kafka-0-10_2.12-3.0.0.jar,/opt/bitnami/spark/jars/commons-pool2-2.8.1.jar spark-jobs/ingest_job.py &>"${logs_folder}"ingest_job.log &
echo "Ingest job submitted"
echo "Log redirected to ${logs_folder}ingest_job.log"
echo "Waiting ${job_submit_sleep_time} before submitting next job"
sleep $job_submit_sleep_time

docker-compose exec -T spark spark-submit --master spark://spark:7077 --total-executor-cores 1 --py-files spark-jobs/cfg.zip --jars /opt/bitnami/spark/jars/spark-sql-kafka-0-10_2.12-3.0.0.jar,/opt/bitnami/spark/jars/kafka-clients-2.6.0.jar,/opt/bitnami/spark/jars/spark-streaming-kafka-0-10_2.12-3.0.0.jar,/opt/bitnami/spark/jars/spark-token-provider-kafka-0-10_2.12-3.0.0.jar,/opt/bitnami/spark/jars/commons-pool2-2.8.1.jar,/opt/bitnami/spark/jars/spark-cassandra-connector-assembly_2.12-3.0.0.jar spark-jobs/frames_storage_job.py &>"${logs_folder}"frames_storage_job.log &
echo "Frames storage job submitted"
echo "Log redirected to ${logs_folder}frames_storage_job.log"
echo "Waiting $job_submit_sleep_time before submitting next job"
sleep $job_submit_sleep_time

docker-compose exec -T spark spark-submit --master spark://spark:7077 --total-executor-cores 2 --py-files spark-jobs/inference_dependencies.zip --jars /opt/bitnami/spark/jars/spark-sql-kafka-0-10_2.12-3.0.0.jar,/opt/bitnami/spark/jars/kafka-clients-2.6.0.jar,/opt/bitnami/spark/jars/spark-streaming-kafka-0-10_2.12-3.0.0.jar,/opt/bitnami/spark/jars/spark-token-provider-kafka-0-10_2.12-3.0.0.jar,/opt/bitnami/spark/jars/commons-pool2-2.8.1.jar,/opt/bitnami/spark/jars/spark-cassandra-connector-assembly_2.12-3.0.0.jar spark-jobs/inference_job.py &>"${logs_folder}"inference_job.log &
echo "Inference job submitted"
echo "Log redirected to ${logs_folder}inference_job.log"
sleep $job_submit_sleep_time
echo "Ready!"

echo "Startup ready."
exit 0
