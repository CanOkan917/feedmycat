import socketio
import time

socket = socketio.Client()

interval = 0
_lastfeed = 0

@socket.event
def connect():
  global _lastfeed
  print('[CLIENT] connection established, sid:', socket.sid)
  if _lastfeed != 0:
    sendRunDetails(_lastfeed)

@socket.event
def disconnect():
  print('[CLIENT] disconnected')

@socket.on('updateData')
def _updateData(data):
  global interval
  interval = int(data['interval'])
  print(f'[CLIENT] data update recieved! Interval: {interval}')

def run():
  socket.connect('http://puf.okancore.com:80')
  # socket.connect('http://192.168.1.55:80')
  return socket

def updateLastFeed(lastFeed): 
  if socket.connected:
    # socket.emit('feeddata', { 'timestamp': lastFeed })
    socket.emit('initialData', {'lastfeed': lastFeed })
  else:
    print('[CLIENT] socket isnt connected!')

def sendRunDetails(lastfeed):
  global _lastfeed
  _lastfeed = lastfeed
  if socket.connected:
    print('[CLIENT] sending initial data')
    socket.emit('initialData', {'lastfeed': lastfeed})
  else:
    print('[CLIENT] socket isnt connected!')

def getFeedingInterval():
  global interval
  return interval

if __name__ == '__main__':
  run()