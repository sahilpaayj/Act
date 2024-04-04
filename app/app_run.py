import os
import re
import cv2
import json
import time
import signal
import pytesseract
import multiprocessing
from PIL import Image
from display import add_macOS
from multiSS import capture

'''
Continuously Capture - Async preform OCR - Async check for no no's

run() - checks every ~5 seconds~ if a user is using specific websites
    stops when stop.txt is in this repo or ctrl + c
    Creates directory for screenshots, opens queues for image processing + pattern matching
    Finds active browser, takes picture, puts picture on image queue
    preprocess_image() receives image, preprocesses, sends to process_image() 
    process_image() runs OCR, puts output on text queue for check_patterns() 
    check_patterns() receives text, runs pattern matching

BUGS...
#TODO: ASAP stop.txt to exit is wack, need a better way. Maybe GUI? but where would they start the GUI from. maybe separate app w sole purpose of creating stop.txt?
#TODO: Bug for small display? check logs

ENHANCEMENTS...
#TODO: Clean up screenshots on program close. unless id'd nono?
#TODO: Add mark to the image where nono found
#TODO: Only take pictures when the display is a web browser? no online shopping offline but wb app purchases? sm we worry about? prolly, gamers
'''
def run(interval=5, debug=True):
    if debug: print('DEBUGGING ENABLED')

    # Create directory for this sessions screenshots
    parent = os.path.dirname(os.path.abspath(__file__))
    directory = os.path.join(parent, f'screenshots/test_{time.strftime("%Y-%m-%d_%H-%M-%S")}')
    os.makedirs(directory, exist_ok=True) # Check if directory exists, create if not

    # Create a Queue for communication between main process and OCR process
    image_queue = multiprocessing.Queue(maxsize=10)
    text_queue = multiprocessing.Queue(maxsize=10)
    websites = load_json(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nono.json'))

    image_process = multiprocessing.Process(target=process_image, args=(image_queue, text_queue, debug, ))
    image_process.start()

    text_process = multiprocessing.Process(target=check_patterns, args=(text_queue, websites, debug, ))
    text_process.start()

    index = 0
    stop_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stop.txt')
    while True:
        try:
            # Only hits if it finds stop.txt in repo (for now)
            if os.path.exists(stop_file):
                if debug: print(f"---------\n{time.strftime('%Y-%m-%d_%H-%M-%S')}: Stop file found. Exiting.")
                os.remove(stop_file)
                graceful_shutdown(image_queue, text_queue, image_process, text_process, debug)
                break

            # Get the geometry of the active window
            monitor = add_macOS()
            
            # Proceed only if monitor dimensions are valid
            if monitor['width'] == -1 or monitor['height'] == -1:
                raise ValueError("Invalid monitor dimensions received.")

            filename = f"{directory}/cwi_c{index}.png"
            capture(monitor, filename, debug)
            preprocess_image(filename, debug)

            # Send the filename to the OCR process for processing
            image_queue.put(filename)
            index += 1
        except ValueError as ve:
            if debug: print(f"Error encountered: {ve}. Retrying in {interval} seconds.")
        except Exception as e:
            if debug: print(f"An unexpected error occurred: {e}. Retrying in {interval} seconds.")
        finally:
            time.sleep(interval)

# Speed up OCR with preprocessing, in secondary queue
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

# tesseract-OCR on the image, in secondary queue
def process_image(image_queue, text_queue, debug):
    pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
    while True:
        # Wait for an image filename from the main process
        filename = image_queue.get()
        if filename is None:
            if debug: print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')}: image_queue shut down")
            text_queue.put(None)
            break  # Exit the loop if None is received, signaling the end of the program

        # Perform OCR on the image
        if debug: print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')}: Starting OCR")
        ocr = pytesseract.image_to_string(Image.open(filename))
        text_queue.put(ocr)

# Check text ocr output against websites on nono list in a separate process
def check_patterns(text_queue, websites, debug):
    while True:
        ocr = text_queue.get() # Text to check
        if ocr is None:
            if debug: print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')}: text_queue shut down")
            break  # Exit the loop if None is received, signaling the end of the program

        if debug: print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')}: Checking for nono websites")

        for website in websites:
            if re.search(website, ocr, re.IGNORECASE):
                print(f"\nNO NO DETECTED")
                break

# Load websites on nono list from JSON file, called only once
def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['patterns']

# Close queues and processes gracefully, called only once
def graceful_shutdown(image_queue, text_queue, image_process, text_process, debug):
    try:
        image_queue.put(None)  # stop OCR in process_image() + puts None in text_queue > stops text_process
        image_process.join()
        text_process.join()
        image_queue.close()
        text_queue.close()
        for p in multiprocessing.active_children():
            p.terminate()
            p.join()
    except Exception as e:
        if debug: print(f"An error occurred during shutdown: {e}")
    finally:
        if debug: print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')}: Shutdown complete.")
        os._exit(0)  # Forcefully exit the program with a success status

if __name__ == '__main__':
    run()