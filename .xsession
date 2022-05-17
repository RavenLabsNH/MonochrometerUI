#!/usr/bin/env bash
xset s off -dpms
exec matchbox-window-manager -use_cursor no &
while true; do
  unclutter &
  cd /home/pi/MonochrometerUI/
  sleep 5
  /usr/bin/python main.py
done
