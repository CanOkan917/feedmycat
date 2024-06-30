require('dotenv').config();
require('log-timestamp');
const express = require('express');
const app = express();
const http = require('http');
const server = http.createServer(app);
const { Server } = require('socket.io');
const io = new Server(server);
const path = require('path');
const moment = require('moment');

const PORT = process.env.PORT || 3001;

// Saniye cinsinden
let interval = 21600;
let lastfeed = 0;
let lastFeed_parse = "";

var fs = require('fs');
var util = require('util');
var log_file = fs.createWriteStream(__dirname + `/logs/debug-${moment().format("DD-MM-YYYY-HH-mm-ss")}.log`, { flags: 'w' });
var log_stdout = process.stdout;

function secondsToTime(secs) {
  secs = Math.round(secs);
  var hours = Math.floor(secs / (60 * 60));

  var divisor_for_minutes = secs % (60 * 60);
  var minutes = Math.floor(divisor_for_minutes / 60);

  var divisor_for_seconds = divisor_for_minutes % 60;
  var seconds = Math.ceil(divisor_for_seconds);

  var obj = {
    "h": hours,
    "m": minutes,
    "s": seconds
  };
  return obj;
}

console.log = function (d) {
  log_file.write(`[${moment().format("DD-MM-YYYY-HH-MM-SS")}]: ` + util.format(d) + '\n');
  log_stdout.write(util.format(d) + '\n');
};

app.set('views', path.join(__dirname, 'public/views'));
app.set('view engine', 'ejs');
app.use('/assets', express.static(path.join(__dirname, 'public/assets')));

app.get('/', (req, res) => {
  res.render('index', {
    saat: secondsToTime(interval).h,
    dakika: secondsToTime(interval).m,
    saniye: secondsToTime(interval).s,
    // lastfeed: lastFeed_parse
    lastfeed: new Date(lastfeed * 1000).toLocaleString()
  });
});

io.on('connect', (socket) => {
  console.log(`[CLIENT] [${socket.id}] connected`);

  socket.on('feeddata', (data) => {
    console.log(`[CLIENT] feed data recieved: ${JSON.stringify(data)}`);
  });

  socket.on('initialData', (data) => {
    console.log(`[CLIENT] initial data recieved: ${JSON.stringify(data)}`);
    lastfeed = data.lastfeed;
    lastFeed_parse = data.parsed_lastfeed;
    socket.emit('updateData', { interval });
  });

  socket.on('save-interval', (data) => {
    interval = (parseInt(data.saat) * 60 * 60) + (parseInt(data.dakika) * 60) + parseInt(data.saniye);
    console.log('[CLIENT] new interval: ' + interval);
    io.emit('updateData', { interval });
  });
});

server.listen(PORT, () => console.log(`[SERVER] listening on port *:${PORT}`));