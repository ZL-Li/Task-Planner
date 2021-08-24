# Task-Planner

## Table of Contents

- [Introduction](#introduction)
- [Implementation](#implementation)
  - [Possible Input](#possible-input)
  - [Cost](#cost)
  - [Heuristic](#heuristic)
- [Sample Input](#sample-input)
- [Sample Output](#sample-output)

## Introduction

This project concerns developing optimal solutions to planning problems for complex tasks inspired by the scenario of building a house, which requires a range of basic tasks to be performed, sometimes in sequence, sometimes in parallel, but where there are constraints between the tasks. We can assume that any number of basic tasks can be scheduled at the same time, provided all the constraints between all the tasks are satisfied. The objective is to develop a plan to finish each of the basic tasks as early as possible.

For simplicity, let us represent time as days using integers starting at 0, i.e. days are numbered 0, 1, 2, etc., up to 99. A temporal __task planning problem__ is specified as a series of basic tasks. Each task has a fixed duration in days. In addition, there can be constraints both on single tasks and between two tasks, for example, a task might have to start after day 20, or one task might have to start after another task finishes (the complete list of possible constraints is given below). A solution to a planning problem is an assignment of a start day to each of the tasks so that all the constraints are satisfied. The __objective__ of the planner is to develop a solution for any given planning problem where each task finishes soonest, i.e. the solution such that the sum of the end days over all the tasks is the lowest amongst all the possible plans that satisfy the constraints.

More technically, this project is an example of a constraint optimization problem, a problem that has constraints like a standard Constraint Satisfaction Problem (CSP), but also a cost associated with each solution. For this project, we implement a greedy algorithm to find optimal solutions to temporal task planning problems that are specified and read in from a file. However, unlike the greedy search algorithm, this greedy algorithm has the property that it is guaranteed to find an optimal solution for any temporal task planning problem (if a solution exists).

## Implementation

We use the AIPython code for constraint satisfaction and search to develop a greedy search method that uses costs to guide the search, as in heuristic search (heuristic search is the same as A∗ search where the path costs are all zero). The search will use a priority queue ordered by the values of the heuristic function that gives a cost for each node in the search. The [heuristic function](#heuristic) for use in this project is defined below. The nodes in this search are CSPs, i.e. each state is a CSP with variables, domains and the same constraints (and a cost estimate). The transitions in the state space implement domain splitting subject to arc consistency (the AIPython code implements this). A __goal state__ is an assignment of values to all variables that satisfies all the constraints. The __cost__ of a solution is the sum of the end days of the basic tasks in the plan.

A __CSP__ for this project is a set of variables representing tasks, binary constraints on pairs of tasks, and unary domain constraints on tasks. The domains for the start days of the tasks the integers from 0 to 99, and a task duration is in days > 0. The only possible values for the start and end days of a task are integers, however note that it is possible for a task to finish after day 1.  Each task name is a string (with no spaces).

We use the Python code for generic search algorithms in [searchGeneric.py](/searchGeneric.py). This code includes a class Searcher with a method search() that implements depth-first search using a list (treated as a stack) to solve any search problem (as defined in [searchProblem.py](/searchProblem.py)). For this project, we extend the AStarSearcher class that extends Searcher and makes use of a priority queue to store the frontier of the search. We order the nodes in the priority queue based on the cost of the nodes calculated using the heuristic function, but the path cost is always 0. We use this code by passing the CSP problem created from the input into a searchProblem (sub)class to make a search problem, then passing this search problem into a Searcher (sub)class that runs the search when the search() method is called on this search problem.

We use the Python code in [cspProblem.py](/cspProblem.py), which defines a CSP with variables, domains and constraints. We add costs to CSPs by extending this class to include a cost and a heuristic function h to calculate the cost. We also use the code in [cspConsistency.py](/cspConsistency.py). This code implements the transitions in the state space necessary to solve the CSP. The code includes a class Search with AC from CSP that calls a method for domain splitting. Every time a CSP problem is split, the resulting CSPs are made arc consistent (if possible). Rather than extending this class, we prefer to write a new class Search with AC from Cost CSP that has the same methods but works with over constraint optimization problems. This involves just adding costs into the relevant methods, and modifying the constructor to calculate the cost by calculating h whenever a new CSP is created.

Run the code by typing:

```
python3 taskPlanner.py input.txt > output.txt
```

### Possible Input

The possible input (tasks and constraints) are as follows:

```
# tasks with name and duration
task <name> <duration>

# binary constraints
constraint <t1> before <t2>     # t1 ends before t2 starts
constraint <t1> after <t2>      # t1 starts after t2 ends
constraint <t1> starts <t2>     # t1 and t2 start on the same day
constraint <t1> ends <t2>       # t1 and t2 end on the same day
constraint <t1> meets <t2>      # t2 starts the next day after t1 ends
constraint <t1> overlaps <t2>   # t2 starts after t1 starts and ends after t1 ends
constraint <t1> during <t2>     # t1 starts after t2 starts and ends before t2 ends
constraint <t1> equals <t2>     # t1 and t2 must be over the same interval

# domain constraints
domain <t> starts-before <d>    # t starts on or before d
domain <t> starts-after <d>     # t starts on or after d
domain <t> ends-before <d>      # t ends on or before d
domain <t> ends-after <d>       # t ends on or after d
domain <t> starts-in <d1> <d2>  # t starts in the range [d1,d2]
domain <t> ends-in <d1> <d2>    # t ends in the range [d1,d2]
domain <t> between <d1> <d2>    # t starts and finishes in the range [d1,d2]
```

### Cost

To define the cost of a solution, simply sum over the end days of all the tasks in the plan. The end day of a task is the start day of the task assigned in the solution plus the given duration of the task, minus 1. More formally, let $V$ be the set of variables (representing tasks) in the CSP and let $s_v$ be the start day of a task $v$, which has duration $d_v$, in a solution $S$. Then:

\[cost(S) = \sum_{v \in V}(s_v+d_v-1)\]

### Heuristic

In this project, we implement greedy search using a priority queue to order nodes based on a heuristic function $h$. This function must take an arbitrary CSP and return an estimate of the distance from any state $S$ to a solution. So, in contrast to a solution, each variable $v$ is associated with a set of possible values (the current domain), which here we take as the possible start days
of the task.

The heuristic estimates the cost of the best possible solution reachable from a given state $S$ by assuming each variable can be assigned a value that minimizes the end day of the task. The heuristic function sums these minimal costs over the set of all variables, similar to calculating the cost of a solution cost($S$). Let S be a CSP with variables $V$ and let the domain of $v$, written $dom(v)$, be a set of start days for $v$. Then, where the sum is over all variables $v \in V$ representing a task with duration $d_v$ as above:

\[h(S) = \sum_{v \in V} min_{s_v \in dom(v)}(s_v + d_v - 1)\]

## Sample Input

All input will be a sequence of lines defining a number of tasks, binary constraints and domain constraints, in that order. Comment lines (starting with a ‘#’ character) may also appear in the file. All input files can be assumed to be of the correct format.

Below is an example of the input form and meaning.

```
# four unconstrained tasks that are all before a final task
task wall1 10
task wall2 15
task wall3 12
task wall4 10
task roof 20

# binary constraints
constraint wall1 before roof
constraint wall2 before roof
constraint wall3 before roof
constraint wall4 before roof

# domain constraints
domain wall1 starts-after 5
domain roof starts-after 10
```

## Sample Output

Print the output to standard output as a series of lines, giving the start day for each task (in the order the tasks were defined) and the cost of the optimal solution. If the problem has no solution, print 'No solution'. When there are multiple optimal solutions, produce one of them. we set all display options in the AIPython code to 0.

The output corresponding to the above input is as follows:

```
wall1:5
wall2:0
wall3:0
wall4:0
roof:15
cost:82
```
