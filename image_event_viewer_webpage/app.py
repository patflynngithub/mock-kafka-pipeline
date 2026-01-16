"""
This is an image event viewer for the image pipeline, 
displaying a webpage to allow viewing an image event's
involved images.

It uses the python Flask framework, which allows having
dynamic webpages via server-side python scripting.

None of Flask's nice organizational and management tools are used here.
For now, I want to stay close to the low-level for generating
dynamic webpages so that I can renew and extend my basic front-end
skills.
"""

import os

from flask import Flask, request, send_from_directory

app = Flask(__name__)

# Absolute path to the image pipeline main directory inside the container
# (via using the -v argument with the docker run command).
# The images and the image event and image event alert info text files are in 
# subdirectories of this directory.
IMAGE_FOLDER = "/pipeline"

# ----------------------------------------------------------------------------------

def extract_path(a_string):

    """ Extract the path from the string. """

    start_wanted_path = a_string.find("/pipeline")
    wanted_path = a_string[start_wanted_path:-1]

    return wanted_path

# -------------------------------------------------------------------------------------

def get_image_paths(image_event_alert_path):

    """ Use image event alert file to get image paths from image event file. """

    image_path      = None
    diff_image_path = None
    prev_image_path = None

    # Get image event file path from image event alert file
    try:
        with open(image_event_alert_path, 'r') as f:
            lines = f.readlines()
    
        for line in lines:
            line = line.strip()

        image_event_path = extract_path(lines[1])

    except FileNotFoundError:
        print(f"Error: Image event alert file {image_event_alert_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    # Get image, previous image and difference image paths from image event file
    try:
        with open(image_event_path, 'r') as f:
            lines = f.readlines()
    
        for line in lines:
            line = line.strip()

        image_path      = extract_path(lines[2])
        prev_image_path = extract_path(lines[3])
        diff_image_path = extract_path(lines[4])

    except FileNotFoundError:
        print(f"Error: The file '{image_event_path}' was not found.")
    except Exception as e:
        traceback.print_exc()
        print(f"An error occurred: {e}")

    return image_path, diff_image_path, prev_image_path

# ----------------------------------------------------------------------------

def get_image_event_imgs(alert_num_str):
    
    """
    Using the image event alert number, the path to the image event alert info text file
    is generated, which is used to get the image event image paths.
    """

    alert_num = int(alert_num_str)
    image_event_alert_path = f"/pipeline/image_event_alerts/image_event_alert_{alert_num:03d}.txt"

    image_path, diff_image_path, prev_image_path = get_image_paths(image_event_alert_path)

    return image_path, diff_image_path, prev_image_path

# ----------------------------------------------------------------------------------------

@app.route('/pipeline/<path:filename>')
def serve_image(filename):

    """
    Send webpage requested image to the web browser
    """
    return send_from_directory(IMAGE_FOLDER, filename)

# ----------------------------------------------------------------------------------------

@app.route('/')
def display_page():

    """
    Dislays the image event alert number entry dynamic webpage. 
    It handles two states of the webpage. First is the initial
    accepting of input of an image event alert number. Second is
    the display of the image event images associated with the
    input alert number.
    """

    # note extra empty line to end the headers
    webpage = "<!DOCTYPE html>\n\n"

    # Collect the HTML content

    webpage += "<html>\n"
    webpage += "<head><title>Image Event Viewer</title></head>\n"
    webpage += "<body>\n"

    webpage += '<h2 style="text-align:center;">Enter an image event alert number</h2>\n'
    webpage += '<h5 style="text-align:center;">(positive integer)</h5>\n'
    webpage += '<form style="text-align:center;" action="http://127.0.0.1:8000">\n'
    webpage += '   <label for="alert_num">Alert number:</label><br>\n'
    webpage += '   <input type="text" id="alert_num" name="alert_num"><br>\n'
    webpage += '   <input type="submit" value="Submit">\n'
    webpage += '</form>\n\n'

    alert_num = request.args.get('alert_num','')
    if alert_num:
        if not alert_num.isdecimal():
            webpage += f'<p style="text-align:center;">Alert number needs to be a positive integer: \"{alert_num}\" entered</p>\n'

        # a positive integer number was input
        else:
            # Display the images of the image event

            webpage += f'<p style="text-align:center;">Alert number: {alert_num}</p>\n'
            image_path, diff_image_path, prev_image_path = get_image_event_imgs(alert_num)

            webpage  +=  '<div style="display: flex; justify-content: center; gap: 20px;" class="image_and_prev_image">\n'
            webpage  +=  "<figure>\n"
            webpage  += f'  <img src="{prev_image_path}"" style="width: auto; height: auto; max-width: 100%;">\n'
            webpage  +=  "  <figcaption>Previous Image</figcaption>\n"
            webpage  +=  "</figure>\n"
            webpage  +=  "<figure>\n"
            webpage  += f'  <img src="{image_path}"" style="width: auto; height: auto; max-width: 100%;">\n'
            webpage  +=  "  <figcaption>Image</figcaption>\n"
            webpage  +=  "</figure>\n"
            webpage  +=  '</div>\n'

            webpage  +=  '<div style="display: flex; justify-content: center; gap: 20px;" class="diff_image">\n'
            webpage  +=  "<figure>\n"
            webpage  += f'  <img src="{diff_image_path}"" style="width: auto; height: auto; max-width: 100%;">\n'
            webpage  +=  "  <figcaption>Difference Image</figcaption>\n"
            webpage  +=  "</figure>\n"
            webpage  +=  '</div>\n'

    webpage += "</body>\n"
    webpage += "</html>\n"

    return webpage

# ==================================================================

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)

