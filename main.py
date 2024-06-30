import drivers
import time
import subprocess
import os
import RPi.GPIO as GPIO
import serverconnection as Server

readyToFeed = False
feedInterval = 21600 # Saniye cinsinden
portions = 1
FEEDFILE="/home/canok/feeder/LASTFEED"

MOTOR_RELAY_PIN = 23
BUZZER_PIN = 17

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR_RELAY_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(BUZZER_PIN, GPIO.OUT, initial=GPIO.LOW)

display = drivers.Lcd()

local_ip = str(subprocess.check_output(['hostname', '-I'])).split(' ')[0].replace("b'", "")

def saveLastFeed():
  global FEEDFILE
  global lastFeed
  with open(FEEDFILE, 'w') as feedFile:
    feedFile.write(str(lastFeed))
  feedFile.close()

def feednow():
  global GPIO
  global portions
  GPIO.output(BUZZER_PIN, GPIO.HIGH)
  time.sleep(0.2)
  GPIO.output(BUZZER_PIN, GPIO.LOW)
  GPIO.output(MOTOR_RELAY_PIN, GPIO.HIGH)
  time.sleep(0.8 * portions)
  GPIO.output(MOTOR_RELAY_PIN, GPIO.LOW)
  return time.time()

def updateIntervalFromServer(broadcast = False):
  global feedInterval
  if Server.getFeedingInterval() != 0:
    feedInterval = Server.getFeedingInterval()
    if broadcast:
      print('[SYSTEM] Getting interval from server records. Interval: ', feedInterval)
    return feedInterval

try:
  print('[SYSTEM] Starting system...')
  if os.path.isfile(FEEDFILE):
    with open(FEEDFILE, 'r') as feedFile:
      lastFeed = float(feedFile.read())
    feedFile.close()
  else:
    lastFeed = time.time()
    saveLastFeed()
  
  Server.run()
  Server.sendRunDetails(lastFeed)
  while Server.getFeedingInterval() == 0:
    time.sleep(.6)
  updateIntervalFromServer(True)
  
  print(f'[SYSTEM] Current interval: {feedInterval}')
  
  while True:
    display.lcd_display_string("IP: " + local_ip, 1)
    feedInterval = updateIntervalFromServer()
    if (time.time() - lastFeed) > feedInterval:
      display.lcd_display_string(" Feeding now... ", 2)
      print('[SYSTEM] Feeding now')
      lastFeed = feednow()
      saveLastFeed()
      Server.updateLastFeed(lastFeed)
    else:
      timeToFeed = (lastFeed + feedInterval) - time.time()
      display.lcd_display_string("Next:" + time.strftime("%Hh %Mm %Ss", time.gmtime(timeToFeed)), 2)
    time.sleep(.6)
    
except KeyboardInterrupt:
  print('[SYSTEM] System shutdown! Cleaning...')
  display.lcd_clear()
  GPIO.cleanup()
  
# except:
#   print('[SYSTEM] System error!')