import subprocess

'''
Enabled VScode to talk to system events
- App will need this permission
'''

# Capture dimensions of the active display on macOS
# add - active display's dimensions
# TODO: uses z-index, captures command+F box active even if not selected
def add_macOS():
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
