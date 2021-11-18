import argparse
import json

import numpy as np
import paho.mqtt.client as mqtt
import tensorflow as tf
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.python.keras.backend import set_session

classes = ["empty", "lock-n-key", "lock-pick"]

MODEL_FILE = 'mobilenet-tuned.hd5'
SAVED_IMAGE_DIR = 'images'

CLASSIFY_TOPIC = "IMAGES/classify"
PREDICTION_TOPIC = "IMAGES/prediction"


session = tf.compat.v1.Session(graph=tf.compat.v1.Graph())

with session.graph.as_default(), session.as_default():
    model = load_model(MODEL_FILE)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Successfully connected to broker.")
        client.subscribe(CLASSIFY_TOPIC)
    else:
        print("Connection failed with code: %d." % rc)


def classify(filename, image):
    # print("Classifying %s..." % filename)

    with session.graph.as_default(), session.as_default():
        result = model.predict(image)

    max_class = np.argmax(result)

    label, score, index = classes[max_class], result[0][max_class], max_class
    # print("Done with %s." % filename)

    return {"filename": filename, "prediction": label,
            "score": float(score), "index": int(index)}


# TODO: graceful error handling

def on_message(client, userdata, msg):
    recv_dict = json.loads(msg.payload)

    filename = recv_dict["filename"]
    device = recv_dict["device"]
    data = recv_dict["data"]
    print("Received '%s' from %s. Size: %s." %
          (filename, device, np.shape(data)))

    img_data = np.array(data).astype(np.uint8)

    # TODO: create and save to device-specific directory
    img = Image.fromarray(img_data)
    img.save('%s/%s' % (SAVED_IMAGE_DIR, filename))

    img_data = np.expand_dims(img_data, axis=0) / 255
    result = classify(filename, img_data)

    print("Sending result: ", result)
    client.publish(PREDICTION_TOPIC, json.dumps(result))


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
