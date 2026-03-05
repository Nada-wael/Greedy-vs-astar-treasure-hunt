import heapq
import tkinter as tk
import time
from tkinter import messagebox


class Node:
    def __init__(self, state, parent, action, cost=0, heuristic=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.heuristic = heuristic

    def __lt__(self, other):  # heapq uses __lt__ automatically for ordering
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)


class PriorityQueue:
    def __init__(self):
        self.frontier = []

    def add(self, node):
        heapq.heappush(self.frontier, node)

    def containstate(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception('frontier is empty')
        return heapq.heappop(self.frontier)


class race:
    def __init__(self, filename):
        with open(filename) as f:
            contents = f.read()
        if contents.count('A') != 1:
            raise Exception('race must have one A agent')
        if contents.count('B') != 1:
            raise Exception('race must have one B agent')
        if contents.count('T') != 1:
            raise Exception('race must have one Treasure')
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)
        self.obstacles = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == 'A':
                        self.startA = (i, j)
                        row.append(False)
                    elif contents[i][j] == 'B':
                        self.startB = (i, j)
                        row.append(False)
                    elif contents[i][j] == 'T':
                        self.treasure = (i, j)
                        row.append(False)
                    elif contents[i][j] == '.':
                        row.append(False)
                    elif contents[i][j] == ' ':
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.obstacles.append(row)
        self.solutionA = None
        self.solutionB = None
        self.timeA = None
        self.timeB = None

    def print(self):
        solutionA = self.solutionA[1] if self.solutionA is not None else None
        solutionB = self.solutionB[1] if self.solutionB is not None else None
        print()
        for i, row in enumerate(self.obstacles):
            for j, col in enumerate(row):
                if col:
                    print('X', end='')
                elif (i, j) == self.startA:
                    print('A', end='')
                elif (i, j) == self.startB:
                    print('B', end='')
                elif (i, j) == self.treasure:
                    print('T', end='')
                elif solutionA is not None and (i, j) in solutionA:
                    print('+', end='')
                elif solutionB is not None and (i, j) in solutionB:
                    print('*', end='')
                else:
                    print('.', end='')
            print()
        print()

    def neighbors(self, state):
        row, col = state
        cells = [('up', (row - 1, col)),
                 ('down', (row + 1, col)),
                 ('left', (row, col - 1)),
                 ('right', (row, col + 1))]
        neighbors = []
        for action, (r, c) in cells:
            if 0 <= r < self.height and 0 <= c < self.width and not self.obstacles[r][c]:
                neighbors.append((action, (r, c)))
        return neighbors

    def heuristic(self, state):
        return abs(state[0] - self.treasure[0]) + abs(state[1] - self.treasure[1])

    def solveA(self):  # Greedy
        start_time = time.time()
        A = Node(self.startA, None, None, 0, self.heuristic(self.startA))
        frontier = PriorityQueue()
        frontier.add(A)
        self.exploredA = set()
        self.num_exploredA = 0
        while not frontier.empty():
            node = frontier.remove()
            self.num_exploredA += 1
            if node.state == self.treasure:
                actions, cells = [], []
                while node.parent:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solutionA = (actions, cells)
                break
            self.exploredA.add(node.state)
            for action, state in self.neighbors(node.state):
                if state not in self.exploredA and not frontier.containstate(state):
                    frontier.add(Node(state, node, action, 0, self.heuristic(state)))
        end_time = time.time()
        self.timeA = end_time - start_time

    def solveB(self):  # A*
        start_time = time.time()
        B = Node(self.startB, None, None, 0, self.heuristic(self.startB))
        frontier = PriorityQueue()
        frontier.add(B)
        best_cost = {self.startB: 0}
        self.num_exploredB = 0
        while not frontier.empty():
            node = frontier.remove()
            self.num_exploredB += 1
            if node.state == self.treasure:
                actions, cells = [], []
                while node.parent:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solutionB = (actions, cells)
                break
            best_cost[node.state] = node.cost
            for action, state in self.neighbors(node.state):
                new_cost = node.cost + 1
                if state not in best_cost or new_cost < best_cost[state]:
                    best_cost[state] = new_cost
                    heuristic_value = self.heuristic(state)
                    frontier.add(
                        Node(state=state, parent=node, action=action, cost=new_cost, heuristic=heuristic_value))
        end_time = time.time()
        self.timeB = end_time - start_time


CELL_SIZE = 40


class RaceGUI:
    def __init__(self, race_obj):
        self.race = race_obj
        self.root = tk.Tk()
        self.root.title("Treasure Hunt Race")

        self.canvas = tk.Canvas(self.root, width=self.race.width * CELL_SIZE, height=self.race.height * CELL_SIZE,
                                bg="white")
        self.canvas.pack()

        self.draw_grid()

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        greedy_btn = tk.Button(button_frame, text="Start A (Greedy)", command=lambda x='A': self.run(x))
        greedy_btn.pack(side=tk.LEFT, padx=5)
        astar_btn = tk.Button(button_frame, text="Start B (A*)", command=lambda x='B': self.run(x))
        astar_btn.pack(side=tk.LEFT, padx=5)
        first_check = tk.Button(button_frame, text="check first reached", command=lambda x='check': self.run(x))
        first_check.pack(side=tk.LEFT, padx=5)

        self.root.mainloop()

    def draw_grid(self):
        self.canvas.delete("all")
        for i in range(self.race.height):
            for j in range(self.race.width):
                x1, y1 = j * CELL_SIZE, i * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                if self.race.obstacles[i][j]:
                    color = "black"
                elif (i, j) == self.race.startA:
                    color = "red"
                elif (i, j) == self.race.startB:
                    color = "green"
                elif (i, j) == self.race.treasure:
                    color = "gold"
                else:
                    color = "white"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")

    def draw_path(self, path_cells, color):
        if path_cells is None:
            return
        for (i, j) in path_cells:
            x1, y1 = j * CELL_SIZE, i * CELL_SIZE
            x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
            self.canvas.update()
            time.sleep(0.05)

    def run(self, x):
        if x == 'A':
            self.race.solveA()
            self.draw_grid()
            self.draw_path(self.race.solutionA[1], "pink")
            message = f"Agent A explored {self.race.num_exploredA} nodes.\n\ntime taken: {self.race.timeA:.6f}"
            messagebox.showinfo("Nodes Explored & Time", message)

        if x == 'B':
            self.race.solveB()
            self.draw_grid()
            self.draw_path(self.race.solutionB[1], "lightgreen")
            message = f"Agent B explored {self.race.num_exploredB} nodes.\n\ntime taken: {self.race.timeB:.6f}"
            messagebox.showinfo("Nodes Explored & Time", message)
        if x == 'check':
            self.check_winner()

    def check_winner(self):
        try:
            time_A = self.race.timeA
            time_B = self.race.timeB
            if time_A < time_B:
                message = f'Agent A reached the Treasure first.\nTime A: {self.race.timeA:.6f}\nTime B: {self.race.timeB:.6f}'
            elif time_B < time_A:
                message = f'Agent B reached the Treasure first.\nTime B: {self.race.timeB:.6f}\nTime A: {self.race.timeA:.6f}'
            else:
                message = 'Both agents reached the Treasure at the same time.'
            messagebox.showinfo("Race Result", message)
        except TypeError:
            message = 'Please run both agents to check who reaches first the Treasure.'
            messagebox.showinfo("Race Result", message)


RaceGUI(race('race1.txt'))
