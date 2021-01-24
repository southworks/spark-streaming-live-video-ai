import axios from "axios";
import io from "socket.io-client";
import React, { useRef, useEffect, useState } from "react";
import {
  Button,
  Grid,
  Checkbox,
  FormControlLabel,
  FormHelperText,
  FormGroup,
  FormLabel,
  FormControl,
  Tooltip,
  TextField,
  Zoom,
} from "@material-ui/core";
import { Videocam } from "@material-ui/icons";
import StopIcon from "@material-ui/icons/Stop";
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles((theme) => ({
  formControl: {
    margin: theme.spacing(1),
  },
  textField: {
    width: 450,
    padding: "0 48px 0 0",
  },
  formLabel: {
    paddingBottom: "20px",
  },
}));

export const WebcamCapture = ({ handleVideoId, handleVideoStatusUrl, videoStatus }) => {
  const classes = useStyles();

  var socket = useRef();
  var mediaRecorder = useRef();
  const videoRef = useRef(null);

  const analyzing = videoStatus === "Pending" || videoStatus === "Processing";

  const [streaming, setStreaming] = useState(false);

  const [values, setValues] = useState({
    models: ["objects_detection", "emotions_detection", "color_detection"],
    videoUrl: "",
    videoName: "",
    frameStep: 1,
  });

  const [errors, setErrors] = useState({});

  const handleChange = (event) => {
    const { name, value: newValue, type } = event.target;
    const value = type === "number" ? +newValue : newValue;

    setValues({
      ...values,
      [name]: value,
    });
  };

  const handleCheckboxChange = (event) => {
    const { name } = event.target;

    let newValue = {};

    if (!values.models.includes(name)) {
      newValue = {
        ...values,
        models: [...values.models, name],
      };
      setValues(newValue);
    } else {
      newValue = {
        ...values,
        models: values.models.filter((el) => el !== name),
      };
      setValues(newValue);
    }

    const error = newValue.models.length === 0;
    console.log(newValue);
    console.log(values);

    setErrors({
      ...errors,
      models: error,
    });
  };

  const handleBlur = (event) => {
    const { name, value, type } = event.target;

    let error = false;

    if (type === "number") {
      error = value <= 0;
    } else {
      error = !value;
    }

    setErrors({
      ...errors,
      [name]: error,
    });
  };

  useEffect(() => {
    socket.current = io(window.location.href);
    const configureWebcam = () => {
      navigator.getUserMedia =
        navigator.mediaDevices.getUserMedia ||
        navigator.mediaDevices.mozGetUserMedia ||
        navigator.mediaDevices.msGetUserMedia ||
        navigator.mediaDevices.webkitGetUserMedia;
      if (!navigator.getUserMedia) {
        console.log("No getUserMedia() available.");
      }
      if (!MediaRecorder) {
        console.log("No MediaRecorder available.");
      }

      var constraints = {
        audio: false,
        video: {
          width: { min: 100, ideal: 200, max: 1920 },
          height: { min: 100, ideal: 200, max: 1080 },
          frameRate: { ideal: 15 },
        },
      };

      navigator.mediaDevices
        .getUserMedia(constraints)
        .then(function (stream) {
          var output_video = videoRef.current;
          if ("srcObject" in output_video) {
            output_video.muted = true;
            output_video.srcObject = stream;
          } else {
            output_video.src = window.URL.createObjectURL(stream);
          }

          mediaRecorder.current = new MediaRecorder(stream);

          mediaRecorder.current.onstop = function (e) {
            console.log("stopped!");
            console.log(e);
          };

          mediaRecorder.current.onpause = function (e) {
            console.log("media recorder paused!!");
            console.log(e);
          };

          mediaRecorder.current.onerror = function (event) {
            let error = event.error;
            console.log("error", error.name);
          };

          mediaRecorder.current.ondataavailable = function (e) {
            socket.current.emit("binarystream", e.data);
          };
        })
        .catch(function (err) {
          console.log("The following error occured: " + err);
        });
    };
    configureWebcam();
    return () => socket.current.disconnect();
  }, []);

  async function startStreaming() {
    const errorVideoName = !values.videoName;
    const errorFrameStep = values.frameStep <= 0;
    const errorModels = values.models.length === 0;

    setErrors({
      videoName: errorVideoName,
      frameStep: errorFrameStep,
      models: errorModels,
    });

    if (errorVideoName || errorFrameStep || errorModels){
      return;
    }

    console.log("Starting Streaming");
    try {
      const json = JSON.stringify({
        modelsToRun: values.models,
        videoName: values.videoName,
        frameStep: values.frameStep,
      });
      console.log(json);
      const result = await axios.post(
        process.env.REACT_APP_API_URL + "/analysis/rtmp-endpoint",
        json,
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      const rtmpEndpoint = result.data["video_url"];
      var arr = rtmpEndpoint.split("/");
      var _id = arr[arr.length - 1];
      handleVideoId(_id);
      handleVideoStatusUrl(process.env.REACT_APP_API_URL + "/analysis/" + _id);
      socket.current.emit("start", rtmpEndpoint);
      mediaRecorder.current.start(250);
      setStreaming(true);
    } catch (error) {
      if (error.includes("503")) {
        alert(
          "Video analysis pipeline busy. Please try again in a few minutes"
        );
      } else {
        alert(error);
      }
    }
  }

  async function stopStreaming(models) {
    if (MediaRecorder.state !== "inactive") {
      mediaRecorder.current.stop();
      socket.current.emit("stop");
      setStreaming(false);
    }
  }

  return (
    <Grid container spacing={2}>
      <Grid item xs={12}>
        <video autoPlay={true} ref={videoRef}></video>
      </Grid>
      <Grid item xs={12}>
        <Tooltip
          title="Name of the video for easier identification"
          classes={{ tooltip: classes.customTooltip }}
          TransitionComponent={Zoom}
          arrow
        >
          <TextField
            id="videoName"
            label="Video name"
            name="videoName"
            className={classes.textField}
            value={values.videoName}
            error={errors.videoName}
            onChange={handleChange}
            onBlur={handleBlur}
            helperText={errors.videoName ? "Video name is required" : " "}
            disabled={analyzing}
          />
        </Tooltip>
        <Tooltip
          title="Number of frames to be skipped while analyzing"
          classes={{ tooltip: classes.customTooltip }}
          TransitionComponent={Zoom}
          arrow
        >
          <TextField
            id="frameStep"
            label="Frame step"
            name="frameStep"
            className={classes.textField}
            type="number"
            value={values.frameStep}
            error={errors.frameStep}
            onChange={handleChange}
            onBlur={handleBlur}
            helperText={
              errors.frameStep ? "Frame step must be greater than 0" : " "
            }
            disabled={analyzing}
          />
        </Tooltip>
      </Grid>
      <Grid item xs={12}>
        <FormControl
          component="fieldset"
          className={classes.formControl}
          error={errors.models}
          disabled={analyzing}
        >
          <FormLabel component="legend" className={classes.formLabel}>
            {" "}
            Models{" "}
          </FormLabel>
          <FormHelperText>
            {errors.models ? "At least one model must be selected" : " "}
          </FormHelperText>
          <FormGroup aria-label="position" row>
            <FormControlLabel
              control={
                <Checkbox
                  checked={values.models.includes("objects_detection")}
                  onChange={handleCheckboxChange}
                  color="primary"
                  name="objects_detection"
                />
              }
              label="Object Detection"
              labelPlacement="bottom"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={values.models.includes("emotions_detection")}
                  onChange={handleCheckboxChange}
                  color="primary"
                  name="emotions_detection"
                />
              }
              label="Emotion Detection"
              labelPlacement="bottom"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={values.models.includes("color_detection")}
                  onChange={handleCheckboxChange}
                  color="primary"
                  name="color_detection"
                />
              }
              label="Color Palette Extraction"
              labelPlacement="bottom"
            />
          </FormGroup>
        </FormControl>
      </Grid>
      <Grid item xs={6}>
        <Button
          variant="contained"
          color="secondary"
          disabled={streaming || analyzing || Object.values(errors).some((el) => el === true)}
          onClick={startStreaming}
          startIcon={<Videocam />}
        >
          Start Capture
        </Button>
      </Grid>
      <Grid item xs={6}>
        <Button
          variant="contained"
          color="secondary"
          disabled={!streaming}
          onClick={stopStreaming}
          startIcon={<StopIcon />}
        >
          Stop Capture
        </Button>
      </Grid>
    </Grid>
  );
};

export default WebcamCapture;
