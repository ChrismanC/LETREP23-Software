from tkinter import *
from PIL import ImageTk, Image

from global_funcs import *
from app import show_app
from baseline import show_baseline

def sign_in(port):
    print("Using PORT %s" % port) if port else print("No port selected")
    root = Tk()
    root.configure(bg="white")

    def continue_button(event=None):
        id = int(id_text.get("1.0", "end"))
        sess = sess_choice.get()
        root.destroy()
        no = port == None
        max(port, id, sess, no_motor=no, no_emg=no)

    img = Image.open(logo_dir)
    img = img.resize((250, 250), Image.ANTIALIAS)
    logo = ImageTk.PhotoImage(img)
    logo_label = Label(root, image=logo, bg="white")
    logo_label.grid(row=0, column=0, columnspan=2, padx=padx, pady=pady)

    id_label = Label(root, text="Patient ID:", bg="white", font=small_font)
    id_label.grid(row=1, column=0, sticky="e")

    id_text = Text(root, width=8, height=1)
    id_text.bind('<Return>', continue_button)
    id_text.grid(row=1, column=1, sticky="w")

    sess_label = Label(root, text="Session Number:",
                       bg="white", font=small_font)


                       
    sess_label.grid(row=2, column=0, sticky="e")

    sess_choice = IntVar(root)
    sess_choice.set(1)

    sess_list = range(2, 16)

    sess_selector = OptionMenu(
        root, sess_choice, sess_choice.get(), *sess_list)
    sess_selector.configure(width=7, anchor="w")
    sess_selector.grid(row=2, column=1, sticky="w")

    cont = Button(root, text="Continue", command=continue_button,
                  width=17, height=0, bg=button_color, font=button_font, fg=button_font_color)
    cont.grid(row=3, column=0, columnspan=2, padx=padx, pady=pady)

    center_window(root)
    root.mainloop()


if __name__ == "__main__":
    sign_in(None)
