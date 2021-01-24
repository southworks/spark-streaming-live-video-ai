import React from "react";
import Webcam from "react-webcam";
import { Button, Grid } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { GetApp, Stop, Videocam } from '@material-ui/icons';

const useStyles = makeStyles((theme) => ({
    button: {
        margin: theme.spacing(1),
    },
    cam: {
        paddingTop: "20px"
    }
}));

const WebcamStreamCapture = () => {
    const classes = useStyles();
    const webcamRef = React.useRef(null);
    const mediaRecorderRef = React.useRef(null);
    const [capturing, setCapturing] = React.useState(false);
    const [recordedChunks, setRecordedChunks] = React.useState([]);

    const handleStartCaptureClick = React.useCallback(() => {
        setCapturing(true);
        mediaRecorderRef.current = new MediaRecorder(webcamRef.current.stream, {
            mimeType: "video/webm"
        });
        mediaRecorderRef.current.addEventListener(
            "dataavailable",
            handleDataAvailable
        );
        mediaRecorderRef.current.start();
    }, [webcamRef, setCapturing, mediaRecorderRef]);

    const handleDataAvailable = React.useCallback(
        ({data}) => {
            if (data.size > 0) {
                setRecordedChunks((prev) => prev.concat(data));
            }
        },
        [setRecordedChunks]
    );

    const handleStopCaptureClick = React.useCallback(() => {
        mediaRecorderRef.current.stop();
        setCapturing(false);
    }, [mediaRecorderRef, webcamRef, setCapturing]);

    const handleDownload = React.useCallback(() => {
        if (recordedChunks.length) {
            const blob = new Blob(recordedChunks, {
                type: "video/webm"
            });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            document.body.appendChild(a);
            a.style = "display: none";
            a.href = url;
            a.download = "react-webcam-stream-capture.webm";
            a.click();
            window.URL.revokeObjectURL(url);
            setRecordedChunks([]);
        }
    }, [recordedChunks]);

    return (
        <Grid container spacing={2}>
            <Grid item xs={12}>
                <Webcam audio={false} className={classes.cam} ref={webcamRef} />
            </Grid>
            <Grid item xs={12}>
                {capturing ? (
                    <Button
                    variant="contained"
                    color="secondary"
                    onClick={handleStopCaptureClick}
                    className={classes.button}
                    startIcon={<Stop />}
                    >
                    Stop Capture
                    </Button>
                ) : (
                    <Button
                    variant="contained"
                    color="secondary"
                    onClick={handleStartCaptureClick}
                    className={classes.button}
                    startIcon={<Videocam />}
                    >
                    Start Capture
                    </Button>
                )}
                {recordedChunks.length > 0 && (
                    <Button
                    variant="contained"
                    color="primary"
                    onClick={handleDownload}
                    className={classes.button}
                    startIcon={<GetApp />}
                    >
                    Download
                    </Button>
                )}
            </Grid>
        </Grid>
    );
};

export default WebcamStreamCapture
