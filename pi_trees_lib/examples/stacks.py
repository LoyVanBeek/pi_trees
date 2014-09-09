#! /usr/bin/env python
import sys
sys.path.append("../src") #the examples folder is not in the right folder for the import to work out of the box.

# pi_trees package
from pi_trees_lib.pi_trees_lib import *

import time

#This is the global belief state of the robot. Initially, it believes that there are 10 orders, whatever than means. 
beliefs = {'orders':range(10)}

class Stacks():
    def __init__(self):
        # The root node
        ROOT_NODE = Sequence("ROOT_NODE")
        
        with ROOT_NODE.add(Sequence("beliefss")) as beliefss:
            with beliefss.add(RepeatUntilFail(Sequence("CHECK_AND_POP"))) as until_fail_check_pop:
                passthrough = {}
                until_fail_check_pop += Pop('pop', passthrough)
                until_fail_check_pop += Print('print', passthrough)

        
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
    def __init__(self, name, passthrough):
        super(Pop, self).__init__(name)
        self.passthrough = passthrough

    def run(self):
        global beliefs
        try:
            print "Stack: {0}".format(beliefs)
            self.passthrough["to_print"] = beliefs['orders'].pop()
            return TaskStatus.SUCCESS
        except:
            return TaskStatus.FAILURE

class Print(Task):
    def __init__(self, name, passthrough):
        super(Print, self).__init__(name)
        self.passthrough = passthrough

    def run(self):
        print self.passthrough["to_print"]

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