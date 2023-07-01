"""
This file contains class declarations for:

1. CSP: a class which represents a CSP object, formatted such that it can later be solved
by the BacktrackingSearch class

2. Event: a dictionary that contains the event and its attributes, including name, id, 
tags, coordinates, and description. Individual events are actually created when the EventBulletin
class reads the json events file

3. EventBulletin: a class that contains a list (as self.events) of Event objects for each
of the events that it reads from the json events file

4. EventProfile: mainly functions as a regex reader for a txt file that takes a user txt 
profile and then gains access to the number of days someone is visiting a location, a list
of the preferred activities, and a list of their group members in general categories

5. ItinCSPCreator: initialized with an EventBulletin and an EventProfile, and has access to
both of these objects through its lifetime. Can create a basic csp from the combination of 
these objects, and then can also add on constraints using its member functions

"""

import json
import re
from typing import Dict, List, Tuple
import math

# General code for representing a weighted CSP (Constraint Satisfaction Problem).
# All variables are being referenced by their index instead of their original names
### Code and comments for the CSP class have been taken w/ small modifications from CS221
class CSP:
    def __init__(self):
        # Total number of variables in the CSP.
        self.numVars= 0

        # The list of variable names in the same order as they are added. A
        # variable name can be any hashable objects, for example: int, str,
        # or any tuple with hashtable objects.
        self.variables = []

        # Each key K in this dictionary is a variable name.
        # values[K] is the list of domain values that variable K can take on.
        self.values = {}

        # Each entry is a unary factor table for the corresponding variable.
        # The factor table corresponds to the weight distribution of a variable
        # for all added unary factor functions. If there's no unary function for
        # a variable K, there will be no entry for K in unaryFactors.
        # E.g. if B \in ['a', 'b'] is a variable, and we added two
        # unary factor functions f1, f2 for B,
        # then unaryFactors[B]['a'] == f1('a') * f2('a')
        self.unaryFactors = {}

        # Each entry is a dictionary keyed by the name of the other variable
        # involved. The value is a binary factor table, where each table
        # stores the factor value for all possible combinations of
        # the domains of the two variables for all added binary factor # functions.
        # The table is represented as a dictionary of dictionary.
        # As an example, if we only have two variables
        # A \in ['b', 'c'],  B \in ['a', 'b']
        # and we've added two binary functions f1(A,B) and f2(A,B) to the CSP,
        # then binaryFactors[A][B]['b']['a'] == f1('b','a') * f2('b','a').
        # binaryFactors[A][A] should return a key error since a variable
        # shouldn't have a binary factor table with itself.

        self.binaryFactors = {}

    def add_variable(self, var, domain: List) -> None:
        """
        Add a new variable to the CSP.
        """
        if var in self.variables:
            raise Exception("Variable name already exists: %s" % str(var))

        self.numVars += 1
        self.variables.append(var)
        self.values[var] = domain
        self.unaryFactors[var] = None
        self.binaryFactors[var] = dict()


    def get_neighbor_vars(self, var) -> List:
        """
        Returns a list of variables which are neighbors of |var|.
        """
        return list(self.binaryFactors[var].keys())

    def add_unary_factor(self, var, factorFunc) -> None:
        """
        Add a unary factor function for a variable. Its factor
        value across the domain will be *merged* with any previously added
        unary factor functions through elementwise multiplication.

        How to get unary factor value given a variable |var| and
        value from the domain |val|?
        => csp.unaryFactors[var][val]
        """
        factor = {val:float(factorFunc(val)) for val in self.values[var]}
        if self.unaryFactors[var] is not None:
            assert len(self.unaryFactors[var]) == len(factor)
            self.unaryFactors[var] = {val:self.unaryFactors[var][val] * \
                factor[val] for val in factor}
        else:
            self.unaryFactors[var] = factor

    def add_binary_factor(self, var1, var2, factor_func):
        """
        Takes two variable names and a binary factor function
        |factorFunc|, add to binaryFactors. If the two variables already
        had binaryFactors added earlier, they will be *merged* through element
        wise multiplication.

        How to get binary factor value given a variable |var1| with value |val1|
        and variable |var2| with value |val2|?
        => csp.binaryFactors[var1][var2][val1][val2]
        """
        # never shall a binary factor be added over a single variable
        try:
            assert var1 != var2
        except:
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print('!! Tip:                                                                      !!')
            print('!! You are adding a binary factor over a same variable...                    !!')
            print('!! Please check your code and avoid doing this.                              !!')
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            raise

        self.update_binary_factor_table(var1, var2,
            {val1: {val2: float(factor_func(val1, val2)) \
                for val2 in self.values[var2]} for val1 in self.values[var1]})
        self.update_binary_factor_table(var2, var1, \
            {val2: {val1: float(factor_func(val1, val2)) \
                for val1 in self.values[var1]} for val2 in self.values[var2]})

    def update_binary_factor_table(self, var1, var2, table):
        """
        Private method you can skip for 0c, might be useful for 1c though.
        Update the binary factor table for binaryFactors[var1][var2].
        If it exists, element-wise multiplications will be performed to merge
        them together.
        """
        if var2 not in self.binaryFactors[var1]:
            self.binaryFactors[var1][var2] = table
        else:
            currentTable = self.binaryFactors[var1][var2]
            for i in table:
                for j in table[i]:
                    assert i in currentTable and j in currentTable[i]
                    currentTable[i][j] *= table[i][j]

