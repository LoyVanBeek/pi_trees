#!/usr/bin/env python

"""
    parallel_example.py - Version 1.0 2013-09-22
    
    Perform a number of parallel counting tasks
    
    Created for the Pi Robot Project: http://www.pirobot.org
    Copyright (c) 2013 Patrick Goebel.  All rights reserved.

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details at:
    
    http://www.gnu.org/licenses/gpl.html
"""

import sys
sys.path.append("../src") #the examples folder is not in the right folder for the import to work out of the box.

from pi_trees_lib.pi_trees_lib import *
import time

class ParallelExample():
    def __init__(self):
        # The root node
        BEHAVE = Sequence("behave")
        
        # Create a ParallelOne composite task (returns SUCCESS as soon as any subtask returns SUCCESS)
        PARALLEL_TASKS = ParallelOne("Counting in Parallel")
        
        # Add the tasks to the parallel composite task existing of three counting tasks
        PARALLEL_TASKS += Count("Count+2", 1, 2, 1)
        PARALLEL_TASKS += Count("Count-5", 5, 1, -1)
        PARALLEL_TASKS += Count("Count+16", 1, 16, 1)
        
        # Add the composite task to the root task
        BEHAVE += PARALLEL_TASKS
        
        # Print a simple representation of the tree
        print "Behavior Tree Structure"
        print_tree(BEHAVE)
            
        # Run the tree
        while True:
            status = BEHAVE.run()
            if status == TaskStatus.SUCCESS:
                print "Finished running tree."
                break

# A counting task that extends the base Task task
class Count(Task):
    def __init__(self, name, start, stop, step, *args, **kwargs):
        super(Count, self).__init__(name, *args, **kwargs)
        
        self.name = name
        self.start = start
        self.stop = stop
        self.step = step
        self.count = self.start
        print "Creating task Count", self.start, self.stop, self.step
 
    def run(self):
        if abs(self.count - self.stop - self.step) <= 0:
            return TaskStatus.SUCCESS
        else:
            print self.name, self.count
            time.sleep(0.5)
            self.count += self.step
            if abs(self.count - self.stop - self.step) <= 0:
                return TaskStatus.SUCCESS
            else:
                return TaskStatus.RUNNING

    
    def reset(self):
        self.count = self.start

if __name__ == '__main__':
    tree = ParallelExample()

