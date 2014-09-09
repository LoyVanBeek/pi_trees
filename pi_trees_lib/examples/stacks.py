#! /usr/bin/env python
import sys
sys.path.append("../src") #the examples folder is not in the right folder for the import to work out of the box.

# pi_trees package
from pi_trees_lib.pi_trees_lib import *

import time

#This is the global belief state of the robot. Initially, it believes that there are 10 orders, whatever that means. 
beliefs = {'orders':range(10)}

class Stacks():
    def __init__(self):
        # The root node
        ROOT_NODE = Sequence("ROOT_NODE")
        
        with ROOT_NODE.add(Sequence("stacks")) as stacks:
            with stacks.add(RepeatUntilFail(Sequence("CHECK_AND_POP"))) as _while:
                passthrough = {}
                _while += Generate('generate', (i for i in range(10)), passthrough) 
                #Pop something from 'orders in the global belief state and temporatily store it in the passthrough
                # _while += Pop('pop', 'orders', passthrough) 
                _while += Print('print', passthrough) #Print whatever is stored in the passthough for us.

        
        # Print a simple representation of the tree
        print "Behavior Tree Structure"
        print_tree(ROOT_NODE)

        print "\n\n Starting ROOT_NODE"
        # Run the tree
        while True:
            status = ROOT_NODE.run()
            time.sleep(0.5)
            if status == TaskStatus.SUCCESS:
                print "Finished running tree."
                break

class Pop(Task):
    """Takes some value from the global belief state and stores it in passthrough['temp']"""
    def __init__(self, name, key, passthrough):
        super(Pop, self).__init__(name)
        self.key = key
        self.passthrough = passthrough

    def run(self):
        global beliefs
        try:
            print "Stack: {0}".format(beliefs)
            self.passthrough["temp"] = beliefs[self.key].pop()
            return TaskStatus.SUCCESS
        except:
            return TaskStatus.FAILURE

class Generate(Task):
    """Stores 'generator.next()' in passthrough['temp'] and returns SUCCESS or FAILURE on StopIteration"""
    def __init__(self, name, generator, passthrough):
        super(Generate, self).__init__(name)
        self.generator = generator
        self.passthrough = passthrough

    def run(self):
        try:
            current_value = self.generator.next()
            print "{0.name}: Putting {1} in 'temp'".format(self, current_value)
            self.passthrough["temp"] = current_value
            return TaskStatus.SUCCESS
        except StopIteration:
            return TaskStatus.FAILURE

class Print(Task):
    """Prints wehatever is stored in passthrough['temp']"""
    def __init__(self, name, passthrough):
        super(Print, self).__init__(name)
        self.passthrough = passthrough

    def run(self):
        print "{0.name}: Retrieving {1} from 'temp'".format(self, self.passthrough["temp"])
        print self.passthrough["temp"]

        return TaskStatus.SUCCESS

class RepeatUntilFail(Task):
    """ Inspired by http://www.gamasutra.com/blogs/ChrisSimpson/20140717/221339/Behavior_trees_for_AI_How_they_work.php
    Like a repeater, these decorators will continue to reprocess their child. 
    That is until the child finally returns a failure, at which point the repeater will return success to its parent.
    """
    def __init__(self, task):
        super(RepeatUntilFail, self).__init__(task.name+"repeat_until_fail")
        self.children = [task]
 
    def run(self):
        result = self.children[0].run()
        if result != TaskStatus.FAILURE:
            return TaskStatus.RUNNING
        else:
            return TaskStatus.SUCCESS

    def add_child(self, c):
        self.children[0].add_child(c)

    def remove_child(self, c):
        self.children[0].remove_child(c)
        
    def prepend_child(self, c):
        self.children[0].prepend_child(0, c)
        
    def insert_child(self, c, i):
        self.children[0].insert_child(i, c)

if __name__ == '__main__':
    tree = Stacks()