#!/bin/sh
# Mount essential filesystems
mount -t proc none /proc
mount -t sysfs none /sys
mount -t devtmpfs devtmpfs /dev

# Invoke the actual system init (Python script, another shell script, etc.)
exec /usr/bin/python3 /usr/bin/cli.py
