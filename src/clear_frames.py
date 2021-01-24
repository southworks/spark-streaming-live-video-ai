import argparse
from datetime import datetime, timedelta
import os
from shutil import rmtree
import sys

from cassandra.cluster import Cluster, NoHostAvailable, UnresolvableContactPoints
from cassandra.cqlengine import connection

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--days', type=int, help="Remove all entries older than current minus N days")
parser.add_argument('-n', '--host', type=str, help="Cassandra hostname or IP", default="localhost")
parser.add_argument('-p', '--port', type=int, help="Cassandra port", default=9042)

args = parser.parse_args(sys.argv[1:])
frames_dir = os.path.join(os.getcwd(), 'data', 'frames')
limit_date = int((datetime.now() - timedelta(days=args.days)).timestamp() * 1000)


def delete_from(table, field, value, session):
    session.execute("""
    DELETE FROM %s where %s = %s
    """ % (table, field, value))


try:
    session = Cluster(contact_points=[args.host], port=args.host).connect()
    connection.register_connection('cluster', session=session)
    session.set_keyspace('videoanalysis')

except (NoHostAvailable, UnresolvableContactPoints):
    print("""
No active Cassandra instance was found at {}:{}. Make sure to pass the right values
for hostname and port using -n HOSTNAME and -p PORT options""".format(args.host, args.host))
    sys.exit(1)

vids = session.execute("""
SELECT video_id FROM videos where ts < %s allow filtering;
""" % limit_date)

for row in vids:
    delete_from('videos', 'video_id', row['video_id'], session)
    delete_from('analysis', 'video_id', row['video_id'], session)
    metrics = session.execute("""
    SELECT metric_id FROM metrics where video_id = %s allow filtering;
    """ % row['video_id'])
    for m in metrics:
        delete_from('metrics', 'metric_id', m['metric_id'], session)
    tmp_dir = os.path.join(frames_dir, str(row['video_id']))
    if os.path.exists(tmp_dir):
        rmtree(tmp_dir)
