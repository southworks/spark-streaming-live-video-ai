# Cassandra Data Models

## Analysis

```json
{
    "video_id": uuid,               // Generated unique ID for the video
    "frame_number": int,            // Frame number
    "video_timestamp": decimal,     // Refers to the video time corresponding to the frame
    "inference_model": text,        // Name of the inference model
    "inference_results": text,      // Results returned by the model (JSON)
    "inference_start_time": decimal // Inference starting time
    "inference_time": decimal       // Time elapsed while running the inference
}
```

## Videos

```json
{
    "video_id": uuid,               // Generated unique ID for the video
    "video_url": text,              // URL to the video
    "status": text,                 // Keeps track of the current status of the video within the pipeline
    "error": text,                  // Error message when the ingest job fail
    "video_name": text,             // Video name provided by the user
    "frame_step": int,              // Frames to skip in the ingest
    "ts": timestamp                 // Video analysis start time
}
```

## Metrics
```json
{
    "video_id": uuid,               // Inference model name (unique)
    "metric_name": text,            // Frame height
    "metric_value": decimal         // Frame width
}
```
