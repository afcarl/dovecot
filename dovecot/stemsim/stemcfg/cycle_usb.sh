#!/bin/bash
sh -c "echo 0 > /sys/bus/usb/devices/$1/authorized"
sleep 0.1
sh -c "echo 1 > /sys/bus/usb/devices/$1/authorized"
sleep 0.1