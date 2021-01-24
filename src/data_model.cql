DROP KEYSPACE IF EXISTS videoanalysis;

CREATE keyspace videoanalysis with replication={'class':'NetworkTopologyStrategy', 'datacenter1':1} AND durable_writes = true;
USE videoanalysis;
CREATE TABLE videos(video_id uuid PRIMARY KEY, video_url text, status text, frame_step int, ts timestamp, error text);
CREATE TABLE metrics(video_id uuid, metric_name text, metric_value decimal, PRIMARY KEY(video_id, metric_name)) WITH CLUSTERING ORDER BY (metric_name ASC);
CREATE TABLE analysis(video_id uuid, frame_number int, video_timestamp decimal, inference_model text,inference_start_time text, inference_results text, inference_time decimal, PRIMARY KEY(video_id, frame_number, inference_model));
