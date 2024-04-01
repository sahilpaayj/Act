import os
import re
import mss
import json
import time
import pytesseract

from PIL import Image
from multiprocessing import Process, Queue

from display import add_macOS
from multiSS import capture

'''
Continuously Capture - Async OCR - Async Check

run() - checks every 5 seconds if a user is using specific websites
    reference nono.json in this repo as the list of unallowed websites
    theres a parameter for frequency of checks

#TODO: Clean up screenshots on program close, unless id'd
#TODO: Add mark to the place on the image that the model found
#TODO: Preprocess images, as small as possible
'''

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
        if debug: print(f"\n{time.strftime('%Y-%m-%d_%H-%M-%S')}\nChecking for nono websites\n")

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
        if debug: print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')}: Processed OCR for {filename}\n{ocr}\n")

# Creates Directory, opens queues + processes for ocr and pattern matching
# Finds active browser, gets a picture, puts picture on image queue
# process_image() receives image, runs OCR, puts output on text queue
# check_patterns() receives output, runs pattern matching
def run(interval=5, debug=False):
    if debug: print('DEBUGGING ENABLED')

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
    while True:
        # Get the geometry of the active window
        monitor = add_macOS()
        filename = f"{directory}/cwi_c{index}.png" 
        capture(monitor, filename, debug)

        # Send the filename to the OCR process for processing
        image_queue.put(filename)
        index += 1
        time.sleep(interval)

if __name__ == '__main__':
    run()