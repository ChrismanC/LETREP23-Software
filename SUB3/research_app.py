from tkinter import *
from PIL import ImageTk, Image
from global_funcs import *
import multiprocessing

def research_app():
    root = Tk()
    root.configure(bg="white")

    #width = 15
    #height = 5

    img = Image.open(logo_dir)
    img = img.resize((250, 250), Image.ANTIALIAS)
    logo = ImageTk.PhotoImage(img)
    logo_label = Label(root, image=logo, bg="white")
    logo_label.grid(row=0, column=0, columnspan=2)

    #def button_command():
        #root.destroy()
        #run new window
    
    #newButton = Button(root, text="newButton", command=button_command,
    #                  width=width, height=height, bg=button_color, font=button_font, fg=button_font_color)

    #newButton.grid(row=1, column=0, padx=padx, pady=pady)

    center_window(root)
    root.mainloop()