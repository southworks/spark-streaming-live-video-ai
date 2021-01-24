import os

from cassandra_repository import CassandraRepository


class StreamingHelper:
    streaming_video_id = None

    # Cassandra configuration
    __cassandra_host = os.getenv("CASSANDRA_HOST")
    __cassandra_port = os.getenv("CASSANDRA_PORT")
    __cassandra_keyspace = os.getenv("CASSANDRA_KEYSPACE")

    __cassandra = CassandraRepository(__cassandra_host, __cassandra_port, __cassandra_keyspace)

    def is_streaming_available(self):
        if self.streaming_video_id is None:
            return True
        else:
            result = self.__cassandra.get_video(self.streaming_video_id)
            if result[0]['status'] in ('Processing', 'Pending'):
                return False
            else:
                return True
