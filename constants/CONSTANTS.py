# "CONSTANTS" for mock pipeline Apache Kafka application

import os

IMAGE_ANALYSIS_TOPIC    = "image_analysis"
IMAGE_EVENT_ALERT_TOPIC = "image_event_alert"

CODE_DIR = os.getcwd()

# original image is the first received image and
# is used to generate the second received image
ORIGINAL_IMAGE_DIR  = CODE_DIR + "/image_original"
ORIGINAL_IMAGE_PATH = ORIGINAL_IMAGE_DIR + "/original_image.jpg"

IMAGE_RECV_DIR         = CODE_DIR + "/image_receiving"       # directory holding new images for image receiving client
IMAGE_DB_DIR           = CODE_DIR + "/image_database"        # mock "database" to store received images in
IMAGE_ANALYSIS_DIR     = CODE_DIR + "/image_analysis"        # directory to move received images into for image analysis client
IMAGE_EVENT_DB_DIR     = CODE_DIR + "/image_event_database"  # mock "database" to store image events (including difference images)
IMAGE_EVENT_ALERTS_DIR = CODE_DIR + "/image_event_alerts"     # contains log of image event alerts that have been sent

# total number of images to be received
TOTAL_NUM_IMAGES = 10
