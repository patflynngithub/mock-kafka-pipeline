# IMAGE EVENT: receives image event Kafka messages from the image analysis client,
# ALERTER      "sends" image event alerts to those who have subscribed to them, and 
# (client)     logs the alerts

from constants.CONSTANTS import *

import os
import numpy as np
from PIL import Image

from kafka import KafkaConsumer
import json

# ===================================================================================================

# Main part of program

if __name__ == "__main__":

    # Create a Kafka Consumer instance for receiving messages from the 
    # image_receiving client
    consumer_topic = IMAGE_EVENT_ALERT_TOPIC
    consumer = KafkaConsumer(
        consumer_topic,  # Topic to consume from
        group_id='image_event_alert_group', # Consumer group for offset management
        bootstrap_servers=['localhost:9092'], # Replace with your Kafka broker address
        auto_offset_reset='earliest', # Start consuming from the beginning if no offset is found
        enable_auto_commit=True, # Automatically commit offsets
        value_deserializer=lambda v: json.loads(v.decode('utf-8')) # Deserialize messages from JSON bytes
    )

    print()
    print("Starting image event alert client")
    print("CODE_DIR = " + CODE_DIR)
    print()

    for message in consumer:

        print(f"Received message: Topic={message.topic}, Value={message.value}")

        image_event_num     = message.value["image_event_num"]
        image_event_db_path = message.value["image_event_db_path"]

        # HERE, EMAIL ALERTS WOULD BE SENT TO THOSE WHO HAVE SUBSCRIBED TO BE
        # ALERTED ABOUT THIS TYPE OF IMAGE EVENT

        image_event_alert_path = IMAGE_EVENT_ALERTS_DIR + "/" + f"image_event_alert_{image_event_num:03d}.txt"
        image_event_alert_lines = [f"Image event #: {image_event_num}",
                                   f"Image event database path: {image_event_db_path}"]
        with open(image_event_alert_path, "w") as file:
            for line in image_event_alert_lines:
                file.write(f"{line}\n")

        print(f"Image event alert stored in: {image_event_alert_path}")
        print()
        
