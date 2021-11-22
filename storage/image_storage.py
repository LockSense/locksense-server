import argparse
import json

import numpy as np
import paho.mqtt.client as mqtt
from PIL import Image

SAVED_IMAGE_DIR = 'images'

IMAGE_DATA_TOPIC = "image/data"

device_door_map = {
    "web_61f3442604cb": "door1",  # Samsung Galaxy
    "web_4342e44ea8da": "door2",  # Dorcas' iPhone
    "web_40cf1dd6a603": "door2",  # Laptop
}


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Successfully connected to broker.")
        client.subscribe(IMAGE_DATA_TOPIC)
    else:
        print("Connection failed with code: %d." % rc)


def on_message(client, userdata, msg):
    recv_dict = json.loads(msg.payload)

    filename = recv_dict["filename"]
    device = recv_dict["device"]
    data = recv_dict["data"]
    print("Received '%s' from %s. Size: %s." %
          (filename, device, np.shape(data)))

    if device not in device_door_map:
        print("Error: unrecognised device")
        return

    door_id = device_door_map[device]

    img_data = np.array(data).astype(np.uint8)

    img = Image.fromarray(img_data)
    img.save('%s/%s/%s' % (SAVED_IMAGE_DIR, door_id, filename))


def setup(hostname, username, password, tls=False):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(username, password)

    port = 1883
    if tls:
        client.tls_set()
        port = 8883

    client.connect(hostname, port=port)
    client.loop_start()
    return client


def main():
    parser = argparse.ArgumentParser(
        description='Run image classifying service.')
    parser.add_argument('-u', '-username', dest='username', required=True,
                        help='username for connecting to MQTT broker')
    parser.add_argument('-p', '-password', dest='password', required=True,
                        help='password for connecting to MQTT broker')

    args = parser.parse_args()

    setup("locksense.dorcastan.com", args.username, args.password, tls=True)
    while True:
        pass


if __name__ == '__main__':
    main()
