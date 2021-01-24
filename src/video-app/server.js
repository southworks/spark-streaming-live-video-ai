var express = require("express");
var app = express();

var spawn = require("child_process").spawn;

app.use(express.static("build"));
const server = require("http").createServer(app);

var io = require("socket.io")(server);
spawn("ffmpeg", ["-h"]).on("error", function (m) {
  console.error(
    "FFMpeg not found in system cli; please install ffmpeg properly or make a softlink to ./!"
  );
  process.exit(-1);
});

io.on("connection", function (socket) {
  console.log("Frontend connected");

  var ffmpeg_process,
    feedStream = false;

  socket.on("start", function (rtmpEndpoint) {
    if (ffmpeg_process || feedStream) {
      console.log("stream already started.");
      return;
    }
    if (!rtmpEndpoint) {
      console.log("no destination given.");
      return;
    }

    var ops = [
      "-i",
      "-",
      "-c:v",
      "libx264",
      "-preset",
      "ultrafast",
      "-tune",
      "zerolatency",
      "-max_muxing_queue_size",
      "1000",
      "-bufsize",
      "5000",
      "-r",
      "15",
      "-g",
      "30",
      "-keyint_min",
      "30",
      "-x264opts",
      "keyint=30",
      "-crf",
      "25",
      "-pix_fmt",
      "yuv420p",
      "-profile:v",
      "baseline",
      "-level",
      "3",
      "-c:a",
      "aac",
      "-b:a",
      "22k",
      "-ar",
      22050,
      "-f",
      "flv",
      rtmpEndpoint,
    ];

    ffmpeg_process = spawn("ffmpeg", ops);

    feedStream = function (data) {
      ffmpeg_process.stdin.write(data);
    };

    ffmpeg_process.stderr.on("data", function (d) {
      console.log("ffmpeg_stdout" + " " + d);
    });
    ffmpeg_process.on("error", function (e) {
      console.log("child process error" + e);
      console.log("ffmpeg error!" + e);
      feedStream = false;
    });
    ffmpeg_process.on("exit", function (e) {
      console.log("ffmpeg exit!" + e);
    });
  });

  socket.on("binarystream", function (m) {
    if (feedStream) {
      feedStream(m);
    }    
  });

  function stopFfmpeg(){
    feedStream = false;
    if (ffmpeg_process) {
      try {
        ffmpeg_process.stdin.end();
        ffmpeg_process.kill("SIGINT");
        ffmpeg_process = false;
        console.log("ffmpeg process ended!");
      } catch (e) {
        console.warn("killing ffmpeg process attempt failed...");
      }
    }
  }
  
  socket.on("stop", function() {
    console.log("streamming stopped");
    stopFfmpeg();
  });

  socket.on("disconnect", function () {
    console.log("socket disconnected");
    stopFfmpeg();
  });

  socket.on("error", function (e) {
    console.log("socket.io error:" + e);
  });
});

io.on("error", function (e) {
  console.log("socket.io error:" + e);
});

server.listen(8080, function () {
  console.log("https and websocket listening on *:8080");
});

process.on("uncaughtException", function (err) {
  // handle the error safely
  console.log(err);
  // Note: after client disconnect, the subprocess will cause an Error EPIPE, which can only be caught this way.
});
