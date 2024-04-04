import re
import json
import tkinter as tk
from tkinter import messagebox
from app_confirm_runability import SettingsScreen

class EnterNoNo(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Add websites you want Charlie to monitor")
        self.geometry("550x350")

        self.website_list = self.load_websites()
        
        # Text field to accept websites
        self.entry_var = tk.StringVar()
        self.entry_var.set("amazon.com")
        self.entry = tk.Entry(self, textvariable=self.entry_var, width=37)
        self.entry.bind("<FocusIn>", self.on_entry_click)
        self.entry.bind("<FocusOut>", self.on_focusout)
        self.entry.bind('<Return>', self.add_website)
        self.entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Add button
        self.add_button = tk.Button(self, text="Add Website!", command=lambda: self.add_website())
        self.add_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Create + populate scrollable area with the side bar
        SCROLL_WIDTH = 350  # Max width for the scrollable area
        SCROLL_HEIGHT = 150  # Height for the scrollable area

        self.scroll_frame = tk.Frame(self, width=SCROLL_WIDTH)
        self.scroll_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.scroll_frame.grid_propagate(False)  # Lock the frame's size

        self.scroll_canvas = tk.Canvas(self.scroll_frame, width=SCROLL_WIDTH, height=SCROLL_HEIGHT, bg="gray")  # Set a background color for visibility
        self.scrollbar = tk.Scrollbar(self.scroll_frame, orient="vertical", command=self.scroll_canvas.yview)
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollable_frame = tk.Frame(self.scroll_canvas)
        self.scroll_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scroll_frame_bg = "black"
        self.scrollable_frame.bind("<Configure>", lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all")))
        self.scrollable_frame.config(bg=self.scroll_frame_bg)

        # Pack scrollbar left
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="left", fill="y")

        self.populate_scrollbox()

        # Button to move to next screen
        self.done_button = tk.Button(self, text="Done!", command=self.switch_to_settings)
        self.done_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Make frames grow as window is expanded
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def on_entry_click(self, event):
        """Clear the entry box on focus if it's the placeholder text."""
        if self.entry_var.get() == 'amazon.com':
            self.entry.delete(0, tk.END)
            self.entry_var.set('')

    def on_focusout(self, event):
        """Repopulate placeholder if the box is empty when focus is lost."""
        if not self.entry_var.get():
            self.entry_var.set('amazon.com')

    def validate_website(self, website):
        pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        if pattern.match(website) or website.endswith('.com'):
            return True
        return False

    def add_website(self, event=None):
        website = self.entry_var.get()
        if not website:
            messagebox.showerror("Error", "Please enter a website.")
            return
        if website in self.website_list:
            messagebox.showerror("Error", "This website has already been added.")
            return
        if self.validate_website(website):
            self.website_list.append(website)
            self.save_website(website)
            self.populate_scrollbox()
            self.entry_var.set("amazon.com")
        else:
            messagebox.showerror("Error", "Invalid website. Please enter a valid URL.")

    def save_website(self, website):
        with open("nono.json", "w") as file:
            data = {"patterns": self.website_list}
            json.dump(data, file, indent=4)

    def load_websites(self):
        try:
            with open("nono.json", "r") as file:
                data = json.load(file)
                return data["patterns"]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def populate_scrollbox(self):
        """Clear and repopulate the scrollable list with websites and remove buttons."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        for website in self.website_list:

            # Then, when creating each row_frame, you would use the same background color
            row_frame = tk.Frame(self.scrollable_frame, bg=self.scroll_frame_bg)
            row_frame.pack(fill='x', expand=True, padx=15, pady=10)

            label = tk.Label(row_frame, text=website, bg=self.scroll_frame_bg)
            label.pack(side='left', padx=5)  # Adds padding on the left side of the label, acting like a margin

            remove_button = tk.Button(row_frame, text='Remove', bg=self.scroll_frame_bg, command=lambda w=website: self.remove_website(w))
            remove_button.pack(side='right', padx=10)


    def remove_website(self, website):
        """Remove a website from the list and update nono.json."""
        self.website_list.remove(website)
        self.save_website(website)  # Save the updated list to nono.json
        self.populate_scrollbox()  # Refresh the scrollable list

    def switch_to_settings(self):
        self.withdraw()  # Hide the main window
        settings_screen = SettingsScreen(self)
        settings_screen.grab_set()  # Modal focus to the settings window
        '''
        for widget in self.winfo_children():
            widget.destroy()
        self.title("Configure your settings")
        # Implement settings screen layout here as needed
        '''

if __name__ == "__main__":
    app = EnterNoNo()
    app.mainloop()
