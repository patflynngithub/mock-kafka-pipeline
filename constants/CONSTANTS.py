# "CONSTANTS"

import os

IMAGE_ANALYSIS_TOPIC = "image_analysis"
IMAGE_EVENT_TOPIC    = "image_event"

CODE_DIR           = os.getcwd()

ORIGINAL_IMAGE_DIR     = CODE_DIR + "/image_original"
# original image is the first received image and
# is used to generate first generated and second received image
ORIGINAL_IMAGE_PATH    = ORIGINAL_IMAGE_DIR + "/original_image.jpg"

IMAGE_RECV_DIR     = CODE_DIR + "/image_receiving"  # directory holding received images for image receiving client
IMAGE_DB_DIR       = CODE_DIR + "/image_database"   # "database" for MOCK pipeline instead of an actual SQL database
IMAGE_ANALYSIS_DIR = CODE_DIR + "/image_analysis"   # directory to move received images to for image analysis client
IMAGE_EVENTS_DIR   = CODE_DIR + "/image_events"     # directory to place image event text files in

# total number of images to be received
TOTAL_NUM_IMAGES = 10
