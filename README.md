<a href="https://www.buymeacoffee.com/rbpiuserf" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

# FreeDS-SCADA (work in progress, use only for testing purposes)
FreeDS SCADA developed using Node-Red

#### Project objectives
This projects implements a SCADA for FreeDS

#### Requeriments
1. Raspberry Pi administration skills
2. A Raspberry Pi, I'm using a Raspberry Pi 2 and a 16 GB SD card
3. Install and configure Mosquito MQTT broker:<br>
https://randomnerdtutorials.com/how-to-install-mosquitto-broker-on-raspberry-pi/
```
sudo apt install mosquitto mosquitto-clients
```
Edit /etc/mosquitto/mosquitto.conf and add at the end:
```
allow_anonymous true
listener 1883 0.0.0.0
```
Enable and restart Mosquitto:
```
sudo systemctl enable mosquitto.service
sudo service mosquitto restart
```
4. Install Node-Red:<br>
https://nodered.org/docs/getting-started/raspberrypi
```
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered) 
sudo systemctl enable nodered.service
sudo service nodered restart
```

5. Optional but recommendable: configure your timezone and enable time synchronization
```
sudo raspi-config
sudo systemctl enable systemd-timesyncd
```
6. Download <a href="FreeDS-SCADA.json" target="_blank"></a>, import it into Node-Red and enjoy !
