import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import math

class GraphVisualizer:
    '''
    xStep is the length of one Step in ms. Default is 250
    xRange referes to the displayed raqnge of xValues on the x-Axis. Default is 1000
    animation_show = True shows and animates the graph imeadiately as the last step of init
    '''
    def __init__(self, x_Step=250, x_Range=10000, animation_show = False, animation_Interval = 250) -> None:
        self.x_Step = x_Step
        self.x_Range = x_Range
        self.animation_show = animation_show
        self.animation_Interval = animation_Interval

        # counts the time since the last push_step, resets if item is inserted into queue in push_step
        self.ms_since_last_push = 0 
            
        # fill initial queue and X_Value values
        self.y_queue = []
        self.x_values = []

        for x in range(0, self.x_Range, self.x_Step):
            self.y_queue.append(0)
            self.x_values.append(x)

        # setup the plot
        style.use('fivethirtyeight') # not shure if this needs to be here
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(1,1,1)

        if self.animation_show:
            self.animate()

    '''
    y_Value is the yValue of current Datapoint
    ms_Since_Last informs how much time, since previous Datapoint was pushed. If -1 its assumed to be x_Step
    '''
    def push_step(self, y_Value, ms_Since_Last = -1):
        if ms_Since_Last == -1:
            self.ms_since_last_push += self.x_Step
        else:
            self.ms_since_last_push += ms_Since_Last
        
        steps = math.floor(self.ms_since_last_push/self.x_Step)

        if steps > 0:
            self.ms_since_last_push = 0
            
            y_value_previous = self.y_queue[0]
            y_steps_value = (y_Value - y_value_previous)/steps
            for x in range(1, steps + 1):
                
                if x < steps:
                    #fill steps, that where missed linear
                    self.y_queue.pop()
                    self.y_queue.insert(0, y_value_previous + y_steps_value * x)
                else:
                    self.y_queue.pop()
                    self.y_queue.insert(0, y_Value)

    def animation_func(self, i):
        self.ax1.clear()
        self.ax1.plot(self.x_values, self.y_queue)

    '''
    animate = True shows and animates the graph, if its not animated already
    animate = False stops the animation, if the graph was already animated
    '''
    def animate(self, animate = True, interval = 250):
        style.use('fivethirtyeight')
        ani = animation.FuncAnimation(self.fig, self.animation_func, interval= interval)
        plt.show()