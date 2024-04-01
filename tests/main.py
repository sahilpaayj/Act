import re
import os
import mss
import time
import json
import signal
import pytesseract

from PIL import Image
from multiprocessing import Process, Manager

from fint.display import add_macOS

# Continuously capture active window, send to OCR (process_image())
def cc_aocr(directory, image_queue, text_queue, interval, debug):
    index = 0
    with mss.mss() as sct:
        while True:
            signal.signal(signal.SIGINT, stop_process(image_queue, text_queue))
            # Get geometry of the user's active window
            monitor = add_macOS()
            filename = f"{directory}/cwi_c{index}_{time.strftime('%Y-%m-%d_%H-%M-%S')}.png" 
                
            # Screen grab active window
            ss = sct.grab(monitor)
            mss.tools.to_png(ss.rgb, ss.size, output=filename)
            if debug: print(f"---------\nScreenshot saved as {filename}  -  {time.strftime('%Y-%m-%d_%H-%M-%S')}")

            # Add filename to the queue for ocr, prepare for next
            image_queue.put(filename)
            index +=1
            time.sleep(interval)

def signal_handler(signal_number, frame):
    stop_process(image_queue, text_queue)

def stop_process(image_queue, text_queue):
    image_queue.put(None)  
    text_queue.put(None)  
    print("Gracefully shutting down")

# Send image through Google OCR to check for websites (check_websites())
def process_image(image_queue, text_queue, pytesseract_cmd, debug):
    pytesseract.pytesseract.tesseract_cmd = pytesseract_cmd
    while True:
        filename = image_queue.get()

        # Check for the poison pill to shut down
        if filename is None:  
            text_queue.put(None)  # Pass the poison pill to the next queue
            break

        # Perform OCR
        ocr = pytesseract.image_to_string(Image.open(filename))
        if debug: print(f"OCR Output: {ocr}")
        text_queue.put(ocr)  # Put the OCR result into the text queue

# Parse OCR text for website names
def check_websites(text_queue, websites, debug):
    while True:
        ocr_text = text_queue.get()

        # Check for the poison pill to shut down
        if ocr_text is None: 
            break

        if debug: print("Checking OCR text for websites")
        for website in websites:
            if re.search(website, ocr_text, re.IGNORECASE):
                print(f"Detected not allowed website: {website}")
                break

def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['patterns']

# Load variables and queues
def run(interval, debug=False):
        tesseract_path = r'/usr/local/bin/tesseract'  # Path from $ which tesseract, download tesseract-ocr.exe
        websites = load_json(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nono.json'))  # Finds the .json file in this repo

        # Open queues
        manager = Manager()
        image_queue = manager.Queue()
        text_queue = manager.Queue()

        image_process = Process(target=process_image, args=(image_queue, text_queue, tesseract_path, debug))
        check_websites_process = Process(target=check_websites, args=(text_queue, websites, debug))

        image_process.start()
        check_websites_process.start()

        # Path to save the screen grabs
        parent = os.path.dirname(os.path.abspath(__file__))
        directory = os.path.join(parent, f'screenshots/test_{time.strftime("%Y-%m-%d_%H-%M-%S")}')
        os.makedirs(directory, exist_ok=True) # Check if directory exists, create if not
        cc_aocr(directory, image_queue, text_queue, interval, debug)

if __name__ == '__main__':    
    run(5, True)