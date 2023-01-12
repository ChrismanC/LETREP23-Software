from tkinter import *
from PIL import ImageTk, Image
from global_funcs import *
import multiprocessing
from time import sleep
import os


from analysis_app import analysis_app
from research_app import research_app

def show_main():
    root = Tk()
    root.configure(bg="white")

    def analysis_command():
        root.destroy()
        app = analysis_app()
        app.run()

    def collection_button():
        from select_device import select_device
        root.destroy()
        select_device()

    def research_button():
        root.destroy()
        research_app()

    width = 15
    height = 5

    img = Image.open(logo_dir)
    img = img.resize((250, 250), Image.ANTIALIAS)
    logo = ImageTk.PhotoImage(img)
    logo_label = Label(root, image=logo, bg="white")
    logo_label.grid(row=0, column=0, columnspan=3, padx=padx, pady=pady)

    analysis = Button(root, text="Analysis", command=analysis_command,
                      width=width, height=height, bg=button_color, font=button_font, fg=button_font_color)
    collection = Button(root, text="Collection", command=collection_button,
                        width=width, height=height, bg=button_color, font=button_font, fg=button_font_color)
    research = Button(root, text="Research", command=research_button,
                        width=width, height=height, bg=button_color, font=button_font, fg=button_font_color)
    analysis.grid(row=1, column=0, padx=padx, pady=pady)
    collection.grid(row=1, column=1, padx=padx, pady=pady)
    research.grid(row=1, column=2, padx=padx, pady=pady)

    center_window(root)
    root.mainloop()

    # 


#
#

if __name__ == "__main__":
    multiprocessing.freeze_support()

    show_main()
