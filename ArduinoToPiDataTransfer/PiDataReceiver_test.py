import PiDataReceiver as PDR
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from threading import Thread
import time

pdr = PDR.PiDataReceiver(port="COM3")

for p in pdr.list_possible_ports():
    print(p)

style.use('fivethirtyeight') # not shure if this needs to be here
fig = plt.figure()
# ax0 = fig.add_subplot(1,3,1)
# ax1 = fig.add_subplot(1,3,2)
# ax2 = fig.add_subplot(1,3,3)
ax2 = fig.add_subplot(1,1,1)


def animation_func(i):
    # ax0.clear()
    # ax0.plot(y_queue, x_values0)
    # ax1.clear()
    # ax1.plot(x_values1, y_queue)
    ax2.clear()
    ax2.plot(pdr.x_queue, pdr.y_values_send_envlope)

def main():
    ani = animation.FuncAnimation(fig, animation_func, 250)
    plt.show()
    

if __name__ == '__main__':
    main()