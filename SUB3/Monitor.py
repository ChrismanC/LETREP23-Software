

from time import sleep
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from emg import emg
from statistics import mean
from itertools import chain

#I have never used this file in my life
#my best guess is that it lets you display EMG in real time?
def animate(i, xs, ys):

    # Limit x and y lists to 20 items
    n1 = 2000
    n2 = 2000
    # adat = ys[1][-n1:]
    adat = [(x + 1)*.1 for x in ys[1][-n1:]]
    acc_xs = xs[0:len(adat)]

    edat = ys[0][-n2:]
    emg_xs = xs[0:len(edat)]
    ys[:] = ys[:][-n2:]

    # Draw x and y lists
    ax.clear()
    ax.plot(acc_xs, adat)

    ax.plot(emg_xs, edat)

    # Format plot
    plt.title('EMG Readings')
    plt.ylim([0, 1])


last_received = "Here we go"

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
# ay = fig.add_subplot(1, 1, 2)
xs = [i for i in range(0, 5001)]
ys = [[], []]

emg_obj = emg()
emg_obj.start_cont_collect(ys,)

try:
    ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=1)
    plt.show()
finally:
    emg_obj.exit()
    print("Good Exit")
