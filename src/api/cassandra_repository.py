from datetime import datetime
import sys
from uuid import UUID

from cassandra.cluster import Cluster, NoHostAvailable
from cassandra.cqlengine import columns, connection
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import Model


class CassandraRepository:
    session = None

    def __init__(self, host, port, keyspace):
        try:
            self.session = Cluster(contact_points=[host], port=port).connect()
            connection.register_connection('cluster', session=self.session)
            self.session.execute("""
                CREATE KEYSPACE IF NOT EXISTS %s
                WITH REPLICATION = { 'class': 'NetworkTopologyStrategy', 'datacenter1':1 }
                AND durable_writes = true
                """ % keyspace)
            self.session.set_keyspace(keyspace)

            sync_table(self.Analysis, keyspaces=[keyspace], connections=["cluster"])
            sync_table(self.Metrics, keyspaces=[keyspace], connections=["cluster"])
            sync_table(self.Videos, keyspaces=[keyspace], connections=["cluster"])

        except NoHostAvailable:
            print("No active Cassandra instance was found at {0}:{1}. If you are using another host or port, "
                  "please make sure to set $CASSANDRA_HOST and $CASSANDRA_PORT before running".format(host, port))
            sys.exit(1)

    def get_results(self, video_id):
        return self.__get_by_video_id("analysis", video_id)

    def get_video(self, video_id):
        return self.__get_by_video_id("videos", video_id)

    def get_metrics(self, video_id):
        return self.__get_by_video_id("metrics", video_id)

    def __get_by_video_id(self, table_name, video_id):
        return self.session.execute("SELECT * FROM {} WHERE video_id=%s ALLOW FILTERING".format(table_name),
                                    (UUID(video_id),))

    def insert_video(self, video_url, video_id, video_name, frame_step):
        status = "Pending"
        self.session.execute("INSERT INTO videoanalysis.videos "
                             "(video_id, video_url, status, frame_step, ts, video_name)"
                             "VALUES (%s, %s, %s, %s, %s, %s)",
                             (video_id, video_url, status, int(frame_step), datetime.now(), video_name))
        return {
            "video_id": str(video_id),
            "video_url": video_url,
            "status": status,
            "video_name": video_name
        }

    def get_results_by_frame_number(self, video_id, frame_number):
        return self.session.execute("SELECT * FROM analysis WHERE video_id=%s AND frame_number=%s ALLOW FILTERING",
                                    (UUID(video_id), int(frame_number)))

    def get_greatest_frame_analysed(self, video_id):
        return self.session.execute("SELECT MAX(frame_number) as greatest_frame FROM analysis WHERE video_id=%s",
                                    (video_id,))

    def get_completed_videos(self):
        results = self.session.execute("SELECT * from videos WHERE status='Completed' ALLOW FILTERING")
        videos = list(results)
        return videos

    class Videos(Model):
        video_id = columns.UUID(primary_key=True)
        video_url = columns.Text()
        status = columns.Text()
        ts = columns.DateTime()
        frame_step = columns.Integer()
        error = columns.Text()
        video_name = columns.Text()

    class Metrics(Model):
        video_id = columns.UUID(primary_key=True)
        metric_name = columns.Text(primary_key=True, clustering_order='ASC')
        metric_value = columns.Decimal()

    class Analysis(Model):
        video_id = columns.UUID(primary_key=True)
        frame_number = columns.Integer(primary_key=True)
        video_timestamp = columns.Decimal()
        inference_model = columns.Text(primary_key=True)
        inference_results = columns.Text()
        inference_start_time = columns.Decimal()
        inference_time = columns.Decimal()
