import time
import threading
from datetime import datetime

t_cycle = 50  # ms

class ThreadApplication(threading.Thread):

    def __init__(self, gui):
        ''' Threading class for GUI. '''
        self.gui = gui
        threading.Thread.__init__(self)

    def run(self):
        ''' Updates the thread. '''
        while(True):
            print 'threading'
            start_time = datetime.now()
            self.gui.updGUI.emit()
            end_time = datetime.now()
            dt = end_time - start_time
            dtms = ((dt.days * 24 * 60 * 60 + dt.seconds) * 1000
                + dt.microseconds / 1000.0)

            if(dtms < t_cycle):
                time.sleep((t_cycle - dtms) / 1000.0);
