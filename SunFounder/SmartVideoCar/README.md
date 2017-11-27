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
Run `sudo apt-get install hostapd isc-dhcp-server`
Run `sudo nano /etc/hostapd/hostapd.conf` and use the following as an example
```
interface=wlan0
#driver=nl80211
bssid=b8:27:eb:98:8c:a7 # specify mac address of the usb wifi
ssid=Pi_AP-1c54  # name of wifi
country_code=US
hw_mode=g
channel=11
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=Raspberry
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
wpa_group_rekey=86400
ieee80211n=1
wme_enabled=1
```

# Setup monitor mode of wifi card
1. Check with `iw dev` which interface to use, in our case `wlan1` on `phy1` is what we want
2. Double check if `iw phy phy1 info` returns `monitor` in `Supported interface modes`
3. Do the following
```
sudo iw phy phy1 interface add mon1 type monitor
sudo iw dev wlan1 del
sudo ifconfig mon1 up
sudo iw dev mon1 set freq 2437
iwconfig mon1
```

# Capture RSS signal of, e.g., sandlab wireless network
```sudo tcpdump -i mon1 -n -tttt | grep sandlab | awk '{print $8}'```
