import mss
import time
import os

# os.path.abspath() - absolute path of current script
# os.path.dirname() - parent directory of current script
parent = os.path.dirname(os.path.abspath(__file__))
ss_path = os.path.join(parent, f'screenshots/test_{time.strftime("%Y-%m-%d_%H-%M-%S")}')

# os.makedirs() - check if directory exists, create not
os.makedirs(ss_path, exist_ok=True)

def capture_all_monitors(directory, index, debug, timestamp):
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    with mss.mss() as sct:
        for monitor_number, monitor in enumerate(sct.monitors[1:], start=1):  # Skip the first entry which is the aggregate of all monitors
            filename = f"{directory}/cam_c{index}_m{monitor_number}.png" # Cam - capture all monitors
            
            # Capture the monitor
            sct_img = sct.grab(monitor)
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)
            if debug: print(f"Screenshot saved as {filename}")
            if timestamp: print(time.strftime("%Y-%m-%d_%H-%M-%S"))


capture_all_monitors(ss_path, 1, True, True)