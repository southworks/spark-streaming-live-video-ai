import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import {
  Paper,
  Table,
  TableBody,
  TableContainer,
  TableCell,
  TableHead,
  TableRow,
  Tooltip,
  Zoom,
} from "@material-ui/core";

const useStyles = makeStyles(() => ({
  customTooltip: {
    maxWidth: 250,
    fontSize: 12,
  },
}));

const FrameMetricsTable = ({ metrics }) => {
  const classes = useStyles();

  return (
    <TableContainer component={Paper}>
      <Table size="medium" aria-label="a dense table">
        <TableHead>
          <TableRow>
            <Tooltip
              title="Name of the model used for prediction"
              classes={{ tooltip: classes.customTooltip }}
              TransitionComponent={Zoom}
              arrow
            >
              <TableCell> Inference Model </TableCell>
            </Tooltip>
            <Tooltip
              title="Time consumed before returning the prediction, in seconds"
              classes={{ tooltip: classes.customTooltip }}
              TransitionComponent={Zoom}
              arrow
            >
              <TableCell> Inference Time (seconds) </TableCell>
            </Tooltip>
            <Tooltip
              title="Time mark where current frame appears on the original video, in seconds"
              classes={{ tooltip: classes.customTooltip }}
              TransitionComponent={Zoom}
              arrow
            >
              <TableCell> Video Offset (seconds) </TableCell>
            </Tooltip>
          </TableRow>
        </TableHead>
        <TableBody>
          {metrics.map((it) => (
            <TableRow>
              <TableCell> {it.model} </TableCell>
              <TableCell> {it.inferenceTime} </TableCell>
              <TableCell> {it.timestamp} </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default FrameMetricsTable;
