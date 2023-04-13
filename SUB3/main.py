from tkinter import *
from PIL import ImageTk, Image
from global_funcs import *
import multiprocessing
from time import sleep
import os


from analysis_app import analysis_app
from r_device import r_device

#Welcome to Main.py! This file runs the project as a whole.
#this screen lets you choose between analysis, research, and (data) collection.

def show_main():
    
    #Create a Tkinter root called root; this is how all screens in this project are currently implemented
    #In Tkinter, your objects need to be associated with a root window
    root = Tk()
    root.configure(bg="white") #background = "white"

    #Defines a function for use with a button, 'analysis'
    #this one destroys the current window and runs analysis_app.py
    def analysis_command():
        app = analysis_app()
        app.run()

    #The collection button replaces the current window with select_device.py
    def collection_button():
        from select_device import select_device
        root.destroy()
        select_device()

    #The research button replaces the current window with r_device.py
    def research_button():
        root.destroy()
        r_device()

    #defines all 3 button sizes equally
    width = 15
    height = 5

    #Gets the logo; sizes it; makes it a Tkinter image; 
    img = Image.open(logo_dir)
    img = img.resize((250, 250), Image.ANTIALIAS)
    logo = ImageTk.PhotoImage(img)
    #inserts it into a 'label' object; places the label on the grid
    #the grid divides rows and columns of the window into squares and places something at a coordinate
    #columnspan, here, makes the label wide
    logo_label = Label(root, image=logo, bg="white")
    logo_label.grid(row=0, column=0, columnspan=3, padx=padx, pady=pady)

    #Defines the three buttons; text, size, color, and font can be defined; 
    # buttons can run any assigned function on click;
    analysis = Button(root, text="Analysis", command=analysis_command,
                      width=width, height=height, bg=button_color, font=button_font, fg=button_font_color)
    collection = Button(root, text="Collection", command=collection_button,
                        width=width, height=height, bg=button_color, font=button_font, fg=button_font_color)
    research = Button(root, text="Research", command=research_button,
                        width=width, height=height, bg=button_color, font=button_font, fg=button_font_color)
    #place each button in the grid
    analysis.grid(row=1, column=0, padx=padx, pady=pady)
    collection.grid(row=1, column=1, padx=padx, pady=pady)
    research.grid(row=1, column=2, padx=padx, pady=pady)

    #Centers the constructed window in the middle of the screen and begins the loop
    #once the loop begins, the tkinter window will interact with the user as constructed
    center_window(root)
    root.mainloop()

    # 


#
#

if __name__ == "__main__":
    multiprocessing.freeze_support() 
    #important for multiprocessing 
    # (the C++ and python programs are multiple processes so that pipe does not hang)
    # unsure if this is where the split actually occurs

    show_main()
