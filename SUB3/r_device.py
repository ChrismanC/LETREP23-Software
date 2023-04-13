from tkinter import *
from PIL import ImageTk, Image
import serial
import serial.tools.list_ports

from global_funcs import *
from r_sign_in import *

#This is the first research display screen
#it follows main.py and precedes r_sign_in.py
#the port is chosen here and passed forward

def r_device():
    #make tkinter root
    root = Tk()
    root.configure(bg="white")

    #grab the list of ports on the computer
    ports = serial.tools.list_ports.comports()
    port_names = [x[0] + ": " + x[1] for x in ports]
    #(Preston is a dummy)
    port_names.append("COM7: Dummy") 
    #the computer currently does not display the correct option automatically, so it is hardcoded here
    #this only works with Preston

    #Get the logo; resize; make it a Tkinter image
    img = Image.open(logo_dir)
    img = img.resize((250, 250), Image.ANTIALIAS)
    logo = ImageTk.PhotoImage(img)
    #Put it in a label; place the label
    logo_label = Label(root, image=logo, bg="white")
    logo_label.grid(row=0, column=0, columnspan=2)

    #Adds prompt text
    label = Label(root, text="Select device:", bg="white", font=small_font)
    label.grid(row=1, column=0)


    choice = StringVar(root) #choice.get gets the choice of port from the tkinter window
    unselected_port = "No Motor (also disables EMG)" 
    choice.set(unselected_port) #set the default as a backup

    #this button gets the port choice runs r_sign_in.py 
    # if a port is selected, it is separated from the display colon ": " before being passed
    def continue_button():
        port = choice.get()
        root.destroy()
        r_sign_in(port.split(": ")[0] if port != unselected_port else None)

    #this selector allows choice to .get() the selected port_name
    selector = OptionMenu(root, choice, choice.get(), *
                          port_names)
    selector.configure(width=30, anchor="w")
    selector.grid(row=1, column=1)

    #this button iterates the the next screen, r_sign_in.py
    cont = Button(root, text="Continue", command=continue_button,
                  width=17, height=0, bg=button_color, font=button_font, fg=button_font_color)
    cont.grid(row=3, column=0, columnspan=2, padx=padx, pady=pady)

    #center and loop
    center_window(root)
    root.mainloop()

#this file can be run directly for testing purposes. It is not main.py.
if __name__ == "__main__":
    r_device()
