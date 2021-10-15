# locksense-server

This repository sets up a cloud server for an Internet of Things (IoT) system 
that serves as an MQTT broker and data storage provider.

## Setting Up

1. Clone this Git repository.
1. Install Docker and Docker Compose on the host machine.
1. Configure authentication credentials for the MQTT broker by adding a password file to `mqtt-broker/passwd`. 
   This file can be created by installing and running the `mosquitto_passwd` utility, which will prompt for a password before saving it.
   ```
   mosquitto_passwd -c mqtt-broker/passwd <username>
   ```
1. Start the application by running `docker-compose` from the root project directory:
    ````
    docker-compose up --detach
    ````
 
## References \& Links

- [Setting up a secure MQTT broker (without Docker)](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-the-mosquitto-mqtt-messaging-broker-on-ubuntu-18-04)
- [Obtaining an SSL certificate from Let's Encrypt](https://www.digitalocean.com/community/tutorials/how-to-use-certbot-standalone-mode-to-retrieve-let-s-encrypt-ssl-certificates-on-ubuntu-1804)
