# Kafka message models

## Video frames

```json
{
	"video_id": UUID,           // Generated ID for the video
	"frame_number": Integer,    // Frame number
	"timestamp": Double,        // Timestamp in milliseconds of the current frame
	"buffer": String,           // Base64-encoded frame
	"models_to_run": Array      // Model names to run (color_detection, emotions_detection, objects_detection)
}
```

## Videos

```json
{
    "video_id": UUID,           // Generated ID for the video
    "video_url": String,        // URL for the video to analyse
    "models_to_run": Array,     // Model names to run (color_detection, emotions_detection, objects_detection)
    "frame_step": Integer       // Frames to skip in the ingest
  
}
```