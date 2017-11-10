# Assemble the car

# Install Raspberry Pi
1. Download `SD Card Formatter` from https://www.sdcard.org/downloads/formatter_4/ based on your operating system
2. Format microsd card on your laptop
3. Download `Raspbian` from https://downloads.raspberrypi.org/raspbian_latest
4. Follow instructions at https://www.raspberrypi.org/forums/viewtopic.php?t=74176 to burn the image (system) onto the sdcard
5. Create an empty file named `ssh` in the root folder of micro sdcard
6. Insert the card into raspberry pi on the robotic car and power it up (with either a mini-usb cable or battery)

# Setup wired IP address
1. Connect to the raspberry pi by connecting an Ethernet cable to a router you have access to (wait for about 90s and `ssh pi@raspberrypi` should work)
2. Fix the Ethernet IP address to 192.168.1.10 and network mask to 255.255.255.0
3. Disconnect the cable to the router and connect it directly to your laptop
4. Set your laptop Ethernet IP address to be in the same subnet (e.g., 192.168.1.2)
5. Now you can ping 192.168.1.10 and hopefully you can connect to it (for the debugging purpose)

# Setup wireless networks



# Setup monitor mode of wifi card
1. Check with `iw dev` which interface to use, in our case `wlan0` on `phy0` is what we want
2. Double check if `iw phy phy0 info` returns `monitor` in `Supported interface modes`
3. Do the following
```sudo iw phy phy0 interface add mon0 type monitor
sudo iw dev wlan0 del
sudo ifconfig mon0 up
sudo iw dev mon0 set freq 2437
iwconfig mon0```

# Capture RSS signal of, e.g., sandlab wireless network
```sudo tcpdump -i mon0 -n -tttt | grep sandlab | awk '{print $8}'```
