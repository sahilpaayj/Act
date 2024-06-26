import subprocess
from multiSS import get_primary_screen_dimensions


'''
Enabled VScode to talk to system events
- App will need this permission
'''

# Capture dimensions of the active display on macOS
# add - active display's dimensions
# TODO: uses z-index, captures command+F box active even if not selected

def get_active_display_dimensions():
    script = '''
        tell application "System Events"
            set frontmostProcess to first application process whose frontmost is true and name is not "Finder"
            if exists (first window of frontmostProcess) then
                set frontmostWindow to first window of frontmostProcess
                set windowPosition to position of frontmostWindow
                set windowSize to size of frontmostWindow
                return {windowPosition, windowSize}
            else
                return {-1, -1, -1, -1}
            end if
        end tell
    '''
    
    try:
        # Command line command to find the dimensions + position of the first process's front window
        output = subprocess.check_output(["osascript", "-e", script]).decode('utf-8')
        if output.startswith('-1'):
            return get_primary_screen_dimensions() # raise ValueError("Could not get frontmost window dimensions.")
        
        output_parts = output.strip().split(", ")
        x, y, width, height = map(int, output_parts)
        return {"top": y, "left": x, "width": width, "height": height}
    
    except subprocess.CalledProcessError as e:
        print("Error executing AppleScript:", e)

    except ValueError as e:
        print(e)