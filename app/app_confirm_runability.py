import tkinter as tk
import subprocess
from tkinter import messagebox
from app_run import run

class SettingsScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Configure your settings")
        self.geometry("550x350")

        # Question 1: Are you using a Mac?
        self.mac_var = tk.BooleanVar()
        self.mac_question_label = tk.Label(self, text="Are you using a Mac?")
        self.mac_question_label.pack()

        self.mac_yes_button = tk.Radiobutton(self, text="Yes", variable=self.mac_var, value=True)
        self.mac_yes_button.pack()

        self.mac_no_button = tk.Radiobutton(self, text="No", variable=self.mac_var, value=False, command=self.check_compatibility)
        self.mac_no_button.pack()

        # Question 2: Have you added all your websites?
        self.websites_var = tk.BooleanVar()
        self.websites_question_label = tk.Label(self, text="Have you added all your websites?")
        self.websites_question_label.pack()

        self.websites_yes_button = tk.Radiobutton(self, text="Yes", variable=self.websites_var, value=True)
        self.websites_yes_button.pack()

        self.websites_no_button = tk.Radiobutton(self, text="No", variable=self.websites_var, value=False)
        self.websites_no_button.pack()

        # Start Monitoring Button (initially disabled)
        self.start_monitoring_button = tk.Button(self, text="Start Monitoring + Close Window", command=self.on_close, state=tk.DISABLED)
        self.start_monitoring_button.pack()

        # Check button states to enable the start button if conditions are met
        self.mac_yes_button['command'] = self.check_conditions
        self.websites_yes_button['command'] = self.check_conditions

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def check_compatibility(self):
        messagebox.showerror("Unsupported OS", "Sorry, we only support Mac at this time.")
        self.start_monitoring_button['state'] = tk.DISABLED  # Keep the button disabled

    def check_conditions(self):
        if self.mac_var.get() and self.websites_var.get():
            self.start_monitoring_button['state'] = tk.NORMAL  # Enable the button
        else:
            self.start_monitoring_button['state'] = tk.DISABLED  # Keep the button disabled

    def on_close(self):
        if self.start_monitoring_button['state'] == tk.NORMAL :
            subprocess.Popen(["python3.11", "app_run.py"])
        self.destroy()  # Destroy the window
        self.master.destroy()  # Close the main application window too


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Optionally hide the root window
    settings = SettingsScreen(root)
    root.mainloop()
