import axios from "axios";
import React, { useState } from "react";
import {
  Button,
  Checkbox,
  Grid,
  FormControl,
  FormControlLabel,
  FormHelperText,
  FormGroup,
  FormLabel,
  TextField,
  Tooltip,
  Typography,
  Zoom,
} from "@material-ui/core";
import { PlayArrow } from "@material-ui/icons";
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles((theme) => ({
  formControl: {
    margin: theme.spacing(1),
  },
  textField: {
    width: 450,
    margin: "0 48px 0 0",
  },
  formLabel: {
    paddingBottom: "20px",
  },
  customTooltip: {
    maxWidth: 450,
    fontSize: 18,
  },
}));

export const SubmitComponent = ({ handleVideoId, handleVideoStatusUrl, videoStatus }) => {
  const classes = useStyles();

  const [values, setValues] = useState({
    models: ["objects_detection", "emotions_detection", "color_detection"],
    videoUrl: "",
    videoName: "",
    frameStep: 1,
  });

  const [errors, setErrors] = useState({});

  const analyzing = videoStatus === "Pending" || videoStatus === "Processing";

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

  const startAnalysis = () => {
    const errorVideoName = !values.videoName;
    const errorVideoUrl = !values.videoUrl;
    const errorFrameStep = values.frameStep <= 0;
    const errorModels = values.models.length === 0;

    setErrors({
      videoName: errorVideoName,
      videoUrl: errorVideoUrl,
      frameStep: errorFrameStep,
      models: errorModels,
    });

    if (errorVideoName || errorVideoUrl || errorFrameStep || errorModels) {
      return;
    }

    const json = JSON.stringify({
      videoURL: values.videoUrl,
      modelsToRun: values.models,
      videoName: values.videoName,
      frameStep: values.frameStep,
    });
    axios
      .post(process.env.REACT_APP_API_URL + "/analysis/start", json, {
        headers: {
          "Content-Type": "application/json",
        },
      })
      .then((response) => {
        console.log("In axios response: " + response.data.video_id + " " + response.data.status_url);
        handleVideoId(response.data.video_id);
        handleVideoStatusUrl(response.data.status_url);
      });
  };

  return (
    <Grid container spacing={4}>
      <Grid item xs={12}></Grid>
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
        <Tooltip
          title="URL of the video to be analyzed"
          classes={{ tooltip: classes.customTooltip }}
          TransitionComponent={Zoom}
          arrow
        >
          <TextField
            id="url"
            label="URL"
            name="videoUrl"
            className={classes.textField}
            placeholder="HTTP:// or RTMP://"
            value={values.videoUrl}
            error={errors.videoUrl}
            onChange={handleChange}
            onBlur={handleBlur}
            helperText={errors.videoUrl ? "Video URL is required" : " "}
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
      <Grid item xs={12}>
        <Button
          variant="contained"
          color="secondary"
          disabled={
            analyzing || Object.values(errors).some((el) => el === true)
          }
          onClick={startAnalysis}
          startIcon={<PlayArrow />}
        >
          Start Analysis
        </Button>
      </Grid>
      <Grid item xs={12}></Grid>
      <Grid item xs>
        <Typography variant="h4"> Instructions </Typography>
        <Typography variant="body1" gutterBottom>
          1. Type or paste a valid URL. HTTP and RTMP protocols supported.
        </Typography>
        <Typography variant="body1" display="block" gutterBottom>
          2. Select at least one detection model to perform inferences.
        </Typography>
        <Typography variant="body1" display="block" gutterBottom>
          3. Click the "Send" icon to push the video to the pipeline.
        </Typography>
      </Grid>
    </Grid>
  );
};

export default SubmitComponent;
