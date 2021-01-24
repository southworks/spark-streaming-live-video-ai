import json
import os

from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError


class KafkaManager:

    videos_topic = os.getenv("KAFKA_VIDEOS_TOPIC")
    frames_topic = os.getenv("KAFKA_FRAMES_TOPIC")
    kafka_server = f'{os.getenv("KAFKA_HOST")}:{os.getenv("KAFKA_PORT")}'

    def __init__(self):
        self.create_topics()

    def get_admin(self):
        return KafkaAdminClient(
            bootstrap_servers=self.kafka_server,
            client_id='admin'
        )

    def create_topics(self):
        topic_list = []
        topic_list.append(NewTopic(name=self.videos_topic, num_partitions=1, replication_factor=1))
        topic_list.append(NewTopic(name=self.frames_topic, num_partitions=1, replication_factor=1))
        try:
            self.get_admin().create_topics(new_topics=topic_list, validate_only=False)
        except TopicAlreadyExistsError:
            pass

    def get_broker(self):
        return KafkaProducer(bootstrap_servers=[self.kafka_server],
                             value_serializer=lambda x:
                             json.dumps(x).encode('utf-8'))

    def send_video(self, video):
        producer = self.get_broker()
        producer.send(self.videos_topic, video)
