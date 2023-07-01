### NOTE: This is not all my (Aadi's) code. I borrowed aspects of the BacktrackingSearch
### class, including reset_results, print_stats, get_delta_weight, solve, and backtrack
### from CS221, albeit with some small modifications

"""
This file contains the BacktrackingSearch class declaration:

We start with the solve method. This is the primary function of the class as it
solves the CSP. Within the solve method, we have:

    1. reset_results: initializes several properties including self.optimalAssignment,
    self.optimalWeight, self.allAssignments, etc.

    2. backtrack: a recursive search algorithm. First, checks if we have found a solution
    (a.k.a., have assigned all the variables) and sees if that solution is optimal. If not, 
    we use get_unassigned_variable to receive a var in the csp that hasn't been assigned yet,
    we assign it to a value in the domain, and then we recurse

    3. print_stats: just outputs the optimal solution that was found, some information about
    stats for solving for that solution, or alternatively, that no solution was found

"""

from logic.cspSetup import CSP
from typing import Dict, List
import copy

class BacktrackingSearch:
    def reset_results(self) -> None:
        """
        This function resets the statistics of the different aspects of the
        CSP solver. We will be using the values here for grading, so please
        do not make any modification to these variables.
        """
        # Keep track of the best assignment and weight found.
        self.optimalAssignment = {}
        self.optimalWeight = 0

        # Keep track of the number of optimal assignments and assignments. These
        # two values should be identical when the CSP is unweighted or only has binary
        # weights.
        self.numOptimalAssignments = 0
        self.numAssignments = 0

        # Keep track of the number of times backtrack() gets called.
        self.numOperations = 0

        # Keep track of the number of operations to get to the very first successful
        # assignment (doesn't have to be optimal).
        self.firstAssignmentNumOperations = 0

        # List of all solutions found.
        self.allAssignments = []
        self.allOptimalAssignments = []

    def print_stats(self) -> None:
        """
        Prints a message summarizing the outcome of the solver.
        """
        if self.optimalAssignment:
            print(f'Found {self.numOptimalAssignments} optimal assignments \
                    with weight {self.optimalWeight} in {self.numOperations} operations')
            print(
                f'First assignment took {self.firstAssignmentNumOperations} operations')
            print(
                self.optimalAssignment
            )
        else:
            print(
                "No consistent assignment to the CSP was found. The CSP is not solvable.")

    def get_delta_weight(self, assignment: Dict, var, val) -> float:
        """
        Given a CSP, a partial assignment, and a proposed new value for a variable,
        return the change of weights after assigning the variable with the proposed
        value.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param var: name of an unassigned variable.
        @param val: the proposed value.

        @return w: Change in weights as a result of the proposed assignment. This
            will be used as a multiplier on the current weight.
        """
        assert var not in assignment
        w = 1.0
        if self.csp.unaryFactors[var]:
            w *= self.csp.unaryFactors[var][val]
            if w == 0:
                return w
        for var2, factor in list(self.csp.binaryFactors[var].items()):
            if var2 not in assignment:
                continue  # Not assigned yet
            w *= factor[val][assignment[var2]]
            if w == 0:
                return w
        return w

    def solve(self, csp: CSP, mcv: bool = True, ac3: bool = True) -> None:
        """
        Solves the given weighted CSP using heuristics as specified in the
        parameter. Note that unlike a typical unweighted CSP where the search
        terminates when one solution is found, we want this function to find
        all possible assignments. The results are stored in the variables
        described in reset_result().

        @param csp: A weighted CSP.
        @param mcv: When enabled, Most Constrained Variable heuristics is used.
        @param ac3: When enabled, AC-3 will be used after each assignment of an
            variable is made.
        """
        # CSP to be solved.
        self.csp = csp

        # Set the search heuristics requested asked.
        self.mcv = mcv
        self.ac3 = ac3

        # Reset solutions from previous search.
        self.reset_results()

        # The dictionary of domains of every variable in the CSP.
        self.domains = {
            var: list(self.csp.values[var]) for var in self.csp.variables}

        # Perform backtracking search.
        self.backtrack({}, 0, 1)
        # Print summary of solutions.
        # self.print_stats()
        return self.optimalAssignment

    def backtrack(self, assignment: Dict, numAssigned: int, weight: float) -> None:
        """
        Perform the back-tracking algorithms to find all possible solutions to
        the CSP.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param numAssigned: Number of currently assigned variables
        @param weight: The weight of the current partial assignment.
        """

        self.numOperations += 1
        assert weight > 0
        if numAssigned == self.csp.numVars:
            # A satisfiable solution have been found. Update the statistics.
            self.numAssignments += 1
            newAssignment = {}
            for var in self.csp.variables:
                newAssignment[var] = assignment[var]
            self.allAssignments.append(newAssignment)

            if len(self.optimalAssignment) == 0 or weight >= self.optimalWeight:
                if weight == self.optimalWeight:
                    self.numOptimalAssignments += 1
                    self.allOptimalAssignments.append(newAssignment)
                else:
                    self.numOptimalAssignments = 1
                    self.allOptimalAssignments = [newAssignment]
                self.optimalWeight = weight

                self.optimalAssignment = newAssignment
                if self.firstAssignmentNumOperations == 0:
                    self.firstAssignmentNumOperations = self.numOperations
            return

        # Select the next variable to be assigned.
        var = self.get_unassigned_variable(assignment)
        # Get an ordering of the values.
        ordered_values = self.domains[var]

        # Continue the backtracking recursion using |var| and |ordered_values|.
        if not self.ac3:
            # When arc consistency check is not enabled.
            for val in ordered_values:
                deltaWeight = self.get_delta_weight(assignment, var, val)
                if deltaWeight > 0:
                    assignment[var] = val
                    self.backtrack(assignment, numAssigned +
                                   1, weight * deltaWeight)
                    del assignment[var]
        else:
            # Arc consistency check is enabled. This is helpful to speed up 3c.
            for val in ordered_values:
                deltaWeight = self.get_delta_weight(assignment, var, val)
                if deltaWeight > 0:
                    assignment[var] = val
                    # create a deep copy of domains as we are going to look
                    # ahead and change domain values
                    localCopy = copy.deepcopy(self.domains)
                    # fix value for the selected variable so that hopefully we
                    # can eliminate values for other variables
                    self.domains[var] = [val]

                    # enforce arc consistency
                    self.apply_arc_consistency(var)

                    self.backtrack(assignment, numAssigned +
                                   1, weight * deltaWeight)
                    # restore the previous domains
                    self.domains = localCopy  # kind of like backtracking on steroids since we're removing all of the lookahead assignments we did
                    del assignment[var]

    def get_unassigned_variable(self, assignment: Dict):
        """
        Given a partial assignment, return a currently unassigned variable.

        @param assignment: A dictionary of current assignment. This is the same as
            what you've seen so far.

        @return var: a currently unassigned variable. The type of the variable
            depends on what was added with csp.add_variable
        """

        if not self.mcv:
            # Select a variable without any heuristics.
            for var in self.csp.variables:
                if var not in assignment:
                    return var
        else:
            # Problem 1b
            # Heuristic: most constrained variable (MCV)
            # Select a variable with the least number of remaining domain values.
            # Hint: given var, self.domains[var] gives you all the possible values.
            #       Make sure you're finding the domain of the right variable!
            # Hint: satisfies_constraints determines whether or not assigning a
            #       variable to some value given a partial assignment continues
            #       to satisfy all constraints.
            # Hint: for ties, choose the variable with lowest index in self.csp.variables
            # BEGIN_YOUR_CODE (our solution is 13 lines of code, but don't worry if you deviate from this)
            minVal = float('inf')
            chosen = None
            for var in self.csp.variables:
                if var not in assignment:
                    counter = 0
                    for option in self.domains[var]:
                        if self.get_delta_weight(assignment, var, option) > 0:
                            counter += 1
                    if counter < minVal:
                        chosen = var
                        minVal = counter

            return chosen

    def apply_arc_consistency(self, var) -> None:
        """
        Perform the AC-3 algorithm. The goal is to reduce the size of the
        domain values for the unassigned variables based on arc consistency.

        @param var: The variable whose value has just been set.
        """

        def remove_inconsistent_values(var1, var2):
            removed = False
            # the binary factor must exist because we add var1 from var2's neighbor
            factor = self.csp.binaryFactors[var1][var2]
            for val1 in list(self.domains[var1]):
                # Note: in our implementation, it's actually unnecessary to check unary factors,
                #       because in get_delta_weight() unary factors are always checked.
                if (self.csp.unaryFactors[var1] and self.csp.unaryFactors[var1][val1] == 0) or \
                        all(factor[val1][val2] == 0 for val2 in self.domains[var2]):
                    self.domains[var1].remove(val1)
                    removed = True
            return removed

        queue = [var]
        while len(queue) > 0:
            curr = queue.pop(0)
            for neighbor in self.csp.get_neighbor_vars(curr):
                if remove_inconsistent_values(neighbor, curr):
                    queue.append(neighbor)