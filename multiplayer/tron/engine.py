import random


class Position:
    x = 0
    y = 0
    state = -1

    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def __repr__(self):
        return str(self.x) + "," + str(self.y)


class Board:
    width = 0
    height = 0
    cells = []

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = [[Position(i, j) for j in range(height)] for i in range(width)]

    def cell(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        return self.cells[x][y]

    def clean(self, id_bot):
        for i in range(self.height):
            for j in range(self.width):
                if self.cell(j, i).state == id_bot:
                    self.cell(j, i).state = -1

    def print(self):
        output = ""
        for i in range(self.height):
            for j in range(self.width):
                if self.cell(j, i).state == -1:
                    output += "_"
                else:
                    output += str(self.cell(j, i).state)
            output += "\n"
        print(output)


class GameEngine:
    width = 30
    height = 20
    bot_list = []
    positions = []
    bot_alive = []
    bot_live_duration = []
    board = None

    debug = False

    def __init__(self, bot_list, debug=False):
        self.positions = []
        self.board = Board(self.width, self.height)
        self.bot_list = bot_list
        self.debug = debug

        x_rand = random.randrange(self.width / 2)
        y_rand = random.randrange(self.height / 2)

        pos_bot1 = self.board.cell(x_rand, y_rand)
        self.positions.append(pos_bot1)
        pos_bot1.state = 0
        pos_bot2 = self.board.cell(self.width - 1 - x_rand, self.height - 1 - y_rand)
        self.positions.append(pos_bot2)
        pos_bot2.state = 1
        if len(bot_list) > 2:
            pos_bot3 = self.board.cell(x_rand, self.height - 1 - y_rand)
            self.positions.append(pos_bot3)
            pos_bot3.state = 2
        if len(bot_list) > 3:
            pos_bot4 = self.board.cell(self.width - 1 - x_rand, y_rand)
            self.positions.append(pos_bot4)
            pos_bot4.state = 1

        self.bot_alive = [True for i in bot_list]
        self.bot_live_duration = [0 for i in bot_list]

        main_inputs = []
        for j in range(len(self.bot_list)):
            main_inputs.append("0 0 " + str(self.positions[j].x) + " " + str(self.positions[j].y))

        for idx in range(len(self.bot_list)):
            self.bot_list[idx].get_init_input(str(len(self.bot_list)) + " " + str(idx))
            self.bot_list[idx].get_main_input(main_inputs)
            self.positions[idx].state = idx

        if debug:
            print("Initial positions:", self.positions)

    def next_turn(self):
        for i in range(len(self.bot_list)):
            if self.bot_alive[i]:
                main_inputs = []
                for j in range(len(self.bot_list)):
                    if self.bot_alive[j]:
                        main_inputs.append("0 0 " + str(self.positions[j].x) + " " + str(self.positions[j].y))
                    else:
                        main_inputs.append("-1 -1 -1 -1")
                self.bot_list[i].get_main_input(main_inputs)
                next_play = self.bot_list[i].get_next_play()
                self.execute_play(i, next_play)

                if self.bot_alive[i]:
                    self.bot_live_duration[i] += 1
        if self.debug:
            self.board.print()

    def execute_play(self, idx_bot, next_play):
        if next_play == "UP":
            next_cell = self.board.cell(self.positions[idx_bot].x, self.positions[idx_bot].y - 1)
        elif next_play == "DOWN":
            next_cell = self.board.cell(self.positions[idx_bot].x, self.positions[idx_bot].y + 1)
        elif next_play == "LEFT":
            next_cell = self.board.cell(self.positions[idx_bot].x - 1, self.positions[idx_bot].y)
        elif next_play == "RIGHT":
            next_cell = self.board.cell(self.positions[idx_bot].x + 1, self.positions[idx_bot].y)
        else:
            next_cell = None

        if next_cell is None or next_cell.state != -1:
            if self.debug:
                print("Bot number", idx_bot, "is dead, trying to go " + next_play + " from ", self.positions[idx_bot])
            self.bot_alive[idx_bot] = False
            self.board.clean(idx_bot)
        else:
            if self.debug:
                print("Bot number", idx_bot, " move from ", self.positions[idx_bot], " to ", next_cell, "(", next_play,
                      ")")
            self.positions[idx_bot] = next_cell
            next_cell.state = idx_bot

    def is_finished(self):
        count_bot_alive = 0
        for j in range(len(self.bot_list)):
            if self.bot_alive[j]:
                count_bot_alive += 1
            if count_bot_alive >= 2:
                return False
        return True
