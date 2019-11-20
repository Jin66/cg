import numpy as np
import sys


class Board:
    width = 0
    height = 0
    cells = []

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = [-1 for _ in range(width * height)]

        self.neighbors = {}
        for row in range(self.height):
            for col in range(self.width):
                self.neighbors[tuple([col, row])] = self.accessible_neighbors([col, row])

    def cell(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        return self.cells[x + y * self.width]

    def set_cell(self, x, y, value):
        self.cells[x + y * self.width] = value

    def clean(self, id_bot):
        cells = []
        for row in range(self.height):
            for col in range(self.width):
                if self.cell(col, row) == id_bot:
                    self.set_cell(col, row, -1)
                    cells.append(tuple([col, row]))
        for cell in cells:
            self.update_accessible_neighbors(cell)

    def distances_limit(self, pos, move):
        dx, dy = move
        cell_x = pos[0] + dx
        cell_y = pos[1] + dy
        distance = 0
        while self.cell(cell_x, cell_y) is not None and self.cell(cell_x, cell_y) == -1:
            cell_x += dx
            cell_y += dy
            distance += 1
        return distance

    def print(self):
        output = ""
        for i in range(self.height):
            for j in range(self.width):
                if self.cell(j, i) == -1:
                    output += "_"
                else:
                    output += str(self.cell(j, i))
            output += "\n"
        print(output)

    def accessible_neighbors(self, pos):
        neighbors = []
        if pos[0] > 0 and self.cell(pos[0] - 1, pos[1]) == -1:
            neighbors.append(tuple([pos[0] - 1, pos[1]]))
        if pos[0] < self.width - 1 and self.cell(pos[0] + 1, pos[1]) == -1:
            neighbors.append(tuple([pos[0] + 1, pos[1]]))
        if pos[1] > 0 and self.cell(pos[0], pos[1] - 1) == -1:
            neighbors.append(tuple([pos[0], pos[1] - 1]))
        if pos[1] < self.height - 1 and self.cell(pos[0], pos[1] + 1) == -1:
            neighbors.append(tuple([pos[0], pos[1] + 1]))
        return neighbors

    def update_accessible_neighbors(self, pos):
        for neighbor in self.neighbors[pos]:
            if self.cell(pos[0], pos[1]) is not -1 and self.neighbors[neighbor].__contains__(pos):
                self.neighbors[neighbor].remove(pos)
            elif not self.neighbors[neighbor].__contains__(pos):
                self.neighbors[neighbor].append(pos)

    def multiple_accessible_path(self, pos):
        closed_set = set()
        open_set = set()
        open_set.add(tuple(pos))
        g_score = {tuple(pos): 0}
        while open_set:
            current = open_set.pop()
            closed_set.add(tuple(current))
            for neighbor in self.neighbors[current]:
                if closed_set.__contains__(neighbor):
                    continue
                neighbor_g_score = g_score[current] + 1
                if not open_set.__contains__(neighbor):
                    open_set.add(neighbor)
                elif neighbor_g_score >= g_score[neighbor]:
                    continue
                g_score[neighbor] = neighbor_g_score

        return closed_set

    @staticmethod
    def build_path(position, came_from):
        path = [position]
        current = position
        while current in came_from.keys():
            current = came_from[current]
            path.append(current)
        return path


class NNBotCG:
    width = 30
    height = 20

    def __init__(self, weights):
        self.board = Board(self.width, self.height)
        self.positions = []
        self.my_id = 0
        self.nb_players = 2
        self.weights = weights  # size: 48 = 12 inputs x 4 outputs (fully connected)
        self.weights_matrix = np.reshape(self.weights, (12, 4))

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def get_next_play(self):
        # Prepare input network
        my_position = self.positions[self.my_id]

        # Distance to the closest wall
        dist_down_right = self.board.distances_limit(my_position, [1, -1])
        dist_right = self.board.distances_limit(my_position, [1, 0])
        dist_up_right = self.board.distances_limit(my_position, [1, 1])
        dist_up = self.board.distances_limit(my_position, [0, 1])
        dist_up_left = self.board.distances_limit(my_position, [-1, 1])
        dist_left = self.board.distances_limit(my_position, [-1, 0])
        dist_down_left = self.board.distances_limit(my_position, [-1, -1])
        dist_down = self.board.distances_limit(my_position, [0, -1])

        # Number of accessible cells
        closed_set_left = []
        closed_set_right = []
        closed_set_up = []
        closed_set_down = []
        if my_position[0] > 0:
            # print("Compute left")
            closed_set_left = self.board.multiple_accessible_path([my_position[0] - 1, my_position[1]])
        if my_position[0] < self.board.width - 1:
            if closed_set_left.__contains__(tuple([my_position[0] + 1, my_position[1]])):
                closed_set_right = closed_set_left
            else:
                # print("Compute right")
                closed_set_right = self.board.multiple_accessible_path([my_position[0] + 1, my_position[1]])
        if my_position[1] > 0:
            if closed_set_left.__contains__(tuple([my_position[0], my_position[1] - 1])):
                closed_set_down = closed_set_left
            elif closed_set_right.__contains__(tuple([my_position[0], my_position[1] - 1])):
                closed_set_down = closed_set_right
            else:
                # print("Compute down")
                closed_set_down = self.board.multiple_accessible_path([my_position[0], my_position[1] - 1])
        if my_position[1] < self.board.height - 1:
            if closed_set_left.__contains__(tuple([my_position[0], my_position[1] + 1])):
                closed_set_up = closed_set_left
            elif closed_set_right.__contains__(tuple([my_position[0], my_position[1] + 1])):
                closed_set_up = closed_set_right
            elif closed_set_down.__contains__(tuple([my_position[0], my_position[1] + 1])):
                closed_set_up = closed_set_right
            else:
                # print("Compute up")
                closed_set_up = self.board.multiple_accessible_path([my_position[0], my_position[1] + 1])

        inputs = np.array([
            dist_down_right,
            dist_right,
            dist_up_right,
            dist_up,
            dist_up_left,
            dist_left,
            dist_down_left,
            dist_down,
            len(closed_set_left) / 100,
            len(closed_set_right) / 100,
            len(closed_set_down) / 100,
            len(closed_set_up) / 100
        ])
        # print("Inputs :", inputs)

        # Compute output
        outputs = self.sigmoid(np.dot(inputs, self.weights_matrix))
        if dist_right == 0:
            outputs[0] = 100000000
        if dist_left == 0:
            outputs[1] = 100000000
        if dist_down == 0:
            outputs[2] = 100000000
        if dist_up == 0:
            outputs[3] = 100000000
        #  print("Outputs :", outputs)

        directions = ["RIGHT", "LEFT", "UP", "DOWN"]

        return directions[np.argmin(outputs)]

    def get_init_input(self, init):
        nb_players_str, my_id_str = init.split()
        self.nb_players = int(nb_players_str)
        self.my_id = int(my_id_str)
        self.positions = [[-1, -1] for i in range(self.nb_players)]

    def get_main_input(self, main_lines):
        line_number = 0
        for line in main_lines:
            x0, y0, x1, y1 = line.split()
            if int(x1) < 0:
                self.board.clean(line_number)
            else:
                x1 = int(x1)
                y1 = int(y1)
                self.positions[line_number] = [int(x1), int(y1)]
                self.board.set_cell(int(x1), int(y1), line_number)
                self.board.update_accessible_neighbors(tuple([x1, y1]))
            line_number += 1


# game loop
bot = NNBotCG(
    np.array([  4.52420512 , -0.87766097  , 7.30934799 , -1.10277717 ,-13.43480801,
                0.74623081  , 1.22035503  , 9.57820187 ,  4.46626086  , 4.58981703,
                0.3581873  ,-10.21943045  , 0.11875104 , -1.84715706  , 5.87171064,
                -9.65189541 ,  5.64380018 ,  0.30027729,  -0.89810895 ,  2.88333544,
                -0.67573445 ,-13.7406503  ,  5.03949205,  -0.19827648 , -0.29126397,
                -0.0434047  ,  1.71455815 ,  1.65001797,   1.2616012  , -0.60119918,
                -8.97846468 ,  3.9140979  , -0.18953093,   0.45765932  , 1.02685338,
                -3.46206591 , -6.25248716 ,  0.60866736,  -3.70255812 ,  4.4860027,
                2.05957479  , 3.03443933  , 8.41810065 ,  2.01300032 ,  2.21458412,
                -0.60364104 , -4.38924748 , -1.25531358])
)

turn = 0
while True:

    if turn == 0:
        bot.get_init_input(input())
    else:
        input()

    main_inputs = []
    for i in range(bot.nb_players):
        main_inputs.append(input())
    print("Main inputs:", main_inputs, file=sys.stderr)
    bot.get_main_input(main_inputs)

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)

    print(bot.get_next_play())
    turn += 1
