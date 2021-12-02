import PiDataReceiverGeneric as PDRG
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from threading import Thread
import time

pdr = PDRG.PiDataReceiverGeneric(port="COM3", send_raw_data=True, send_envlope=True, send_filtered_data=True)

for p in pdr.list_possible_ports():
    print(p)

style.use('fivethirtyeight') # not shure if this needs to be here
fig = plt.figure()
# ax0 = fig.add_subplot(1,3,1)
# ax1 = fig.add_subplot(1,3,2)
# ax2 = fig.add_subplot(1,3,3)
ax2 = fig.add_subplot(1,1,1)
x_values0 = []
x_values1 = []
x_values2 = []
y_queue = []

def threaded_function(arg):
    tt_start = time.thread_time()
    lst = pdr.read()
    if(len(lst) == 3):
        y_queue.append(0)
        x_values0.append(lst[0])
        x_values1.append(lst[1])
        x_values2.append(lst[2])
    else:
        print("bad values:")
        print(lst)
    while 1:
        lst = pdr.read()
        if(len(lst) == 3):
            y_queue.append(time.thread_time() - tt_start)
            x_values0.append(lst[0])
            x_values1.append(lst[1])
            x_values2.append(lst[2])
        else:
            print("bad values:")
            print(lst)
        

def animation_func(i):
    # ax0.clear()
    # ax0.plot(y_queue, x_values0)
    # ax1.clear()
    # ax1.plot(x_values1, y_queue)
    ax2.clear()
    ax2.plot(y_queue, x_values2)

def main():
    time.sleep(3)
    pdr.init_arduino()
    time.sleep(0.1)
    thread = Thread(target = threaded_function, args = (1, ))
    thread.start()
    ani = animation.FuncAnimation(fig, animation_func, 250)
    plt.show()
    pass
    

if __name__ == '__main__':
    main()