# locksense-server

This repository sets up a cloud server for an Internet of Things (IoT) system 
that serves as an MQTT broker and data storage provider.

## Setting Up

1. Clone this Git repository.
1. Install Docker and Docker Compose on the host machine.
1. Configure authentication credentials for the MQTT broker by adding a password file to `mqtt-broker/passwd`. 
   This file can be created by installing and running the `mosquitto_passwd` utility, which will then prompt for a password.
   ```sh
   mosquitto_passwd -c mqtt-broker/passwd <username>
   ```
1. Find a domain registrar and point your selected domain at the server's IP address.
1. Generate SSL certificates for your domain, then copy the certificates to the `mosquitto/certs` subdirectory:
   ```sh
   mkdir /mosquitto/certs
   cp -r -L /etc/letsencrypt/live/<domain> /mosquitto/certs
   ```
      * Note that the files under `/etc/letsencrypt/live/<domain>` are symbolic links to those under `/etc/letsencrypt/archive/<domain>`,
      so the `-L` option is used to follow the links and copy the contents of the actual files.
1. Change the ownership and group of the `mosquitto/certs` subdirectory so that it belongs to user `1883`:
   ```sh
   chown -R 1883:1883 /mosquitto/certs
   ```
      * This step is necessary because as of V2.0, Mosquitto loads TLS certificates as an unprivileged user instead of the root user.
      Since the `eclipse-mosquitto` Docker image runs Mosquitto as user `1883` (`mosquitto`), this user must be able to access the certificates.
1. Start the application by running `docker-compose` from the root project directory:
   ````sh
   docker-compose up --detach
   ````

## Usage

To test the connection to the MQTT broker from any machine, run the following in separate terminals:

```
mosquitto_sub -h <domain> -p 8883 -u <username> -P <password> -t test 
```

```
mosquitto_pub -h <domain> -p 8883 -u <username> -P <password> -t test -m "Hello World!"
```

Note that connections must be carried out over TLS, so we use the domain name (instead of an IP address)
and specify port `8883` (instead of the default `1883`).

The MQTT broker can also receive connections via WebSockets over TLS (WSS).
Example code using the [MQTT.js](https://github.com/mqttjs/MQTT.js) client library is given below:

```
const client = mqtt.connect(`wss://${MQTT_HOST}:9001`, {
  username: MQTT_USERNAME,
  password: MQTT_PASSWORD,
});

const topics = ['test', 'helloworld'];
client.on('connect', () => {
  console.log('Connected');
  client.subscribe(topics, (err, granted) => {
    console.log(`Subscribed to topic(s) '${granted.map((grant) => grant.topic).join("', '")}'`);

    client.publish('test', 'This works!', {}, (err) => {
      if (err) {
        console.error('Failed to publish message', err);
      }
    });
  });
});

client.on('message', (topic, message, packet) => {
  console.log(`[${topic}] Received Message:`, message.toString(), packet);
});
```

## References \& Links

- [Setting up a secure MQTT broker (without Docker)](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-the-mosquitto-mqtt-messaging-broker-on-ubuntu-18-04)
- [Obtaining an SSL certificate from Let's Encrypt](https://www.digitalocean.com/community/tutorials/how-to-use-certbot-standalone-mode-to-retrieve-let-s-encrypt-ssl-certificates-on-ubuntu-1804)
