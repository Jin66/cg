import random


class Results:
    lives_duration = []
    winner = 0

    def __init__(self, lives_duration, winner, moves):
        self.moves = moves
        self.winner = winner
        self.lives_duration = lives_duration

    def __repr__(self):
        return "Winner: " + str(self.winner) + " lives duration: " + str(self.lives_duration)


class Position:
    x = 0
    y = 0
    state = -1

    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def __repr__(self):
        return str(self.x) + "," + str(self.y)

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)


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

    def clean(self, id_bot=None):
        for i in range(self.height):
            for j in range(self.width):
                if id_bot is None or self.cell(j, i).state == id_bot:
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
    bots_alive = []
    bots_live_duration = []
    board = None

    debug = False

    def __init__(self, debug=False):
        self.moves = []
        self.board = Board(self.width, self.height)
        self.debug = debug

    def run(self, bot_list):
        """
            Run a complete game for all the bots sent. Stopped when only one bot remains
            :return: game results
        """

        self.board.clean()
        self.moves.clear()
        self.positions = []
        self.bot_list = bot_list

        # Bot lives
        self.bots_alive = [True for i in bot_list]
        self.bots_live_duration = [0 for i in bot_list]

        # Initialize positions for all bots
        x_rand = random.randrange(self.width / 2)
        y_rand = random.randrange(self.height / 2)

        self.positions.append(self.board.cell(x_rand, y_rand))
        self.positions.append(self.board.cell(self.width - 1 - x_rand, self.height - 1 - y_rand))

        if len(bot_list) > 2:
            self.positions.append(self.board.cell(x_rand, self.height - 1 - y_rand))

        if len(bot_list) > 3:
            self.positions.append(self.board.cell(self.width - 1 - x_rand, y_rand))

        # Shuffle positions
        random.shuffle(self.positions)

        if self.debug:
            print("Initial positions:", self.positions)

        # Send init input to bots
        for idx in range(len(self.bot_list)):
            self.positions[idx].state = idx
            self.bot_list[idx].get_init_input(str(len(self.bot_list)) + " " + str(idx))

        # Run the game
        while True:
            is_finished = self.next_turn()
            if is_finished:
                return self.get_results()

    def next_turn(self):
        """
        Run a single turn for all the bots. Stopped if only one bot remains
        :return: if the game need to continue
        """

        # Store old
        old_positions = []
        for idx_bot in range(len(self.bot_list)):
            old_positions.append(self.positions[idx_bot])

        for idx_bot in range(len(self.bot_list)):
            if self.bots_alive[idx_bot]:
                main_inputs = []
                count_bot_alive = 0
                for j in range(len(self.bot_list)):
                    if self.bots_alive[j]:
                        main_inputs.append(str(old_positions[j].x) + " " +
                                           str(old_positions[j].y) + " " +
                                           str(self.positions[j].x) + " " +
                                           str(self.positions[j].y))
                        count_bot_alive += 1
                    else:
                        main_inputs.append("-1 -1 -1 -1")
                self.bot_list[idx_bot].get_main_input(main_inputs)
                next_play = self.bot_list[idx_bot].get_next_play()
                self.execute_play(idx_bot, next_play)

                if self.bots_alive[idx_bot]:
                    self.bots_live_duration[idx_bot] += 1
                elif count_bot_alive == 2:
                    return True
        if self.debug:
            self.board.print()
        return False

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
            self.bots_alive[idx_bot] = False
            self.board.clean(idx_bot)
            self.moves.append((idx_bot, next_play, self.positions[idx_bot], None))
        else:
            if self.debug:
                print("Bot number", idx_bot, " move from ", self.positions[idx_bot], " to ", next_cell, "(", next_play,
                      ")")
            self.moves.append((idx_bot, next_play, self.positions[idx_bot], next_cell))
            self.positions[idx_bot] = next_cell
            next_cell.state = idx_bot

    def is_finished(self):
        count_bot_alive = 0
        for j in range(len(self.bot_list)):
            if self.bots_alive[j]:
                count_bot_alive += 1
            if count_bot_alive >= 2:
                return False
        return True

    def get_results(self):
        winner = -1
        for i, bot_live_duration in enumerate(self.bots_alive):
            if bot_live_duration:
                winner = i
        return Results(self.bots_live_duration, winner, self.moves)
