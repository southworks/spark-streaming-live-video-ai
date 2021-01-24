import React, { useEffect, useState } from "react";
import axios from "axios";
import { DataGrid } from '@material-ui/data-grid';
import { Grid } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import ResultItem from './HistoryItem'

const columns = [
  { field: 'id', headerName: 'Video ID', hide: true },
  { field: 'video_name', headerName: 'Video name', width: 425 },
  { field: 'video_url', headerName: 'Video URL', width: 425 }
];

const useStyles = makeStyles(() => ({
  grid: {
    height: 400
  },
}));  

export const HistoryComponent = () => {
  const [state, setState] = React.useState({ videos: [] });
  const classes = useStyles();

  const [row, setRow] = React.useState({
    selected: false,
    videoId: "",
    metrics: [],
    frameStep: 1
});

  const [frame, setFrame] = React.useState({
    startingFrame: 1,
    startingFrameUrl: "",
    greatestFrame: 1,
  })

  useEffect(async () => {
    axios.get(process.env.REACT_APP_API_URL + "/analysis/videos")
      .then(res => {
        const videos = res.data.map(({ video_id: id, video_url, video_name, frame_step}) => ({id, video_url, video_name, frame_step}));
        setState({ videos });
      })
  }, []);

  const handleRowSelection = async (e) => {
    let metricsAux = []
    let frameCap = 0;

    await axios.get(process.env.REACT_APP_API_URL + "/analysis/" + e.data.id + "/frame/" + e.data.frame_step +"/results").then(res => {
      for (let i = 0; i < res.data.length; i++) {
        metricsAux = [...metricsAux, [res.data[i].inference_model, res.data[i].inference_time, res.data[i].video_timestamp]]
      }
    });

    await axios.get(process.env.REACT_APP_API_URL + "/analysis/" + e.data.id).then(res => {
      frameCap = res.data.greatest_frame_analyzed
    })

    setFrame({
      startingFrame: e.data.frame_step,
      startingFrameUrl: process.env.REACT_APP_API_URL + "/analysis/" + e.data.id + "/frame/" + e.data.frame_step,
      greatestFrame: frameCap
    });

    setRow({
      selected: true,
      videoId: e.data.id,
      metrics: metricsAux,
      frameStep: e.data.frame_step
    });
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} className={classes.grid}>
        <DataGrid rows={state.videos} columns={columns} pageSize={5} onRowSelected={handleRowSelection} />
      </Grid>
      <Grid item xs={12}>
        { row.selected &&
        <ResultItem videoId={row.videoId} metrics={row.metrics} frame={frame} frameStep={row.frameStep}/> }
      </Grid>
    </Grid>
  );
}

export default HistoryComponent;
