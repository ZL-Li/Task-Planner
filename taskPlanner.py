import sys
from searchGeneric import Searcher, AStarSearcher
from searchProblem import Path
from cspProblem import CSP, Constraint
from cspConsistency import Search_with_AC_from_CSP


class HeuristicSearcher(AStarSearcher):
    # HeuristicSearcher is a subclass of AStarSearcher that the cost is 0
    def __init__(self, problem):
        super().__init__(problem)

    def add_to_frontier(self, path):
        value = self.problem.heuristic(path.end())
        self.frontier.add(path, value)


class CostCSP(CSP):
    # CostCSP is a subclass of CSP which adds costs
    def __init__(self, domains, constraints, costs, positions={}):
        super().__init__(domains, constraints, positions)
        self.costs = costs


class Search_with_AC_from_Cost_CSP(Search_with_AC_from_CSP):
    # Search_with_AC_from_Cost_CSP is a subclass of Search_with_AC_from_CSP which adds costs
    def __init__(self, csp):
        super().__init__(csp)

    def heuristic(self, csp):
        # heuristic function
        res = 0
        for var in csp:
            if not csp[var]:  # no solution
                return 0
            if not var.endswith('_cost'):  # var is variable rather than variable's cost
                res += min(csp[var]) + self.cons.csp.costs[var] - 1
        return res


def to_bin_const(t1, operation, t2):
    # translate the commands to binary constraints
    if operation == 'before':
        return Constraint([t1, t1 + '_cost', t2], lambda x, y, z: x + y <= z)
    if operation == 'after':
        return Constraint([t2, t2 + '_cost', t1], lambda x, y, z: x + y <= z)
    if operation == 'starts':
        return Constraint([t1, t2], lambda x, y: x == y)
    if operation == 'ends':
        return Constraint([t1, t1 + '_cost', t2, t2 + '_cost'], lambda x, y, p, q: x + y == p + q)
    if operation == 'meets':
        return Constraint([t1, t1 + '_cost', t2], lambda x, y, z: x + y == z)
    if operation == 'overlaps':
        return Constraint([t1, t1 + '_cost', t2, t2 + '_cost'], lambda x, y, p, q: x < p and x + y > p and x + y < p + q)
    if operation == 'during':
        return Constraint([t1, t1 + '_cost', t2, t2 + '_cost'], lambda x, y, p, q: x > p and x + y < p + q)
    if operation == 'equals':
        return Constraint([t1, t1 + '_cost', t2, t2 + '_cost'], lambda x, y, p, q: x == p and y == q)


def to_una_const1(t, operation, d):
    # translate the commands to unary constraints(first four)
    d = int(d)
    if operation == 'starts-before':
        return Constraint([t], lambda x: x <= d)
    if operation == 'starts-after':
        return Constraint([t], lambda x: x >= d)
    if operation == 'ends-before':
        return Constraint([t, t + '_cost'], lambda x, y: x + y - 1 <= d)
    if operation == 'ends-after':
        return Constraint([t, t + '_cost'], lambda x, y: x + y - 1 >= d)


def to_una_const2(t, operation, d1, d2):
    # translate the commands to unary constraints(last three)
    d1 = int(d1)
    d2 = int(d2)
    if operation == 'starts-in':
        return Constraint([t], lambda x: x >= d1 and x <= d2)
    if operation == 'ends-in':
        return Constraint([t, t + '_cost'], lambda x, y: x + y - 1 >= d1 and x + y - 1 <= d2)
    if operation == 'between':
        return Constraint([t, t + '_cost'], lambda x, y: x >= d1 and x + y - 1 <= d2)


def temporalPlanner(file):
    # the main function
    domains = {}
    constraints = []
    costs = {}
    dom0 = {i for i in range(0, 100)}

    with open(file) as f:  # read the file
        for line in f:
            line_list = line.split()
            if line.startswith('task'):
                domains[line_list[1]] = dom0
                # add cost to variables
                domains[line_list[1] + '_cost'] = [int(line_list[2])]
                costs[line_list[1]] = int(line_list[2])
            if line.startswith('constraint'):
                constraints.append(
                    to_bin_const(line_list[1], line_list[2], line_list[3]))
            if line.startswith('domain'):
                if line_list[2] not in ['starts-in', 'ends-in', 'between']:
                    constraints.append(
                        to_una_const1(line_list[1], line_list[2], line_list[3]))
                else:
                    constraints.append(
                        to_una_const2(line_list[1], line_list[2], line_list[3], line_list[4]))

    if not constraints:  # no constraints
        count = 0
        for key, value in costs.items():
            print(key + ':0')
            count += value - 1
        print('cost:' + str(count))

    else:  # constraints exist
        csp = CostCSP(domains, constraints, costs)

        searcher = HeuristicSearcher(Search_with_AC_from_Cost_CSP(csp))
        searcher.max_display_level = 0
        res = searcher.search()
        if res:  # solution exists
            res = res.end()
            for key, value in res.items():
                if not key.endswith('_cost'):
                    print(key + ':' + str(list(value)[0]))
            print('cost:' + str(Search_with_AC_from_Cost_CSP(csp).heuristic(res)))
        else:  # No solution
            print('No solution')


if __name__ == "__main__":
    temporalPlanner(sys.argv[1])
