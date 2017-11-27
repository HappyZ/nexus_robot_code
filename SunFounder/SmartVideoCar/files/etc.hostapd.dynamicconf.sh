#!/bin/bash

serial=$(cat /proc/cpuinfo | grep Serial | md5sum | cut -c 1-4)
sed -i "s/^ssid=.*$/ssid=Pi_AP-$serial/" /etc/hostapd/hostapd.conf
