import os
import time
import mss
import pytesseract
from fint.display import add_macOS
from PIL import Image
from multiprocessing import Process, Queue
import json
import re

# Tesseract-OCR locally on machine
# Continuously capture active window every {interval} seconds and send to pytesseract for OCR
#   directory - file path to save files to
#   index (int) - # of times this has been called externally, for file naming
#   interval (int) - sleep between capture
#   debug (bool) - turn on print statements
def cc_ocr(directory, index, interval, debug=False):
    # Check if directory exists, create if not
    os.makedirs(directory, exist_ok=True)

    # Location of tesseract executable - found with $ which tesseract
    pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'

    if debug: print('DEBUGGING ENABLED')

    with mss.mss() as sct:
        while True:
            # Get the geometry of the active window
            monitor = add_macOS()
            filename = f"{directory}/cwi_c{index}_{time.strftime('%Y-%m-%d_%H-%M-%S')}.png" 
                
            # Capture the specified monitor
            ss = sct.grab(monitor)
            mss.tools.to_png(ss.rgb, ss.size, output=filename)
            if debug: print(f"---------\nScreenshot saved as {filename}  -  {time.strftime('%Y-%m-%d_%H-%M-%S')}")

            ocr = pytesseract.image_to_string(Image.open(filename))
            if debug: print(f"\n{time.strftime('%Y-%m-%d_%H-%M-%S')}\n{ocr}\n")

            time.sleep(interval)


def process_image(image_queue):
        # Wait for an image filename from the main process
        filename = image_queue.get()
        if filename is None:
            return

        # send OCR on the image
        ocr = pytesseract.image_to_string(Image.open(filename))
        if self.debug: print(f"\n{time.strftime('%Y-%m-%d_%H-%M-%S')}\n{ocr}\n")

        self.text_queue.put(ocr)

def cc_aocr(interval, debug=False):
    parent = os.path.dirname(os.path.abspath(__file__))
    directory = os.path.join(parent, f'screenshots/test_{time.strftime("%Y-%m-%d_%H-%M-%S")}')
    os.makedirs(directory, exist_ok=True)

    # Tesseract OCR
    pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract' # Location of tesseract executable - found with $ which tesseract
    image_queue = Queue()
    image_process = Process(target=process_image)
    image_process.start()

    if debug: print('DEBUGGING ENABLED')

    index = 0
    with mss.mss() as sct:
        while True:
            # Get the geometry of the active window
            monitor = add_macOS()
            filename = f"{directory}/cwi_c{index}_{time.strftime('%Y-%m-%d_%H-%M-%S')}.png" 
                
            # Capture the specified monitor
            ss = sct.grab(monitor)
            mss.tools.to_png(ss.rgb, ss.size, output=filename)
            if debug: print(f"---------\nScreenshot saved as {filename}  -  {time.strftime('%Y-%m-%d_%H-%M-%S')}")

            image_queue.put(filename)
            #ocr = pytesseract.image_to_string(Image.open(filename))
            #if debug: print(f"\n{time.strftime('%Y-%m-%d_%H-%M-%S')}\n{ocr}\n")
            index += 1
            time.sleep(interval)



class Runner:
    def __init__(self, interval, debug=False):
        self.interval = interval

        self.debug = debug
        if self.debug: print('DEBUGGING ENABLED')

        # Create directory for this sessions screenshots
        
        os.makedirs(self.ss_path, exist_ok=True) # Check if directory exists, create if not

        # Websites to shut down - nono.json in repo
        self.websites = self.load_json(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nono.json'))
        self.text_queue = Queue()
        self.check_websites_process = Process(target=self.check_websites)
        self.check_websites_process.start()

    # Function to load patterns from the JSON file
    def load_json(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data['patterns']
    
    # Function to check OCR output against patterns
    def check_websites(self):
        ocr = self.text_queue.get() # Text to check
        if self.debug: print(f"\n{time.strftime('%Y-%m-%d_%H-%M-%S')}\nChecking for nono websites\n")

        for website in self.websites:
            if re.search(website, ocr, re.IGNORECASE):
                print(f"NO NO DETECTED\nFound pattern '{website}' in the text.")
                break
        else:
            print(f"All good")

    # Process images from Queue
    

    # Continuously capture specific dimensions and asynchronosly hit ocr
    def cc_aocr(self):
        index = 0
        with mss.mss() as sct:
            while True:
                # Get geometry of the user's active window
                monitor = add_macOS()
                filename = f"{self.ss_path}/cwi_c{index}_{time.strftime('%Y-%m-%d_%H-%M-%S')}.png" 
                    
                # Screen grab active window
                ss = sct.grab(monitor)
                mss.tools.to_png(ss.rgb, ss.size, output=filename)
                if self.debug: print(f"---------\nScreenshot saved as {filename}  -  {time.strftime('%Y-%m-%d_%H-%M-%S')}")

                # Add filename to the queue for image processing
                self.image_queue.put(filename)

                index +=1

                time.sleep(self.interval)

# Send to openAI

if __name__ == '__main__':
    runner = Runner(5 ,True)
    runner.cc_aocr()
