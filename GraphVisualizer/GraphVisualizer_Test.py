import GraphVisualizer
import time
from threading import Thread

def threaded_function(arg):
    y = -1
    while 1:
        y = y*(-1)
        time.sleep(2)
        gv.push_step(y, 2000)

gv = GraphVisualizer.GraphVisualizer()

def main():
    thread = Thread(target = threaded_function, args = (1, ))
    thread.start()
    gv.animate(interval = 250)
    

if __name__ == '__main__':
    main()