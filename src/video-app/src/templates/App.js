import "./App.css";
import React, { useState } from "react";
import IconLabelTabs from "../components/TabComponent";
import SelfUpdatingAnalyzedFrame from "../components/SelfUpdatingAnalyzedFrame";

function App() {
  const [videoId, setVideoId] = useState("");
  const [videoStatusUrl, setVideoStatusUrl] = useState("");
  const [videoStatus, setVideoStatus] = useState("Idle");
  const [activeTab, setActiveTab] = React.useState("0");

  const handleVideoId = (videoId) => {
    setVideoId(videoId);
  };

  const handleVideoStatusUrl = (videoStatusUrl) => {
    setVideoStatusUrl(videoStatusUrl);
  };

  const handleVideoStatus = (videoStatus) => {
    setVideoStatus(videoStatus);
  };

  const handleTab = (activeTab) => {
    setActiveTab(activeTab);
  };

  return (
    <div className="App">
      <header className="App-header">
        <IconLabelTabs
          handleVideoId={handleVideoId}
          handleVideoStatusUrl={handleVideoStatusUrl}
          handleTab={handleTab}
          videoStatus={videoStatus}
        />
        {activeTab !== "2" && (
          <SelfUpdatingAnalyzedFrame
            videoId={videoId}
            videoStatusUrl={videoStatusUrl}
            videoStatus={videoStatus}
            handleVideoStatus={handleVideoStatus}
          />
        )}
      </header>
    </div>
  );
}

export default App;
