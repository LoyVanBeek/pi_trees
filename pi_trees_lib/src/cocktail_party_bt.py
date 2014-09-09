#! /usr/bin/env python
# import roslib; roslib.load_manifest("cocktail_party_bt")
# import rospy


# pi_trees package
from pi_trees_lib.pi_trees_lib import *

# other imports
import time


################################# SETUP VARIABLES ######################################


MIN_SIMULTANEOUS_ORDERS = 2   # Amigo won't fetch the drinks until he has this amount of requests
MAX_SIMULTANEOUS_ORDERS = 3   # Amigo will imediatly fetch the drinks when he has reached this amount of requests
MAX_DRINKS_SERVED       = 3   # The challenge will finish when Amigo has served this amount of requests


#########################################################################################

knowledge = {'orders':[], 'processed':[]}

class CocktailPartyBT():
    def __init__(self):
        # The root node
        ROOT_NODE = Sequence("ROOT_NODE")
        
        with ROOT_NODE.add(Sequence("COCKTAIL_PARTY")) as COCKTAIL_PARTY:
            #Problem: After taking 1 request, the TAKE_REQUEST_sl is SUCCESS, which means GET_REQUESTS_sq is SUCCES too
            #This means we move to GET_DRINKS_sq-->NAV_KITCHEN_t which takes one step and then returns RUNNING
            #Then, we go back to the top of the tree, 
            #   running the lowest level child until one returns SUCCESS or FAILURE.
            #
            #This means that once we have 1 order, we proceed to ITERATE_ORDERS, 
            #   while instead we should be taking more orders.
            #So, The GET_REQUESTS_sq should not be SUCCESS until we have enough orders


            ############## Get request from people ##############
            with COCKTAIL_PARTY.add(Sequence("GET_REQUESTS_sq")) as get_requests:
                with get_requests.add(Sequence("until enough requests")) as until:
                    until += Nav("NAV_LIVING_ROOM_t", "Living room", 3)
                    with until.add(Selector("TAKE_REQUEST_sl")) as take_requests:
                        take_requests += CheckPendingRequests("CHECK_REQ_t1", knowledge)
                        take_requests += GetPersonRequest("GET_PERSON_REQ_t", knowledge)
                    until += CheckPendingRequests("CHECK_REQ_t2", knowledge)
            
            ############## Get drinks requested ##############
            with COCKTAIL_PARTY.add(Selector("collect_drinks")) as collect_drinks:
                collect_drinks += CheckPendingOrders("CheckPendingOrders_t", knowledge)

                with collect_drinks.add(Sequence("Until enough collected")) as until:
                    with until.add(Sequence("GET_DRINKS_sq")) as get_drinks_sq:
                        get_drinks_sq += Nav("NAV_KITCHEN_t", "Kitchen", 3)
                        get_drinks_sq += FetchDrinks("FETCH_DRINK_t", knowledge)
                    until += CheckPendingOrders("CheckPendingOrders_t", knowledge)

            # with COCKTAIL_PARTY.add(RepeatUntilFail(Sequence("While"))) as foreach:
            #     seq = foreach.decorated
            #     seq += invert(CheckPendingOrders("CHECK_ORDERS_t", knowledge))
            #     seq += FetchDrinks("FETCH_DRINK_t", knowledge)
        
        # Print a simple representation of the tree
        print "Behavior Tree Structure"
        print_tree(ROOT_NODE)

        print "\n\n Starting ROOT_NODE"
            
        # Run the tree
        while True:
            status = ROOT_NODE.run()
            if status == TaskStatus.SUCCESS:
                print "Finished running tree."
                break


#########################################################################
#########################################################################

class FetchDrinks(Task):
    def __init__(self, name, knowledge, *args, **kwargs):
        super(FetchDrinks, self).__init__(name, *args, **kwargs)
        
        self.name = name
        self.count = 0
        self.knowledge = knowledge
        print "[", self.name, "]", "Creating task"
 
    def run(self):
        print "[", self.name, "]", "Run"
        time.sleep(0.5)

        order = self.knowledge['orders'].pop(0) #orders is a list, here used as a queue. Each item is a tuple
        print "Fetching a drink: a {1} for {0}".format(order[0], order[1])
        
        print "[", self.name, "]", "Return SUCCESS\n"
        self.knowledge['processed'] += order
        return TaskStatus.SUCCESS
    
    def reset(self):
        print "[", self.name, "]", "Reset"


