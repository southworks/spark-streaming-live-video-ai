import axios from "axios";
import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import {CircularProgress, Grid, Paper, IconButton, FormLabel, Typography} from '@material-ui/core';
import ArrowForwardIcon from '@material-ui/icons/ArrowForward';
import ArrowBackIcon from '@material-ui/icons/ArrowBack';
import RefreshIcon from '@material-ui/icons/Refresh';

const useStyles = makeStyles(() => ({
    root: {
        flexGrow: 1,
        width: 900
    },
    formLabel: {
        paddingBottom: "20px"
    },
    imgContainer: {
        maxWidth: "100%",
    },
    img: {
        paddingTop: "20px",
        maxWidth: "40%"
    }
}));

export const ResultImage = (props) => {
    const classes = useStyles();
    const frameStep = 5;
    const defaultImage = "waiting.png";

    React.useEffect(() => {
        const interval = setInterval(() => {
            axios.get(props.status).then(res => {
                let responseStatus = res.data.status;
                setVideoStatus({status: responseStatus ? responseStatus : "Idle"});
            });
        }, 1000);
        return () => clearInterval(interval);
    }, [props.status]);

    const getFrameUrl = (frameNumber) => {
        return process.env.REACT_APP_API_URL + "/analysis/" + props.videoId + "/frame/" + frameNumber
    }

    const [state, setState] = React.useState({
        frameUrl: getFrameUrl(frameStep),
        frameNumber: frameStep,
        frameExists: false
    });

    const [videostatus, setVideoStatus] = React.useState({
        status: "Idle"
    });

    const handlePreviousClick = () => {
        setState(prev => ({
            frameNumber: prev.frameNumber - frameStep,
            frameUrl: getFrameUrl(prev.frameNumber - frameStep),
            frameExists: true
        }));
    };

    const handleNextClick = () => {
        setState(prev => ({
            frameNumber: prev.frameNumber + frameStep,
            frameUrl: getFrameUrl(prev.frameNumber + frameStep),
            frameExists: true
        }));
    };

    const handleNoPictureFound = () => {
        setState(prev => ({
            frameNumber: prev.frameNumber,
            frameUrl: defaultImage,
            frameExists: false
        }));
    }

    const handleRefreshClick = () => {
        setState(prev => ({
            frameNumber: prev.frameNumber,
            frameUrl: getFrameUrl(prev.frameNumber),
            frameExists: true
        }));
    }


    return (
        <Paper square className={classes.root}>
            <Grid container spacing={2}>
                <Grid item xs={12}>
                    <Typography variant="h6"> Video Status: {videostatus.status} </Typography>
                </Grid>
                <Grid item xs={12}>
                    {videostatus.status === "Idle" ?
                        <CircularProgress/> :
                        <Grid className={classes.imgContainer} display="flex" container direction="row" justify="center" alignItems="center">
                            <img src={state.frameUrl} className={classes.img} onError={handleNoPictureFound} alt="Analyzed frame"/>
                        </Grid>
                    }
                    <br/>
                    <IconButton onClick={handlePreviousClick} disabled={state.frameNumber <= frameStep}>
                        <ArrowBackIcon/>
                    </IconButton>
                    <FormLabel className={classes.formLabel}>{state.frameNumber}</FormLabel>
                    <IconButton onClick={handleRefreshClick} disabled={state.frameExists}>
                        <RefreshIcon/>
                    </IconButton>
                    <IconButton onClick={handleNextClick} disabled={!state.frameExists}>
                        <ArrowForwardIcon/>
                    </IconButton>
                </Grid>
            </Grid>
        </Paper>
    )

}

export default ResultImage;