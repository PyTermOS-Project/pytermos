#!/bin/sh
clear

echo "
   PPPP   y   y  TTTTT  EEEE  RRRR  M   M 
   P   P   y y     T    E     R   R MM MM       
   PPPP     y      T    EEE   RRRR  M M M       
   P        y      T    E     R  R  M   M      
   P        y      T    EEEE  R   R M   M 
"
while ! systemctl --quiet is-system-running
do
    sleep 1
done