import mss
import time
import os

'''
Enabled VScode to view screen
- App will need this permission
'''

# os.path.abspath() - absolute path of current script
# os.path.dirname() - parent directory of current script
parent = os.path.dirname(os.path.abspath(__file__))
ss_path = os.path.join(parent, f'screenshots/test_{time.strftime("%Y-%m-%d_%H-%M-%S")}')

# Capture a window, specify dimensions of the window to capture or it will default to the user's whole primary monitor
#   directory - file path to save files to
#   index (int) - # of times this has been called externally, for file naming
#   debug (bool) - turn on print statements
#   stamp (bool) - turn on timestamps
#   dimensions - of monitor to capture, EG dimensions =  {"top": 100, "left": 100, "width": 500, "height": 300}
def cw(directory, index, debug=False, stamp=False, dimensions=None):
    # Check if directory exists, create if not
    os.makedirs(directory, exist_ok=True)

    with mss.mss() as sct:
        monitor = dimensions if dimensions else sct.monitors[1] # What to take a picture of, dimensions on screen, or primary monitor
        filename = f"{directory}/cw_c{index}_{time.strftime('%Y-%m-%d_%H-%M-%S')}.png"  # where to save to

        # Capture the monitor
        ss = sct.grab(monitor)
        mss.tools.to_png(ss.rgb, ss.size, output=filename)

        if debug: print(f"Screenshot saved as {filename}")
        if stamp: print(time.strftime("%Y-%m-%d_%H-%M-%S"))



# Capture a specified window every {interval} seconds.
#   directory - file path to save files to
#   index (int) - # of times this has been called externally, for file naming
#   interval (int) - sleep between capture
#   debug (bool) - turn on print statements
#   stamp (bool) - turn on timestamps
#   dimensions - of monitor to capture, EG dimensions =  {"top": 100, "left": 100, "width": 500, "height": 300}
def cw_interval(directory, index, interval, debug=False, stamp=False, dimensions=None):
    # Check if directory exists, create if not
    os.makedirs(directory, exist_ok=True)

    with mss.mss() as sct:
        monitor = dimensions if dimensions else sct.monitors[1]

        while True:
            filename = f"{directory}/cwi_c{index}_{time.strftime('%Y-%m-%d_%H-%M-%S')}.png" 
                
            # Capture the monitor
            ss = sct.grab(monitor)
            mss.tools.to_png(ss.rgb, ss.size, output=filename)

            if debug: print(f"Screenshot saved as {filename}")
            if stamp: print(time.strftime("%Y-%m-%d_%H-%M-%S"))

            time.sleep(interval)



# Capture all monitors
#   directory - file path to save files to
#   index (int) - # of times this has been called externally, for file naming
#   debug (bool) - turn on print statements
#   stamp (bool) - turn on timestamps
def cam(directory, index, debug=False, stamp=False): # cam - capture all monitors
    # Check if directory exists, create if not
    os.makedirs(directory, exist_ok=True)

    with mss.mss() as sct:
        # Loop through monitors
        for monitor_number, monitor in enumerate(sct.monitors[1:], start=1):  # Skip the first entry which is the aggregate of all monitors
            filename = f"{directory}/cam_c{index}_m{monitor_number}.png" 
            
            # Capture the monitor
            sct_img = sct.grab(monitor)
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)

            if debug: print(f"Screenshot saved as {filename}")
            if stamp: print(time.strftime("%Y-%m-%d_%H-%M-%S"))



# Capture all monitors ever {interval} sectionds
#   directory - file path to save files to
#   index (int) - # of times this has been called externally, for file naming
#   interval (int) - seconds of sleep between capture
#   debug (bool) - turn on print statements
#   stamp (bool) - turn on timestamps
def cam_interval(directory, index, interval, debug=False, stamp=False): # cam - capture all monitors
    # Check if directory exists, create if not
    os.makedirs(directory, exist_ok=True)

    with mss.mss() as sct:
        while True:
            # Loop through monitors
            for monitor_number, monitor in enumerate(sct.monitors[1:], start=1):  # Skip the first entry which is the aggregate of all monitors
                filename = f"{directory}/cami_c{index}_m{monitor_number}_{time.strftime('%Y-%m-%d_%H-%M-%S')}.png" 
            
                # Capture the monitor
                sct_img = sct.grab(monitor)
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)

                if debug: print(f"Screenshot saved as {filename}")
                if stamp: print(time.strftime("%Y-%m-%d_%H-%M-%S"))

            time.sleep(interval)



#######################################################__main__####################################################################
#cw_interval(ss_path, 1, 3, True, True, {"top": 100, "left": 100, "width": 500, "height": 300})
#cw_interval(ss_path, 1, 3, True, True)

#cw(ss_path, 1, True, True)

#cam(ss_path, 1)

#cam_interval(ss_path, 5, 6, True, True)
###################################################################################################################################