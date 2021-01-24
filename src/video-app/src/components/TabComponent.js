import React from "react";
import { Paper, Tab, Tabs } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";
import { TabContext, TabPanel } from "@material-ui/lab";
import { Camera, Public } from "@material-ui/icons";
import HistoryIcon from "@material-ui/icons/History";
import SubmitComponent from "./SubmitComponent";
import WebcamCapture from "./WebcamCapture";
import HistoryComponent from "./HistoryComponent";

const useStyles = makeStyles({
  root: {
    flexGrow: 1,
    width: 900,
  },
});

export const IconLabelTabs = ({
  handleVideoId,
  handleVideoStatusUrl,
  handleTab,
  videoStatus,
}) => {
  const classes = useStyles();
  const [value, setValue] = React.useState("0");

  const handleChange = (e, newValue) => {
    setValue(newValue);
    handleTab(newValue);
  };

  return (
    <Paper square className={classes.root}>
      <TabContext value={value}>
        <Tabs
          value={value}
          onChange={handleChange}
          variant="fullWidth"
          indicatorColor="secondary"
          textColor="secondary"
          aria-label="icon label tabs example"
        >
          <Tab icon={<Public />} label="From URL" value="0" />
          <Tab icon={<Camera />} label="From Webcam" value="1" />
          <Tab icon={<HistoryIcon />} label="History" value="2" />
        </Tabs>
        <TabPanel value="0">
          <SubmitComponent
            handleVideoId={handleVideoId}
            handleVideoStatusUrl={handleVideoStatusUrl}
            videoStatus={videoStatus}
          />
        </TabPanel>
        <TabPanel value="1">
          <WebcamCapture
            handleVideoId={handleVideoId}
            handleVideoStatusUrl={handleVideoStatusUrl}
            videoStatus={videoStatus}
          />
        </TabPanel>
        <TabPanel value="2">
          <HistoryComponent />
        </TabPanel>
      </TabContext>
    </Paper>
  );
};

export default IconLabelTabs;
