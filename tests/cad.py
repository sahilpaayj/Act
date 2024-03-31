import os
import time
import mss
from display import add_linux

# Capture active window every {interval} seconds.
#   directory - file path to save files to
#   index (int) - # of times this has been called externally, for file naming
#   interval (int) - sleep between capture
#   debug (bool) - turn on print statements
#   stamp (bool) - turn on timestamps
def cad_interval(directory, index, interval, debug=False, stamp=False):
    # Check if directory exists, create if not
    os.makedirs(directory, exist_ok=True)

    with mss.mss() as sct:
        while True:
            # Get the geometry of the active window
            monitor = add_linux()
            filename = f"{directory}/cwi_c{index}_{time.strftime('%Y-%m-%d_%H-%M-%S')}.png" 
                
            # Capture the specified monitor
            ss = sct.grab(monitor)
            mss.tools.to_png(ss.rgb, ss.size, output=filename)

            if debug: print(f"Screenshot saved as {filename}")
            if stamp: print(time.strftime("%Y-%m-%d_%H-%M-%S"))

            time.sleep(interval)


parent = os.path.dirname(os.path.abspath(__file__))
ss_path = os.path.join(parent, f'screenshots/test_{time.strftime("%Y-%m-%d_%H-%M-%S")}')

cad_interval(ss_path, 1, 7, True, True)
