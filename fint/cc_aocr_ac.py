import os
import re
# import mss
import sys
import cv2
import json
import time
import shutil
import signal
import pytesseract

from PIL import Image
from multiprocessing import Process, Queue

from display import add_macOS
from multiSS import capture

'''
Continuously Capture - Async preform OCR - Async check for no no's

run() - checks every 5 seconds if a user is using specific websites
    reference nono.json in this repo as the list of unallowed websites
    theres a parameter for frequency of checks

#TODO: Clean up screenshots on program close, unless id'd
#TODO: Bug for small display ? check logs for error
#TODO: Add mark to the place on the image that the model found
#TODO: Only take pictures when the display is a web browser, no online shopping offline right? but games have in app purchases?
'''

def signal_handler(sig, frame):
    print('Gracefully exiting, cleaning up files')
    sys.exit(0)

def preprocess_image(image_path, debug):
    if debug: print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')}: Preprocessing started")
    image = cv2.imread(image_path) # Load the image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # Convert to grayscale
    blurred = cv2.GaussianBlur(gray, (5, 5), 0) # Noise reduction with Gaussian blur
    _, thresholded = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU) # Thresholding to get a binary image
    
    # Dilation and erosion to emphasize text
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    dilated = cv2.dilate(thresholded, kernel, iterations=1)
    eroded = cv2.erode(dilated, kernel, iterations=1)
    
    # Scaling - let's assume we want to standardize the height to 800 pixels
    ratio = 800 / eroded.shape[0] # First, get the ratio of the new height to the old height
    new_width = int(eroded.shape[1] * ratio) # Compute the new width
    scaled = cv2.resize(eroded, (new_width, 800), interpolation=cv2.INTER_AREA) # Resize the image
    
    # Resave image to same path
    cv2.imwrite(image_path, scaled) 
    if debug: print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')}: Preprocessing finished")

# Load websites on nono list from JSON file
def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['patterns']

# Check text ocr output against websites on nono list in a separate process
def check_patterns(text_queue, websites, debug):
    while True:
        ocr = text_queue.get() # Text to check
        if ocr is None:
            break  # Exit the loop if None is received, signaling the end of the program
        if debug: print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')}: Checking for nono websites")

        for website in websites:
            if re.search(website, ocr, re.IGNORECASE):
                print(f"\nNO NO DETECTED")
                break

# OCR on the captured image in a separate process
def process_image(image_queue, text_queue, debug):
    pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
    while True:
        # Wait for an image filename from the main process
        filename = image_queue.get()
        if filename is None:
            text_queue.put(None)
            break  # Exit the loop if None is received, signaling the end of the program

        # Perform OCR on the image
        ocr = pytesseract.image_to_string(Image.open(filename))
        text_queue.put(ocr)
        if debug: print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')}: Processed OCR for {filename}") #\n{ocr}\n")    # Not printing results of OCR right now, backspace this to print out OCR results

# Creates Directory, opens queues + processes for ocr and pattern matching
# Finds active browser, gets a picture, puts picture on image queue
# process_image() receives image, runs OCR, puts output on text queue
# check_patterns() receives output, runs pattern matching
def run(interval=5, debug=False):
    if debug: print('DEBUGGING ENABLED')
    #signal.signal(signal.SIGINT, signal_handler)

    # Create directory for this sessions screenshots
    parent = os.path.dirname(os.path.abspath(__file__))
    directory = os.path.join(parent, f'screenshots/test_{time.strftime("%Y-%m-%d_%H-%M-%S")}')
    os.makedirs(directory, exist_ok=True) # Check if directory exists, create if not

    # Create a Queue for communication between main process and OCR process
    image_queue = Queue()
    text_queue = Queue()
    websites = load_json(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nono.json'))

    ocr_process = Process(target=process_image, args=(image_queue, text_queue, debug, ))
    text_process = Process(target=check_patterns, args=(text_queue, websites, debug, ))

    ocr_process.start()
    text_process.start()

    index = 0
    #try:
    while True:
        # Get the geometry of the active window
        monitor = add_macOS()
        filename = f"{directory}/cwi_c{index}.png" 
        capture(monitor, filename, debug)
        preprocess_image(filename, debug)

        # Send the filename to the OCR process for processing
        image_queue.put(filename)
        index += 1
        time.sleep(interval)
    #except KeyboardInterrupt:
    #    print(f"Directory: {directory}")
    #    #shutil.rmtree(directory)
    #    pass

if __name__ == '__main__':
    run(5, True)