
from time import sleep
from tkinter.scrolledtext import ScrolledText
from tkinter import *
from tkinter import filedialog, messagebox
from global_funcs import *

from PIL import ImageTk, Image
from analysis_tools import *

from object_browser import Browser


class analysis_app(Tk):
    def __init__(self):
        super().__init__()
        self.title("LETREP2 Analysis")
        self.configure(bg="white")
        self.running = True

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.cbs = []
        self.sessions = {}

        # Button configuration
        self.big_w = 32
        self.big_h = 3

        self.browser_height = 20 

        # browse_button
        self.open_btn = Button(self, text="Load Sessions", command=self.on_open, width=self.big_w, height=self.big_h,
                        bg="blue", font=button_font, fg=button_font_color)
        self.open_btn.grid(row=1, column=0, padx=padx, pady=pady)

        # to csv Button
        self.csv_btn = Button(self, text="Convert all sessions to CSV", command=self.convert_to_JSON, width=self.big_w, height=self.big_h,
                        bg="blue", font=button_font, fg=button_font_color)
        self.csv_btn.grid(row=2, column=0, padx=padx, pady=pady)

        self.plot_frame = Frame(self, )
        self.plot_frame.grid(
            row=3, column=0, columnspan=4, rowspan=4, padx=padx, pady=pady+10)

        # Browser frame and widgets
        self.browser_frame = Frame(self, )
        self.browser_frame.grid(row=0, column=1, columnspan = 4, rowspan = 4, padx=padx, pady=pady)

        self.trial_browser = Browser(
            self.browser_frame, self.browser_height, {}, "Trial")
        self.trial_browser.grid(row=0, column=2, rowspan=2,
                                padx=padx, pady=pady, sticky=S)

        self.block_browser = Browser(
            self.browser_frame, self.browser_height, {}, "Block", self.trial_browser)
        self.block_browser.grid(row=0, column=1, rowspan=2,
                                padx=padx, pady=pady, sticky=S)

        self.sess_browser = Browser(
            self.browser_frame, self.browser_height, self.sessions, "Session", self.block_browser)
        self.sess_browser.grid(row=0, column=0, rowspan=2, padx=padx, pady=pady, sticky=S)

        # Add logo
        img = Image.open(logo_dir)
        img = img.resize((100, 100), Image.ANTIALIAS)
        logo = ImageTk.PhotoImage(img)
        self.logo_label = Label(self, image=logo, bg="white")
        self.logo_label.photo = logo
        self.logo_label.grid(row=0, column=0, padx=padx, pady=pady)
        
        # Window Configuration
        center_window(self)
        self.title("Analysis App")

        self.bind("<<ListboxSelect>>", self.callback)

    def callback(self, event):
        event.widget.callback()

    def on_closing(self):
        self.running = False

    def on_open(self):
        folder_name = filedialog.askdirectory(title="Select Patient Folder")
        if folder_name != "":
            
            self.sessions, multiple_patids = open_json_files(folder_name)
            
            if multiple_patids:
                messagebox.showwarning(
                    "Data Loading Error!", "Loaded Blocks Contain Differeing Patient IDs")
            
            self.sess_browser.update_items(self.sessions)
            

    def convert_to_JSON(self):
        # Save sessions to csv
        folder_name = filedialog.askdirectory(title="Select Where to Save CSV")
        for sess in self.sessions.values():
                sess_to_csv(sess, folder_name)
                messagebox.showinfo(
                    "Sessions to CSV!", f"Converted {len(self.sessions)} session(s) to csv")

    
    def run(self):
        while self.running:
            self.update()
            if self.sessions:
                self.csv_btn["state"] = "normal"
            else:
                self.csv_btn["state"] = "disabled"
        
        # Close after finished stopping
        self.destroy()

if __name__ == "__main__":

    app = analysis_app()
    app.run()
