import os
import re
import cv2
import json
import time
import signal
import functools
import threading
import pytesseract
import multiprocessing
import tkinter as tk

from PIL import Image
from queue import Queue
from tkinter import messagebox

from display import get_active_display_dimensions
from multiSS import capture, get_primary_screen_dimensions


class ContinuousScreenCapture:
    '''
    Continuously Capture - Async preform OCR - Async check for no no's - Go to thread 2 for

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
    #TODO: Account for load conditions in queue and process management
    #TODO: Pass websites through from app_start instead of nono.json()
    '''
    def __init__(self, interval=5, debug=True):
        self.interval = interval
        self.debug = debug

        self.parent = os.path.dirname(os.path.abspath(__file__))
        self.directory = os.path.join(self.parent, f'screenshots/test_{time.strftime("%Y-%m-%d_%H-%M-%S")}')

        self.websites = self.load_json(os.path.join(self.parent, 'nono.json'))

        self.shutdown_event = multiprocessing.Event()
        self.nono_detected_event = multiprocessing.Event()
        self.nono_detected_site = multiprocessing.Queue()  # To store the website name

        #self.gui_queue = Queue()
        #self.popup_event = threading.Event()

        # Initialize GUI thread
        #self.gui_thread = GuiThread(self.gui_queue, self.popup_event)
        #self.gui_thread.start()  # Runs the run method

        self.nono_detected = None

        self.run()

    def run(self):
        if self.debug: print('DEBUGGING ENABLED')

        handler = functools.partial(self.signal_handler)
        signal.signal(signal.SIGINT, handler)
        
        os.makedirs(self.directory, exist_ok=True)

        # Set up queues for image processing and pattern recognition (just text for now)
        # in here bc of pickling error when passing queues + processes as self.___. 
        # if you know how to move this to init(), or do it better, take a rip
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
            # Shut down without a terminal
            if os.path.exists(stop_file):
                if self.debug: print(f"---------\n{time.strftime('%Y-%m-%d_%H-%M-%S')}: Stop file found, exiting...")
                os.remove(stop_file)
                break
            
            # Check for detections
            #if self.nono_detected_event.is_set():
            #    website = self.nono_detected_site.get()  # Retrieve the detected site
            #    if self.debug: print(f"---------\n{time.strftime('%Y-%m-%d_%H-%M-%S')}: Requesting popup for website: {website}")
            #    self.gui_queue.put("show_popup")   # Request the GUI thread to show the popup
            #    self.popup_event.wait() # Wait here for the popup to be acknowledged before continuing
            if self.nono_detected_event.is_set():
                if self.debug: print(f"---------\n{time.strftime('%Y-%m-%d_%H-%M-%S')}: Popup open, website: {self.nono_detected}")
                website = self.nono_detected_site.get()  # Retrieve the detected site
                self.show_nono_popup(website)
                self.nono_detected_event.clear()  # Reset the event for future detections

            # Find dimensions of the user's active window 
            monitor = get_active_display_dimensions() 
            #if monitor['width'] == -1 or monitor['height'] == -1:  # If fails, default to user's primary monitor (wherever they have selected)
            #    if self.debug: print(f"---------\n{time.strftime('%Y-%m-%d_%H-%M-%S')}: Defaulting to primary monitor")
            #    monitor = get_primary_screen_dimensions() 

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
                    print(f"\nNO NO DETECTED: website: {website}")
                    self.nono_detected_site.put(website)  # Store the detected site
                    self.nono_detected_event.set()  # Signal that a nono was detected             
                    break

    # Display a popup when a nono is detected and pause the program execution.
    def show_nono_popup(self, website):
        # This function will block the calling thread until the messagebox is closed
        root = tk.Tk()
        root.withdraw()  # Hide the main window (optional)
        messagebox.showinfo("Nono Detected!", f"We saw you are on {website}. Are you sure that you want to continue?")
        root.quit()
        root.destroy()
        if self.debug: print(f"---------\n{time.strftime('%Y-%m-%d_%H-%M-%S')}: Popup closed")

    # Load nono.json, only happens in init()
    def load_json(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data['patterns']

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

'''
import tkinter as tk
from tkinter import messagebox
import threading
import queue

class GuiThread(threading.Thread):
    def __init__(self, gui_queue, popup_event):
        super().__init__()
        self.gui_queue = gui_queue
        self.popup_event = popup_event

    def run(self):
        print("GUI thread is running...")
        self.root = tk.Tk()
        self.root.withdraw()
        self.check_queue()
        self.root.mainloop()

    def check_queue(self):
        try:
            while True:
                message = self.gui_queue.get_nowait()
                if message == "show_popup":
                    print("Popup is comin, oh lawd")
                    self.show_popup()
        except queue.Empty:
            pass
        self.root.after(100, self.check_queue)

    def show_popup(self):
        # Show popup and pause main thread
        self.popup_event.clear()
        messagebox.showinfo("Malfesence Detected! Investigate🧐 Mode🔎", "We saw you are on a not allowed site. Are you sure that you want to continue?")
        self.popup_event.set()
'''

if __name__ == '__main__':
    # workaround from https://github.com/python/cpython/issues/90549
    if hasattr(multiprocessing, 'set_start_method'):
        try:
            multiprocessing.set_start_method('fork')
        except RuntimeError as e:
            print(f"Error setting multiprocessing start method: {e}")

    csc = ContinuousScreenCapture(15,True)