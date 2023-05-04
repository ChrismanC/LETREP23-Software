from tkinter import *

from global_funcs import *

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

#for browsing sessions, blocks, trials, in analysis
# Takes a dictionary of items and creates a listbox for them
class Browser(Listbox):
    def __init__(self, frame, height, items, browser_type="Session", child_browser=None):
        self.root = frame
        # Create parent and check if a trial browser
        super().__init__(frame, selectmode=SINGLE if browser_type in
                         ["Session", "Block", "Trial"] else MULTIPLE, height=height)
        self.items = items
        self.child_browser = child_browser

        self._load_items
        self.browser_type = browser_type


    def callback(self):
        selection = self.curselection()
        if selection:
            # Update our child with the newest data
            if self.browser_type == "Session":
                self.child_browser.update_items(
                    self.items[int(self.get(selection).split()[1])])

            elif self.browser_type == "Block":
                self.child_browser.update_items(
                    self.items[int(self.get(selection).split()[1])].trials)

            elif self.browser_type == "Trial":
                for widgets in self.root.master.plot_frame.winfo_children():
                    widgets.destroy()

                sel_trial= self.items[int(self.get(selection).split()[1])]
                # the figure that will contain the plot
                fig = Figure(figsize=(9, 5),
                            dpi=100)

                # adding the subplot
                ax = fig.add_subplot(111)

                ax.plot(sel_trial.emg_data, 'r', label="EMG")
                ax.legend(loc=2)

                ax2 = ax.twinx()
                ax2.plot(sel_trial.acc_data, 'b', label="ACC")
                ax2.legend(loc=1)

                # Format plot
                fig.legend()

                # creating the Tkinter canvas
                # containing the Matplotlib figure
                canvas = FigureCanvasTkAgg(fig,
                                           master=self.root.master.plot_frame)
                canvas.draw()

                # placing the canvas on the Tkinter window
                canvas.get_tk_widget().pack()

                # creating the Matplotlib toolbar
                toolbar = NavigationToolbar2Tk(canvas,
                                            self.root.master.plot_frame)
                toolbar.update()
                center_window(self.root.master)


    def update_items(self,new_items):
        if isinstance(new_items, list):
            new_items = {i: item for i, item in enumerate(new_items)}
        self.items = new_items
        self._load_items()

    def _load_items(self):
        self.delete(0, END)
        for key, _ in self.items.items():
            self.insert(key, f'{self.browser_type} {key}')


