import axios from "axios";
import React, { useEffect } from "react";
import { makeStyles } from "@material-ui/core/styles";
import { Grid, Paper, IconButton, FormLabel } from "@material-ui/core";
import ArrowForwardIcon from "@material-ui/icons/ArrowForward";
import ArrowBackIcon from "@material-ui/icons/ArrowBack";
import FrameMetricsTable from "./FrameMetricsTable";

const useStyles = makeStyles(() => ({
  root: {
    flexGrow: 1,
    width: "100%",
  },
  formLabel: {
    paddingBottom: "20px",
  },
  img: {
    paddingTop: "20px",
    width: "50%",
  },
}));

export const HistoryItem = (props) => {
  const classes = useStyles();
  const frameStep = props.frameStep;

  function handleProps(m) {
    let metrics = [];
    for (let i = 0; i < m.length; i++) {
      metrics = [
        ...metrics,
        createData(m[i][0], +m[i][1].toFixed(4), +m[i][2].toFixed(2)),
      ];
    }
    return metrics;
  }

  useEffect(() => {
    setState({
      frameUrl: props.frame.startingFrameUrl,
      frameNumber: props.frame.startingFrame,
      metrics: handleProps(props.metrics),
    });
  }, [props.videoId]);

  function createData(model, inferenceTime, timestamp) {
    return { model, inferenceTime, timestamp };
  }

  const getFrameUrl = (frameNumber) => {
    return (
      process.env.REACT_APP_API_URL +
      "/analysis/" +
      props.videoId +
      "/frame/" +
      frameNumber
    );
  };

  const [state, setState] = React.useState({
    frameUrl: "",
    frameNumber: 5,
    metrics: [],
  });

  async function updateFrameMetrics(id, frame) {
    let metrics = [];
    await axios
      .get(
        process.env.REACT_APP_API_URL +
          "/analysis/" +
          id +
          "/frame/" +
          frame +
          "/results"
      )
      .then((res) => {
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
      });

    return metrics;
  }

  const handlePreviousClick = async () => {
    let rows =
      state.frameNumber - frameStep >= frameStep
        ? await updateFrameMetrics(props.videoId, state.frameNumber - frameStep)
        : state.metrics;
    setState((prev) => ({
      frameNumber:
        prev.frameNumber - frameStep >= frameStep
          ? prev.frameNumber - frameStep
          : frameStep,
      frameUrl:
        prev.frameNumber - frameStep >= frameStep
          ? getFrameUrl(prev.frameNumber - frameStep)
          : getFrameUrl(prev.frameNumber),
      metrics: rows,
    }));
  };

  const handleNextClick = async () => {
    let rows =
      state.frameNumber + frameStep <= props.frame.greatestFrame
        ? await updateFrameMetrics(props.videoId, state.frameNumber + frameStep)
        : state.metrics;
    setState((prev) => ({
      frameNumber:
        prev.frameNumber + frameStep > props.frame.greatestFrame
          ? prev.frameNumber
          : prev.frameNumber + frameStep,
      frameUrl:
        prev.frameNumber + frameStep > props.frame.greatestFrame
          ? getFrameUrl(prev.frameNumber)
          : getFrameUrl(prev.frameNumber + frameStep),
      metrics: rows,
    }));
  };

  return (
    <Paper square className={classes.root}>
      <Grid container spacing={2} md={12}>
        <Grid item xs={6} md={6}>
          <div style={{ height: "100%" }}>
            <img
              src={state.frameUrl}
              className={classes.img}
              alt="Analyzed frame"
            />
            <br />
            <IconButton onClick={handlePreviousClick}>
              <ArrowBackIcon />
            </IconButton>
            <FormLabel className={classes.formLabel}>
              {state.frameNumber}
            </FormLabel>
            <IconButton onClick={handleNextClick}>
              <ArrowForwardIcon />
            </IconButton>
          </div>
        </Grid>
        <Grid item xs={6}>
          <FrameMetricsTable metrics={state.metrics}></FrameMetricsTable>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default HistoryItem;
