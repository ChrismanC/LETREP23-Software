from tkinter import *
from global_funcs import *

#this gives us widgets for the options menu

#option for floats
class FloatOption:
    def __init__(self, name, text, default_value=0):
        self.name = name
        self.text = text
        self.value = default_value
    
    def grid(self, root, row, column):
        self._lbl = Label(root, text=self.text, bg="white", font=small_font)
        self._lbl.grid(row=row, column=column, sticky="e")

        self._entry = Entry(root, width=8)
        self._entry.insert(0, str(self.value))
        self._entry.grid(row=row, column=column+1, sticky="w")

    def get_value(self):
        return float(self._entry.get())

#option for ints
class IntOption(FloatOption):
    def get_value(self):
        return int(self._entry.get())

#option for yes/no checkmarks
class BooleanOption:
    def __init__(self, name, text, default_value=False):
        self.name = name
        self.text = text
        self.value = default_value
    
    def grid(self, root, row, column):
        self._disp = BooleanVar(root)
        self._disp.set(self.value)

        self._checkbutton = Checkbutton(root, text=self.text, bg='white',
                                       variable=self._disp, onvalue=True, offvalue=False)
        self._checkbutton.grid(row=row, column=column, columnspan=2)

    def get_value(self):
        return self._disp.get()

#dropdown choice box
class DropdownOption:
    def __init__(self, name, text, dropdown_list, default_value=None):
        self.name = name
        self.text = text
        self.value = default_value if default_value else 0

        self.options = dropdown_list

    def grid(self, root, row, column):
        self._label = Label(root, text=self.text, bg="white", font=small_font)
        self._label.grid(row=row, column=column, sticky="e")

        self._choice = IntVar(root)
        self._choice.set(self.value)

        sess_selector = OptionMenu(root, self._choice, *self.options)
        sess_selector.configure(width=5, anchor="w")
        sess_selector.grid(row=row, column=column+1, sticky="w")
    
    def get_value(self):
        return self._choice.get()

#none
class NoneOption:
    def __init__(self):
        self.name = "None"
        self.value = 0

    def grid(self, root, row, column):
        pass

    def get_value(self):
        return 0