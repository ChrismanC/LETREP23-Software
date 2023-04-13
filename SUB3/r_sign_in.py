from tkinter import *
from PIL import ImageTk, Image

from global_funcs import *
from r_max import r_max

#this is the second research display screen
#it follows r_device and precedes r_max
#the ID and session are chosen here and passed forward

def r_sign_in(port):
    #display port being used to console
    print("Using PORT %s" % port) if port else print("No port selected")
    #make tkinter root
    root = Tk()
    root.configure(bg="white")

    #define button function
    #this button gets the ID text; gets the session chosen by user; and replaces the existing window with r_max
    #it passes information collected so far to r_max
    def continue_button(event=None):
        id = int(id_text.get("1.0", "end"))
        sess = sess_choice.get()
        root.destroy()
        no = port == None
        r_max(port, id, sess, no_motor=no, no_emg=no)

    #get logo, make the logo a tkinter image, put it in the window via a Label
    img = Image.open(logo_dir)
    img = img.resize((250, 250), Image.ANTIALIAS)
    logo = ImageTk.PhotoImage(img)
    logo_label = Label(root, image=logo, bg="white")
    logo_label.grid(row=0, column=0, columnspan=2, padx=padx, pady=pady)

    #display patient ID prompt text
    id_label = Label(root, text="Patient ID:", bg="white", font=small_font)
    id_label.grid(row=1, column=0, sticky="e")

    #makes a little text box for data entry
    id_text = Text(root, width=8, height=1)
    id_text.bind('<Return>', continue_button) #if you hit enter, you hit the continue button
    id_text.grid(row=1, column=1, sticky="w")

    #display session number prompt text
    sess_label = Label(root, text="Session Number:",
                       bg="white", font=small_font)
    sess_label.grid(row=2, column=0, sticky="e")

    #sess_choice allows you to .get() the session choice; the default is 1
    sess_choice = IntVar(root)
    sess_choice.set(1)

    #makes a list of values from 2 to 16
    sess_list = range(2, 16) 
    #make a dropdown menu for those values
    sess_selector = OptionMenu(
        root, sess_choice, sess_choice.get(), *sess_list)
    sess_selector.configure(width=7, anchor="w")
    sess_selector.grid(row=2, column=1, sticky="w")

    #makes the button which runs the function defined above
    cont = Button(root, text="Continue", command=continue_button,
                  width=17, height=0, bg=button_color, font=button_font, fg=button_font_color)
    cont.grid(row=3, column=0, columnspan=2, padx=padx, pady=pady)

    #center and loop
    center_window(root)
    root.mainloop()

#this file can be run without port/etc for testing. However, it is not main.py and does not run the project overall.
if __name__ == "__main__":
    r_sign_in(None)
