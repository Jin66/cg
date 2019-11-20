from multiplayer.tron.bots.abstract_bot import AbstractBot
import numpy as np


class Board:
    width = 0
    height = 0

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = [-1 for i in range(width * height)]

        self.neighbors = {}
        for i in range(self.height):
            for j in range(self.width):
                self.neighbors[tuple([j, i])] = self.accessible_neighbors([j, i])

    def cell(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        return self.cells[x + y * self.width]

    def set_cell(self, x, y, value):
        self.cells[x + y * self.width] = value

    def pos_to_cell_index(self, x, y):
        return x + y * self.width

    def clean(self, id_bot):
        cells = []
        for i in range(self.height):
            for j in range(self.width):
                if self.cell(j, i) == id_bot:
                    self.set_cell(j, i, -1)
                    cells.append(tuple([j, i]))
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


class NNBot(AbstractBot):
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
            #print("Compute left")
            closed_set_left = self.board.multiple_accessible_path([my_position[0] - 1, my_position[1]])
        if my_position[0] < self.board.width - 1:
            if closed_set_left.__contains__(tuple([my_position[0] + 1, my_position[1]])):
                closed_set_right = closed_set_left
            else:
                #print("Compute right")
                closed_set_right = self.board.multiple_accessible_path([my_position[0] + 1, my_position[1]])
        if my_position[1] > 0:
            if closed_set_left.__contains__(tuple([my_position[0], my_position[1] - 1])):
                closed_set_down = closed_set_left
            elif closed_set_right.__contains__(tuple([my_position[0], my_position[1] - 1])):
                closed_set_down = closed_set_right
            else:
                #print("Compute down")
                closed_set_down = self.board.multiple_accessible_path([my_position[0], my_position[1] - 1])
        if my_position[1] < self.board.height - 1:
            if closed_set_left.__contains__(tuple([my_position[0], my_position[1] + 1])):
                closed_set_up = closed_set_left
            elif closed_set_right.__contains__(tuple([my_position[0], my_position[1] + 1])):
                closed_set_up = closed_set_right
            elif closed_set_down.__contains__(tuple([my_position[0], my_position[1] + 1])):
                closed_set_up = closed_set_right
            else:
                #print("Compute up")
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
        # if dist_right == 0:
        #     outputs[0] = 100
        # if dist_left == 0:
        #     outputs[1] = 100
        # if dist_down == 0:
        #     outputs[2] = 100
        # if dist_up == 0:
        #     outputs[3] = 100
        #  print("Outputs :", outputs)

        directions = ["RIGHT", "LEFT", "UP", "DOWN"]

        return directions[np.argmax(outputs)]

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
                self.positions[line_number] = [x1, y1]
                self.board.set_cell(x1, y1, line_number)
                self.board.update_accessible_neighbors(tuple([x1, y1]))
            line_number += 1
