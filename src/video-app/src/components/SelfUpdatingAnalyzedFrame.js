import axios from "axios";
import React, { useState, useEffect } from "react";
import { makeStyles } from "@material-ui/core/styles";
import {
  CircularProgress,
  Grid,
  Paper,
  FormLabel,
  Typography,
} from "@material-ui/core";
import FrameMetricsTable from "./FrameMetricsTable";

const useStyles = makeStyles(() => ({
  root: {
    flexGrow: 1,
    width: 900,
  },
  formLabel: {
    paddingBottom: "20px",
  },
  imgContainer: {
    maxWidth: "100%",
  },
  img: {
    paddingTop: "20px",
    maxWidth: "40%",
  },
}));

export const SelfUpdatingAnalyzedFrame = ({
  videoId,
  videoStatusUrl,
  videoStatus,
  handleVideoStatus,
}) => {
  const classes = useStyles();
  const defaultImage = "waiting.png";

  useEffect(() => {
    const interval = setInterval(() => {
      axios.get(videoStatusUrl).then((res) => {
        let responseStatus = res.data.status;
        handleVideoStatus(responseStatus ? responseStatus : "Idle");
        let greatest_frame_analyzed = res.data.greatest_frame_analyzed;
        if (greatest_frame_analyzed > state.frameNumber) {
          handleNewFrameFound(greatest_frame_analyzed);
        }
        if (responseStatus === "Completed") {
          resetFrameNumber();
        }
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [videoStatusUrl]);

  const getFrameUrl = (frameNumber) => {
    return (
      process.env.REACT_APP_API_URL +
      "/analysis/" +
      videoId +
      "/frame/" +
      frameNumber
    );
  };

  const [state, setState] = useState({
    frameUrl: getFrameUrl(0),
    frameNumber: 0,
  });

  const [metrics, setMetrics] = useState([]);

  const handleNoPictureFound = () => {
    setState((prev) => ({
      frameNumber: prev.frameNumber,
      frameUrl: defaultImage,
    }));
  };

  const handleNewFrameFound = (newFrameNumber) => {
    setState((prev) => ({
      frameNumber: newFrameNumber,
      frameUrl: getFrameUrl(newFrameNumber),
    }));

    axios
      .get(
        process.env.REACT_APP_API_URL +
          "/analysis/" +
          videoId +
          "/frame/" +
          newFrameNumber +
          "/results"
      )
      .then((res) => {
        let metrics = [];
        for (let i = 0; i < res.data.length; i++) {
          metrics = [
            ...metrics,
            createData(
              res.data[i].inference_model,
              +res.data[i].inference_time.toFixed(4),
              +res.data[i].video_timestamp.toFixed(2)
            ),
          ];
        }
        setMetrics(metrics);
      });
  };

  function createData(model, inferenceTime, timestamp) {
    return { model, inferenceTime, timestamp };
  }

  const resetFrameNumber = () => {
    setState((prev) => ({
      frameNumber: 0,
      frameUrl: prev.frameUrl,
    }));
  };

  return (
    <Paper square className={classes.root}>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Typography variant="h6"> Video Status: {videoStatus} </Typography>
          {videoStatus !== "Idle" &&
            videoStatus !== "Completed" &&
            state.frameNumber === 0 && <CircularProgress />}
        </Grid>
        {state.frameNumber !== 0 && (
          <Grid item xs={6} md={6}>
            <Grid
              className={classes.imgContainer}
              display="flex"
              container
              direction="row"
              justify="center"
              alignItems="center"
            >
              <img
                src={state.frameUrl}
                className={classes.img}
                onError={handleNoPictureFound}
                alt="Analyzed frame"
              />
            </Grid>

            <br />
            <FormLabel>Current Frame:&nbsp;</FormLabel>
            <FormLabel className={classes.formLabel}>
              {state.frameNumber}
            </FormLabel>
          </Grid>
        )}
        {state.frameNumber !== 0 && (
          <Grid item xs={6}>
            <FrameMetricsTable metrics={metrics}></FrameMetricsTable>
          </Grid>
        )}
      </Grid>
    </Paper>
  );
};

export default SelfUpdatingAnalyzedFrame;
