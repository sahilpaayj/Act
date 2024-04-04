import os
import re
import cv2
import json
import time
import signal
import functools
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
#TODO: ASAP stop.txt to exit is wack, need a better way. Maybe GUI? but they would start a GUI to end a background process?
    maybe an exectuable, do they ever need to stop this process? maybe we build it so it never ends.
#TODO: Bug for small display? check logs, seen in hover over domain in tab in chrome 

ENHANCEMENTS...
#TODO: If nono detected, move image elsewhere, 
       Clean up no nono images unless testing
       mark the found pattern in red? thats tough the way im doing text, but would be useful. 
#TODO: Only take pictures when the display is a web browser? no online shopping offline but wb app purchases? sm we worry about? prolly, gamers
'''
class ContinuousScreenCapture:
    def __init__(self, interval=5, debug=True):
        self.interval = interval
        self.debug = debug

        self.parent = os.path.dirname(os.path.abspath(__file__))
        self.directory = os.path.join(self.parent, f'screenshots/test_{time.strftime("%Y-%m-%d_%H-%M-%S")}')

        self.websites = self.load_json(os.path.join(self.parent, 'nono.json'))

        self.shutdown_event = multiprocessing.Event()

    def run(self):
        if self.debug: print('DEBUGGING ENABLED')

        handler = functools.partial(self.signal_handler)
        signal.signal(signal.SIGINT, handler)
        
        os.makedirs(self.directory, exist_ok=True)

        # Set up queues for image processing and pattern recognition (just text for now)
        # in here bc of https://github.com/python/cpython/issues/90549
        image_queue = multiprocessing.Queue(maxsize=10)
        text_queue = multiprocessing.Queue(maxsize=10)

        image_process = multiprocessing.Process(target=self.process_image, args=(image_queue, text_queue, self.debug))
        image_process.start()

        text_process = multiprocessing.Process(target=self.check_patterns, args=(text_queue, self.websites, self.debug))
        text_process.start()

        # call infinite loop
        try:
            self.capture_and_process_loop(image_queue)
        finally:
            self.graceful_shutdown(image_queue, image_process, text_queue, text_process)

    def capture_and_process_loop(self, image_queue):
        index = 0
        stop_file = os.path.join(self.parent, 'stop.txt')
        while not self.shutdown_event.is_set():
            if os.path.exists(stop_file):
                if self.debug: print(f"---------\n{time.strftime('%Y-%m-%d_%H-%M-%S')}: Stop file found, exiting...")
                os.remove(stop_file)
                break

            monitor = add_macOS() # Find the user's active display
            if monitor['width'] == -1 or monitor['height'] == -1:
                raise ValueError("Invalid monitor dimensions received.")

            filename = f"{self.directory}/cwi_c{index}.png"
            capture(monitor, filename, self.debug) # Screen capture the active display, save as filename
            self.preprocess_image(filename, self.debug)
            image_queue.put(filename)
            index += 1
            time.sleep(self.interval)

    # Preprocess for tesseract-OCR
    def preprocess_image(self, image_path, debug):
        if debug: print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')}: Preprocessing started")
        image = cv2.imread(image_path)
        
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
        
        cv2.imwrite(image_path, scaled) 

    # Process with tesseract-OCR, surprise, surprise
    def process_image(self, image_queue, text_queue, debug):
        pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
        while True:
            filename = image_queue.get()
            if filename is None: break  

            if debug: print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')}: Starting OCR")
            ocr_text = pytesseract.image_to_string(Image.open(filename))
            text_queue.put(ocr_text)

    # Check OCR text against entries in nono.json
    def check_patterns(self, text_queue, websites, debug):
        while True:
            ocr_text = text_queue.get()
            if ocr_text is None: break

            if debug: print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')}: Checking for nono websites")
            for website in websites:
                if re.search(website, ocr_text, re.IGNORECASE):
                    print(f"\nNO NO DETECTED")
                    break

    # Load nono.json, only happens in init()
    def load_json(self, file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    # Gracefully close multiprocessing queues
    def graceful_shutdown(self, image_queue, image_process, text_queue, text_process):
        image_queue.put(None)
        image_queue.close()
        image_process.join()

        if self.debug: print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')}: image_queue shut down")
        
        text_queue.put(None)
        text_queue.close()
        text_process.join()
        if self.debug: print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')}: text_queue shut down")

        if self.debug: print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')}: main queue shut down.")
        if len(multiprocessing.active_children()) > 0:
            print(f"but iam still heh so ya fooked innit")
        os._exit(0)

    # Handle "ctrl + C"
    def signal_handler(self, signum, frame):
        if self.debug: print(f"---------\n{time.strftime('%Y-%m-%d_%H-%M-%S')}: Signal received, exiting...")
        self.shutdown_event.set()

if __name__ == '__main__':
    # adaptation of workaround bc of https://github.com/python/cpython/issues/90549
    if hasattr(multiprocessing, 'set_start_method'):
        try:
            multiprocessing.set_start_method('fork')
        except RuntimeError as e:
            print(f"Error setting multiprocessing start method: {e}")
    csc = ContinuousScreenCapture(10,False)
    csc.run()