# Contains a dict of event attributes
class Event:
    def __init__(self, info: Dict):
        self.__dict__.update(info)

# Takes the json event file and transform to listing of Event objects
class EventBulletin:
    def __init__(self, eventsPath: str):

        self.events = {}
        listform = json.loads(open(eventsPath).read())
        for eventInfo in list(listform.values()):
            event = Event(eventInfo)
            self.events[event.id] = event

# This modified profile class generates the profile object from a flask form
class ProvidedProfile:
    def __init__(self, days: int, prefs: list, cost: int):
        self.days = days
        self.prefs = prefs
        self.cost = cost

# This takes an EventBulletin object and an EventProfile object and turns it into a CSP, 
# for which we can also use this class to add contraints
class ItinCSPConstructor:
    def __init__(self, bulletin: EventBulletin, profile: ProvidedProfile):
        """
        Saves the necessary data.

        @param bulletin: The listings of all the events
        @param profile: the user's profile and preferences
        """

        self.bulletin = bulletin  # We have access to a dictionary of events, where we address an event by it's id. For each event, we have access to its id, description, name, and tags
        self.profile = profile  # We have access to num days someone is traveling, a list of their preferences, and a list of their group members

        self.vars = []
        for i in range(1, self.profile.days + 1):  # Can I just access these properties out of the box? Probably
            for j in range(1, 4):
                time = "day"+str(i)+"num"+str(j)
                self.vars.append(time)


    def add_variables(self, csp: CSP) -> None:
        """
        Given the CSP, which would be created by the calling function before this
        function call, add the variables onto the CSP. The variables are named by
        their place in the itinerary: there are 3 events per day, so the slot for 
        the 3rd activity on the 2nd day would be called 'day2num3'. The domain for
        each variable is the entirety of the event listings

        @param csp: The CSP where the additional constraints will be added to.
        """
        for var in self.vars:
            csp.add_variable(var, list(self.bulletin.events.keys()))

    def add_nonrepeating_constraint(self, csp: CSP):
        """
        This is a hard constraint that ensures someone no itinerary should have the
        same event twice, anywhere        
        """

        for var1 in self.vars:
            for var2 in self.vars:
                if var1 != var2:
                    csp.add_binary_factor(var1, var2, lambda event1, event2: event1 != event2)

    def add_preference_factor(self, csp: CSP):
        """
        Adds a unary factor that multiplies the weighting of a particular event assignment
        by how much the user's activity preferences overlap with the event assignment
        
        """

        def pref(event):  # Can later find the max weight and then limit other factors by that
            weight = 1
            overlap = len(set(self.profile.prefs) & set(self.bulletin.events[event].tags))  # check that event is a string and we're accessing items properly
            weight += overlap
            return weight

        for var in self.vars:
            csp.add_unary_factor(var, pref)

    def add_distance_factor(self, csp: CSP):
        """
        Adds a chain factor to reward events that are close to one another. The chain does not 
        connect between days
        """

        def are_neighbors(event1, event2):  # Probably also have to calculate a max weight then normalize
            weight = math.sqrt(
                (self.bulletin.events[event1].coordinates[0] - self.bulletin.events[event2].coordinates[0])**2 + \
            (self.bulletin.events[event1].coordinates[1] - self.bulletin.events[event2].coordinates[1])**2
            )

            return 1/(weight + 1)

        [csp.add_binary_factor(self.vars[i], self.vars[i+1], are_neighbors) for i, var in enumerate(self.vars) if ((i < len(self.vars) - 1) and (not((i + 1) % 3 == 0)))]
        # The mod check on the list comprehension doesn't link the vars if they take place between different days

    def get_basic_csp(self) -> CSP:
        """
        Return a CSP that only enforces the the basic constraint that we can't do an event
        twice and the preference factors that rewards assignments that align with a user's
        interests

        @return csp: A CSP where basic variables and constraints are added.
        """

        csp = CSP()
        self.add_variables(csp)
        self.add_nonrepeating_constraint(csp)
        self.add_preference_factor(csp)
        return csp

    def add_all_additional_constraints(self, csp: CSP) -> None:
        """
        Add all additional constraints to the CSP. As of now, just adding the distance factor

        @param csp: The CSP where the additional constraints will be added to.
        """
        self.add_distance_factor(csp)

class HotelCSPConstructor:
    def __init__(self, bulletin: EventBulletin, profile: ProvidedProfile):
        self.bulletin = bulletin
        self.profile = profile

    def add_cost_constraint(self, csp: CSP):
        def cost(hotel):
            if self.bulletin.events[hotel].cost == self.profile.cost:
                return 2
            elif abs(self.bulletin.events[hotel].cost - self.profile.cost) == 1:
                return 1
            else: 
                return 0

        csp.add_unary_factor("choice", cost)

    def add_good_constraint(self, csp: CSP):
        csp.add_unary_factor("choice", lambda x: self.bulletin.events[x].score/3)

    def get_basic_csp(self) -> CSP:
        csp = CSP()
        csp.add_variable("choice", list(self.bulletin.events.keys()))
        return csp

    def add_constraints(self, csp: CSP):
        self.add_cost_constraint(csp)
        self.add_good_constraint(csp)

