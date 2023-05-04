from tkinter import *
from PIL import ImageTk, Image
import serial
import serial.tools.list_ports

from global_funcs import *
from sign_in import *

#this is for selecting the port to use
#use DUMMY because the computer is a DUMMY
#since the c++ motor it doesn't auto detect correctly but hardcoding in dummy worked
#otherwise it doesnt get emg and motor right
def select_device():
    root = Tk()
    root.configure(bg="white")

    #list of ports + dummy because dummy
    ports = serial.tools.list_ports.comports()
    port_names = [x[0] + ": " + x[1] for x in ports]
    port_names.append("COM7: Dummy")

    img = Image.open(logo_dir)
    img = img.resize((250, 250), Image.ANTIALIAS)
    logo = ImageTk.PhotoImage(img)
    logo_label = Label(root, image=logo, bg="white")
    logo_label.grid(row=0, column=0, columnspan=2)

    label = Label(root, text="Select device:", bg="white", font=small_font)
    label.grid(row=1, column=0)

    choice = StringVar(root)
    unselected_port = "No Motor (also disables EMG)"
    choice.set(unselected_port)

    #on continue, sent port to sign in
    #weird flex of a way to clean the port name but ok
    def continue_button():
        port = choice.get()
        root.destroy()
        sign_in(port.split(": ")[0] if port != unselected_port else None)

    #the selector
    selector = OptionMenu(root, choice, choice.get(), *
                          port_names)
    selector.configure(width=30, anchor="w")
    selector.grid(row=1, column=1)

    cont = Button(root, text="Continue", command=continue_button,
                  width=17, height=0, bg=button_color, font=button_font, fg=button_font_color)
    cont.grid(row=3, column=0, columnspan=2, padx=padx, pady=pady)

    center_window(root)
    root.mainloop()


if __name__ == "__main__":
    select_device()
