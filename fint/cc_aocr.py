import os
import time
import mss
import pytesseract
from display import add_macOS
from PIL import Image
from multiprocessing import Process, Queue
from multiSS import capture

# Function to perform OCR on the captured image in a separate process
def process_image(queue):
    pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
    while True:
        # Wait for an image filename from the main process
        filename = queue.get()
        if filename is None:
            break  # Exit the loop if None is received, signaling the end of the program

        # Perform OCR on the image
        ocr = pytesseract.image_to_string(Image.open(filename))
        print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')}: Processed OCR for {filename}\n{ocr}\n")

# The modified cc_ocr function
def cc_ocr(interval, debug=False):
    if debug: print('DEBUGGING ENABLED')

    # Create directory for this sessions screenshots
    parent = os.path.dirname(os.path.abspath(__file__))
    directory = os.path.join(parent, f'screenshots/test_{time.strftime("%Y-%m-%d_%H-%M-%S")}')
    os.makedirs(directory, exist_ok=True) # Check if directory exists, create if not

    # Create a Queue for communication between main process and OCR process
    queue = Queue()
    ocr_process = Process(target=process_image, args=(queue,))
    ocr_process.start()

    index = 0
    while True:
        # Get the geometry of the active window
        monitor = add_macOS()
        filename = f"{directory}/cwi_c{index}.png" 
        capture(monitor, filename, debug)

        # Send the filename to the OCR process for processing
        queue.put(filename)
        index += 1
        time.sleep(interval)

if __name__ == '__main__':
    cc_ocr(5, True)