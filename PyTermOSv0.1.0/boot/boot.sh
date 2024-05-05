#!/bin/sh
# Clear the screen
clear

# Use fbi to display the BMP image
# -T 1 tells fbi to use the current tty
# -noverbose suppresses loading info
# -a auto-resizes the image to fit the screen
fbi -T 1 -noverbose -a /imgs/PyTermOS.bmp/

# Display ASCII art after the image
echo "
   PPPP   y   y  TTTTT  EEEE  RRRR  M   M 
   P   P   y y     T    E     R   R MM MM       
   PPPP     y      T    EEE   RRRR  M M M       
   P        y      T    E     R  R  M   M      
   P        y      T    EEEE  R   R M   M 
"

# Wait until the system services have started
while ! systemctl --quiet is-system-running
do
    sleep 1
done

# Clear the screen on exit
clear