#########################################################################

class CheckPendingRequests(Task):
    def __init__(self, name, knowledge, *args, **kwargs):
        super(CheckPendingRequests, self).__init__(name, *args, **kwargs)
        
        self.name = name
        self.knowledge = knowledge

        print "[", self.name, "]", "Creating task"
 
    def run(self):
        print "[", self.name, "]", "Run"
        time.sleep(0.5)

        drinks = self.knowledge['orders']
        processed = self.knowledge['processed']
        if len(drinks)+len(processed) < MAX_SIMULTANEOUS_ORDERS:
            print "Number of requests is not enough: {0} of {1}".format(len(drinks), MAX_SIMULTANEOUS_ORDERS)
            print "[", self.name, "]", "Return FAILURE\n"
            return TaskStatus.FAILURE
        else:
            print "Number of requests *is* enough: {0} of {1}".format(len(drinks), MAX_SIMULTANEOUS_ORDERS)
            print "[", self.name, "]", "Return SUCCESS\n"
            return TaskStatus.SUCCESS
    
    def reset(self):
        print "[", self.name, "]", "Reset"

#########################################################################

class Nav(Task):
    def __init__(self, name, destination, runtime, *args, **kwargs):
        super(Nav, self).__init__(name, *args, **kwargs)
        
        self.name = name
        self.count = 0
        self.runtime = runtime
        self.destination = destination
        print "[", self.name, "]", "Creating task"
 
    def run(self):
        print "[", self.name, "]", "Run"

        # has the robot arrived at the destination?
        if self.count < self.runtime:
            time.sleep(0.5)
            self.count += 1
            print "[", self.name, "]", "Navigating to {0}...".format(self.destination)
            print "[", self.name, "]", "Return RUNNING"
            return TaskStatus.RUNNING
        else:
            print "[", self.name, "]", "Return SUCCESS\n"
            #self.count = 0 #RESET step counter because we arrived, so prepare for next journey
            return TaskStatus.SUCCESS
    
    def reset(self):
        print "[", self.name, "]", "Reset"

#########################################################################

class GetPersonRequest(Task):
    def __init__(self, name, knowledge, *args, **kwargs):
        super(GetPersonRequest, self).__init__(name, *args, **kwargs)
        
        self.name = name
        self.knowledge = knowledge
        print "[", self.name, "]", "Creating task"
 
    def run(self):
        print "[", self.name, "]", "Run"
        
        person_name = raw_input("What is your name? ")
        person_drink = raw_input("What do you want to drink? ")
        self.knowledge["orders"] += [(person_name, person_drink)]

        print "[", self.name, "]", "{0} asked for a {1}".format(person_name, person_drink)

        print "[", self.name, "]", "Return SUCCESS\n"
        return TaskStatus.SUCCESS
    
    def reset(self):
        print "[", self.name, "]", "Reset"


#########################################################################

class CheckPendingOrders(Task):
    def __init__(self, name, knowledge, *args, **kwargs):
        super(CheckPendingOrders, self).__init__(name, *args, **kwargs)
        
        self.name = name
        self.knowledge = knowledge

        print "[", self.name, "]", "Creating task"
 
    def run(self):
        print "[", self.name, "]", "Run"
        time.sleep(0.5)

        drinks = self.knowledge['orders']
        if drinks:
            print "There are still orders to deliver: {0}".format(drinks)
            print "[", self.name, "]", "Return FAILURE\n"
            return TaskStatus.FAILURE
        else:
            print "All orders are delivered"
            print "[", self.name, "]", "Return SUCCESS\n"
            return TaskStatus.SUCCESS
    
    def reset(self):
        print "[", self.name, "]", "Reset"

#########################################################################

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
            return result

class invert(Task):
    """"""
    def __init__(self, task):
        super(invert, self).__init__(task.name+"inverted")
        self.decorated = task
 
    def run(self):
        result = self.decorated.run()
        if result == TaskStatus.FAILURE:
            return TaskStatus.SUCCESS
        elif result == TaskStatus.SUCCESS:
            return TaskStatus.FAILURE
        return result

if __name__ == '__main__':
    tree = CocktailPartyBT()