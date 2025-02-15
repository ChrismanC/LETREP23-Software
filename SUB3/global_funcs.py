#this contains a few misc functions and variables which are used throughout the code.

 #center_window... centers the window.
def center_window(toplevel):
    toplevel.update_idletasks()

    screen_width = toplevel.winfo_screenwidth()
    screen_height = toplevel.winfo_screenheight()

    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = screen_width/2 - size[0]/2
    y = screen_height/2 - size[1]/2

    toplevel.geometry("+%d+%d" % (x, y))

#these define button variables... somewhere. App, probably?
button_color = "blue"
button_font = ("Arial", 15)
small_font = ("Arial", 10)
large_font = ("Arial", 20)
button_font_color = "white"
padx = 10
pady = 10

#unsure if this logo_dir is used
logo_dir = "C:/Program Files/LETREP2/resources/Logo.jpg"
