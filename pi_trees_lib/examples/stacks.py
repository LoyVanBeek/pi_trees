#! /usr/bin/env python
import sys
sys.path.append("../src") #the examples folder is not in the right folder for the import to work out of the box.

# pi_trees package
from pi_trees_lib.pi_trees_lib import *

import time

stack = {'orders':range(10)}

class Stacks():
    def __init__(self):
        # The root node
        ROOT_NODE = Sequence("ROOT_NODE")
        
        with ROOT_NODE.add(Sequence("stacks")) as stacks:
            with stacks.add(RepeatUntilFail(Sequence("CHECK_AND_POP"))) as until_fail_check_pop:
                passthrough = {}
                until_fail_check_pop += Pop('pop', passthrough)
                until_fail_check_pop += Print('print', passthrough)

        
        # Print a simple representation of the tree
        print "Behavior Tree Structure"
        print_tree(ROOT_NODE)

        print "\n\n Starting ROOT_NODE"
            
        import ipdb; ipdb.set_trace()
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
        global stack
        try:
            print "Stack: {0}".format(stack)
            self.passthrough["to_print"] = stack['orders'].pop()
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
        self.decorated = task
 
    def run(self):
        result = self.decorated.run()
        if result != TaskStatus.FAILURE:
            return TaskStatus.RUNNING
        else:
            return TaskStatus.SUCCESS

    def add_child(self, c):
        self.decorated.children.append(c)

if __name__ == '__main__':
    tree = Stacks()