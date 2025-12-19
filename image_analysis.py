# IMAGE ANALYZER: receives Kafka messages from the image receiving client, analyzes the images
# (client)        for an image event of interest, and, if an image event is detected, it adds the 
#                 event to the image event database and it sends a Kafka message to the image 
#                 event alerting client

from constants.CONSTANTS import *

import os
import numpy as np
from PIL import Image

from kafka import KafkaProducer
from kafka import KafkaConsumer
import json

# -----------------------------------------------------------------------------------------------------

# Compares the two most recent images in the pipeline to see if they are different
# from each other. Is so, creates an image event and stores it in the "database."
def analyze_images(image_num, prev_image_num, image_event_num):

    # if no previous image
    if image_num == 0:
        print("First received image. No image to compare it with")
        return [False]

    image_analysis_path      = IMAGE_ANALYSIS_DIR + "/" + f"{image_num:05d}"      + ".jpg"
    prev_image_analysis_path = IMAGE_ANALYSIS_DIR + "/" + f"{prev_image_num:05d}" + ".jpg"

    # Open current and previous images and convert them to NumPy arrays (ensure the same dimensions and type)
    # note: these arrays will be float RGB (m x n x 3)
    image      = np.array(Image.open(image_analysis_path)).astype(float)
    prev_image = np.array(Image.open(prev_image_analysis_path)).astype(float)

    difference = image - prev_image
    l2_norm = np.linalg.norm(difference)
    print(f"l2 norm = {l2_norm}")

    # afer comparing the most recent two images, the previous image is not needed
    # in the image analysis directory anymore. The current image will become the
    # previous image for the next Kafka message
    os.remove(prev_image_analysis_path)

    # if we are dealing with the last generated image, it doesn't need to be kept around
    # in the image analysis directory to later function as the previous image 
    if image_num == TOTAL_NUM_IMAGES:
        os.remove(image_analysis_path)

    # if the two images are the same
    if l2_norm == 0:
        return [False]

    # else if the two images are different
    else:
        # Convert difference array to RGB format (uint8: 0...255)
       
        diff_min   = difference.min()
        diff_max   = difference.max()
        diff_range = diff_max - diff_min

        diff_01 = (difference - diff_min) / diff_range  # float between 0..1
        diff_uint8 = (diff_01 * 255.0).astype(np.uint8)
        diff_image = Image.fromarray(diff_uint8, 'RGB')

        print(f"Image event #{image_event_num}: images {prev_image_num} and {image_num} are different")

        # Store image event difference picture in image event "database"

        image_event_image_db_path = IMAGE_EVENT_DB_DIR + "/" + f"image_event_{image_event_num:03d}" + ".jpg"
        diff_image.save(image_event_image_db_path)
        diff_image.close()

        # Create image event file.

        image_event_db_path = IMAGE_EVENT_DB_DIR + "/" + f"image_event_{image_event_num:03d}" + ".txt"
        image_db_path       = IMAGE_DB_DIR       + "/" + f"{image_num:05d}"                   + ".jpg"
        prev_image_db_path  = IMAGE_DB_DIR       + "/" + f"{prev_image_num:05d}"              + ".jpg"

        event_file_lines = [f"Image event #: {image_event_num}", "Image event: picture has changed",
                            image_db_path, prev_image_db_path, image_event_image_db_path]

        with open(image_event_db_path, "w") as file:
            for line in event_file_lines:
                file.write(f"{line}\n")

        print(f"Image event database entry created: {image_event_db_path}")

        return [True, image_event_db_path]

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
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],  # Replace with your Kafka broker address
        value_serializer=lambda v: json.dumps(v).encode('utf-8') # Serialize messages to JSON bytes
    )

    # image events will use this variable
    image_event_num = 1

    print()
    print("Starting image analyzer client")
    print("CODE_DIR = " + CODE_DIR)
    print()

    for message in consumer:

        print(f"Received message: Topic={message.topic}, Value={message.value}")

        image_num      = message.value["image_num"]
        prev_image_num = image_num - 1

        # analyze current and previous images to see if the two are the same picture.
        # If so, create an image event and store in the image_event "database"
        retvals = analyze_images(image_num, prev_image_num, image_event_num)
        if retvals[0] == False:
            print()
            continue
        else:
            image_event_db_path = retvals[1]

            # Create and send a image event message to the image event alerting client

            message_data = {'image_event_num': image_event_num, 'image_event_db_path': image_event_db_path}
            producer.send(IMAGE_EVENT_ALERT_TOPIC, message_data)
            # Flush message to ensure delivery
            producer.flush()
            print(f"Sent image event # {image_event_num} message to the image event alerting client")

            image_event_num += 1
            print()

