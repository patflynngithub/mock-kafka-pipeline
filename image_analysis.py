# IMAGE ANALYZER: receives Kafka messages from the image receiving client, analyzes the images
# (client)        for an image event of interest, and, if the image event is detected, it sends
#                 aKafka message to the image event alerting client

from constants.CONSTANTS import *

import os
import numpy as np
from PIL import Image

from kafka import KafkaProducer
from kafka import KafkaConsumer
import json

# -----------------------------------------------------------------------------------------------------

# Compares the two most recent imaages in the pipeline to see if they are different
def analyze_images(image_num, prev_image_num):

    global image_event_num

    # if no previous image
    if image_num == 0:
        print("First received image. No image to compare it with")
        return

    image_analysis_path      = IMAGE_ANALYSIS_DIR + "/" + f"{image_num:05d}"      + ".jpg"
    prev_image_analysis_path = IMAGE_ANALYSIS_DIR + "/" + f"{prev_image_num:05d}" + ".jpg"

    # Open images and convert to NumPy arrays (ensure the same dimensions and type)
    image      = np.array(Image.open(image_analysis_path).convert('L')) # Convert to grayscale for simplicity
    prev_image = np.array(Image.open(prev_image_analysis_path).convert('L'))

    # Calculate the element-wise difference
    difference = image.astype("float") - prev_image.astype("float")
    l2_norm = np.linalg.norm(difference)
    print(f"l2 norm = {l2_norm}")

    # afer comparing the most recent two images, the previous image is not needed
    # in the image analysis directory anymore. The current image will become the
    # previous image
    os.remove(prev_image_analysis_path)

    # if we are dealing with the last generated image, it doesn't need to be kept around
    # in the image analysis directory to later function as the previous image 
    if image_num == TOTAL_NUM_IMAGES:
        os.remove(image_analysis_path)

    if l2_norm != 0:  # the two images are different

        print(f"Image event #{image_event_num}: images {image_num} and {prev_image_num} are different")
        send_image_event_msg(image_num, prev_image_num)
        image_event_num += 1
        print()

# -----------------------------------------------------------------------------------------------------

# send an image event message to the image event alerter Kafka client
def send_image_event_msg(image_num, prev_image_num):

    image_event_path   = IMAGE_EVENTS_DIR + "/" + f"image_event_{image_event_num:03d}" + ".txt"
    image_db_path      = IMAGE_DB_DIR     + "/" + f"{image_num:05d}"                   + ".jpg"
    prev_image_db_path = IMAGE_DB_DIR     + "/" + f"{prev_image_num:05d}"              + ".jpg"

    # Create image event file
    
    event_lines = [f"Image event # {image_event_num}", image_db_path, prev_image_db_path]

    with open(image_event_path, "w") as file:
        for line in event_lines:
            file.write(f"{line}\n")

    print(f"Image event file created: {image_event_path}")
    
"""
    # send a Kafka message to the image event alerter client
    message_data = {image_event_num,'image_num' }
    producer.send("image_event_alert", message_data)
    # Flush message to ensure delivery
    producer.flush()

    print(f"Message sent to topic '{topic_name}': {message_data}")
    print()
"""

# ===================================================================================================

# Main part of program

if __name__ == "__main__":

    # Create a Kafka Consumer instance for receiving messages from the 
    # image_receiving client
    consumer_topic = IMAGE_ANALYSIS_TOPIC
    consumer = KafkaConsumer(
        consumer_topic,  # Topic to consume from
        group_id='image_analysis_group', # Consumer group for offset management
        bootstrap_servers=['localhost:9092'], # Replace with your Kafka broker address
        auto_offset_reset='earliest', # Start consuming from the beginning if no offset is found
        enable_auto_commit=True, # Automatically commit offsets
        value_deserializer=lambda v: json.loads(v.decode('utf-8')) # Deserialize messages from JSON bytes
    )

    # Create a Kafka Producer instance for sending messages to the image event alerting client
    producer_topic = IMAGE_EVENT_TOPIC
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],  # Replace with your Kafka broker address
        value_serializer=lambda v: json.dumps(v).encode('utf-8') # Serialize messages to JSON bytes
    )

    image_event_num = 1

    print()
    print("Starting image analyzer client")
    print("CODE_DIR = " + CODE_DIR)
    print()

    for message in consumer:

        print(f"Received message: Topic={message.topic}, Value={message.value}")

        image_num      = message.value["image_num"]
        prev_image_num = image_num - 1

        analyze_images(image_num, prev_image_num)

