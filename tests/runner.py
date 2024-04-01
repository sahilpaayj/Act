import os
import time
import mss
import pytesseract
from display import add_macOS
from PIL import Image

# Continuously capture active window every {interval} seconds and send to pytesseract for OCR
#   directory - file path to save files to
#   index (int) - # of times this has been called externally, for file naming
#   interval (int) - sleep between capture
#   debug (bool) - turn on print statements
def cc_ocr(directory, index, interval, debug=False):
    # Check if directory exists, create if not
    os.makedirs(directory, exist_ok=True)
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


parent = os.path.dirname(os.path.abspath(__file__))
ss_path = os.path.join(parent, f'screenshots/test_{time.strftime("%Y-%m-%d_%H-%M-%S")}')

cc_ocr(ss_path, 1, 5, True)
