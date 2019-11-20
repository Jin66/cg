import numpy as np
import sys


class Board:
    width = 0
    height = 0
    cells = []

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = [-1 for i in range(width * height)]

    def get_cell(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        return self.cells[x + y * self.width]

    def set_cell(self, x, y, value):
        self.cells[x + y * self.width] = value

    def clean(self, id_bot):
        for i in range(self.height):
            for j in range(self.width):
                if self.get_cell(j, i) == id_bot:
                    self.set_cell(j, i, -1)

    def distances_limit(self, pos, move):
        dx, dy = move
        cell_x = pos[0] + dx
        cell_y = pos[1] + dy
        distance = 0
        while self.get_cell(cell_x, cell_y) is not None and self.get_cell(cell_x, cell_y) == -1:
            cell_x += dx
            cell_y += dy
            distance += 1
        return distance

    def print(self):
        output = ""
        for i in range(self.height):
            for j in range(self.width):
                if self.get_cell(j, i) == -1:
                    output += "_"
                else:
                    output += str(self.get_cell(j, i))
            output += "\n"
        print(output)


class NNBotCG:
    width = 30
    height = 20

    def __init__(self, weights):
        self.board = Board(self.width, self.height)
        self.positions = []
        self.my_id = 0
        self.nb_players = 2
        self.weights = weights  # size: 32 = 8 inputs x 4 outputs (fully connected)
        self.weights_matrix = np.reshape(self.weights, (8, 4))

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def get_next_play(self):
        # Prepare input network
        dist_down_right = self.board.distances_limit(self.positions[self.my_id], [1, -1])
        dist_right = self.board.distances_limit(self.positions[self.my_id], [1, 0])
        dist_up_right = self.board.distances_limit(self.positions[self.my_id], [1, 1])
        dist_up = self.board.distances_limit(self.positions[self.my_id], [0, 1])
        dist_up_left = self.board.distances_limit(self.positions[self.my_id], [-1, 1])
        dist_left = self.board.distances_limit(self.positions[self.my_id], [-1, 0])
        dist_down_left = self.board.distances_limit(self.positions[self.my_id], [-1, -1])
        dist_down = self.board.distances_limit(self.positions[self.my_id], [0, -1])

        inputs = np.array([
            dist_down_right,
            dist_right,
            dist_up_right,
            dist_up,
            dist_up_left,
            dist_left,
            dist_down_left,
            dist_down
        ])
        print("Inputs :", inputs, file=sys.stderr)

        # Compute output
        outputs = self.sigmoid(np.dot(inputs, self.weights_matrix))
        if dist_right == 0:
            outputs[0] = 100
        if dist_left == 0:
            outputs[1] = 100
        if dist_down == 0:
            outputs[2] = 100
        if dist_up == 0:
            outputs[3] = 100

        print("Outputs :", outputs, file=sys.stderr)

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
                self.positions[line_number] = [int(x1), int(y1)]
                self.board.set_cell(int(x1), int(y1), line_number)
            line_number += 1


# game loop
bot = NNBotCG(
    np.array(
        [-1.49249326, 6.9250816, - 1.28802327, 8.05553285, - 7.34359195,
         10.43034913, 13.95936218, 7.55466754, 5.38061263, 2.12542998,
         5.38101865, 7.41687042, 4.66123242, 4.1898194, 2.41112609,
         - 7.26737919, - 13.47069627, - 2.91085446, 1.87898524, - 13.33405272,
         7.59897861, - 15.91118506, 3.26020317, - 1.66513524, 1.24017453,
         - 1.89030949, - 1.82190422, 9.36002452, 8.37018528, - 0.54878283,
         - 6.86607161, - 0.58840828]
    )
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
