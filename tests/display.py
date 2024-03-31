# import pygetwindow as gw
# import pyautogui
import subprocess

'''
Enabled VScode to talk to system events
- App will need this permission
'''

# Capture dimensions of the active display on linux (macOS) 
# add - active display's dimensions
def add_linux():
    # AppleScript
    script = '''
        tell application "System Events"
            set frontmostProcess to first process whose frontmost is true
            set frontmostWindow to first window of frontmostProcess
            set windowPosition to position of frontmostWindow
            set windowSize to size of frontmostWindow
            return {windowPosition, windowSize}
        end tell
    '''

    # Command line command to find the dimensions + position of the first process's front window
    output = subprocess.check_output(["osascript", "-e", script]).decode('utf-8')
    output_parts = output.strip().split(", ")
    x, y, width, height = map(int, output_parts)  # Convert each part to an integer

    return {"top": int(y), "left": int(x), "width": int(width), "height": int(height)}

add_linux()

'''
def capture_active_window():
    active_window = gw.getActiveWindow()
    if active_window:
        print(f"Active Window: {active_window.title}")
        # You might need to adjust the method for focusing on the window depending on your requirements
        active_window.activate()
        
        # Give it a moment to become active
        time.sleep(1)
        
        # Use the window's geometry to capture it
        screenshot = pyautogui.screenshot(region=(
            active_window.left,
            active_window.top,
            active_window.width,
            active_window.height
        ))
        screenshot.save(f"{active_window.title}.png")
'''
