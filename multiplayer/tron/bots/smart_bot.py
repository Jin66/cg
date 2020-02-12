import random

from multiplayer.tron.bots.abstract_bot import AbstractBot


#  TODO; big refactoring, extract the Game class from the Board which implements the game logic

class Board:

    def __init__(self, width=30, height=20, board=None):
        if board is None:
            self.height = height
            self.width = width
            self.bots = {}
            self.cells = [-1 for i in range(self.width * self.height)]
            self.neighbors = {}
            for i in range(self.height):
                for j in range(self.width):
                    self.neighbors[tuple([j, i])] = self._accessible_neighbors([j, i])
        else:
            self.height = board.height
            self.width = board.width
            self.bots = board.bots.copy()
            self.cells = board.cells.copy()
            self.neighbors = {}
            for neighbors_pos in board.neighbors:
                self.neighbors[neighbors_pos] = board.neighbors[neighbors_pos].copy()

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

    def cell(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        return self.cells[x + y * self.width]

    def set_cell(self, x, y, value):
        self.cells[x + y * self.width] = value

    def set_bot_position(self, bot_id, pos):
        self.bots[bot_id] = pos
        self.set_cell(pos[0], pos[1], bot_id)
        self.update_accessible_neighbors(pos)

    def clean_bot(self, id_bot):
        cells = []
        for i in range(self.height):
            for j in range(self.width):
                if self.cell(j, i) == id_bot:
                    self.set_cell(j, i, -1)
                    cells.append(tuple([j, i]))
        for cell in cells:
            self.update_accessible_neighbors(cell)

    def _accessible_neighbors(self, pos):
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
        # print("Update neighbors for", pos)
        for neighbor in self.neighbors[pos]:
            if self.cell(pos[0], pos[1]) is not -1 and self.neighbors[neighbor].__contains__(pos):
                self.neighbors[neighbor].remove(pos)
            elif not self.neighbors[neighbor].__contains__(pos):
                self.neighbors[neighbor].append(pos)

    def get_legal_moves(self, bot_id):
        # print("Got legal moves for ", bot_id, " at position ", self.bots[bot_id], " :", legal_moves)
        return self.neighbors[self.bots[bot_id]]


class BoardTreeNode:
    max_turns = 300

    def __init__(self, bot_id, bots_cycle, move=None, parent=None, board=None):
        self.bots_cycle = bots_cycle
        self.bot_id = bot_id
        self.move = move
        self.parent = parent
        self.board = board

        self.children = []
        self.win = 0
        self.played = 0

    def expand(self):
        next_bot_id = self._next_bot_id(self.bot_id)
        legal_moves = self.board.get_legal_moves(next_bot_id)
        if not legal_moves:
            print("Cannot expand, no legal moves for ", next_bot_id)
            return
        for move in legal_moves:
            next_board = Board(board=self.board)
            next_board.set_bot_position(next_bot_id, move)
            next_node = BoardTreeNode(next_bot_id, self.bots_cycle, move, self, next_board)
            self.children.append(next_node)
            # print("Expand tree for bot ", next_bot_id, " with move ", move)

    # TODO: Check if game has ended
    # TODO: manage cleaning if a bot dies
    def rollout(self):
        count_turn = 0
        # print("Rollout for ", self.bot_id, " from move ", self.move)
        current_board = Board(board=self.board)
        bots_alives = [True for i in range(len(self.bots_cycle))]
        next_bot_id = self._next_bot_id(self.bot_id)
        while count_turn < self.max_turns:
            if not bots_alives[next_bot_id]:
                continue
            legal_moves = current_board.get_legal_moves(next_bot_id)
            if not legal_moves:
                bots_alives[next_bot_id] = False
                winner = self._get_winner(bots_alives)
                if winner is not None:
                    self.win += 1 if winner == self.bot_id else 0
                    self.played += 1
                    # TODO: backprop to parent node
                    break
                current_board.clean_bot(next_bot_id)
                next_bot_id = self._next_bot_id(next_bot_id)
                continue
            idx_move = random.randint(0, len(legal_moves) - 1)
            # print("Chose ", legal_moves[idx_move])
            current_board.set_bot_position(next_bot_id, legal_moves[idx_move])
            next_bot_id = self._next_bot_id(next_bot_id)
            count_turn += 1
        if winner is None:
            self.win += 0.5
            self.played += 1

    @staticmethod
    def _get_winner(bots_alive):
        count_alive = 0
        possible_winner = None
        for bot_idx in range(len(bots_alive)):
            if bots_alive[bot_idx]:
                count_alive += 1
                possible_winner = bot_idx
            if count_alive is 2:
                return None
        return possible_winner

    def _next_bot_id(self, current_bot_id):
        return current_bot_id + 1 if current_bot_id + 1 < len(self.bots_cycle) else 0


class SmartBot(AbstractBot):
    max_depth = 3

    def __init__(self, width=30, height=20):
        self.board = Board(width=width, height=height)
        self.my_id = 0
        self.nb_players = 2  # Default
        self.bots_cycle = [0, 1]
        self.turn = 0

    def get_init_input(self, init):
        nb_players_str, my_id_str = init.split()
        self.nb_players = int(nb_players_str)
        self.bots_cycle = [i for i in range(self.nb_players)]
        self.my_id = int(my_id_str)

    def get_main_input(self, main_lines):
        line_number = 0
        for line in main_lines:
            x0, y0, x1, y1 = line.split()

            # Manage first turn
            if self.turn == 0 and (int(x0) != int(x1) or int(y0) != int(y1)):
                self.board.set_bot_position(line_number, tuple([int(x0), int(y0)]))
            if int(x1) < 0:
                self.board.clean_bot(line_number)
            else:
                self.board.set_bot_position(line_number, tuple([int(x1), int(y1)]))
            line_number += 1
        self.turn += 1

    def get_next_play(self):
        root = BoardTreeNode(self._previous_bot_id(self.my_id), self.bots_cycle, board=self.board)
        root.expand()
        number_rollout = 50
        best_move = None
        best_ratio = 0
        for children in root.children:
            for i in range(number_rollout):
                children.rollout()
            # print(children.move, ": ")
            ratio = children.win / children.played
            # print("Move:", children.move, ":", children.win, "/", children.played, " ratio: ", ratio)
            if ratio >= best_ratio:
                best_move = children.move
                best_ratio = ratio
        my_position = self.board.bots[self.my_id]
        if best_move is None:
            print("No legal moves, suicide")
            return "UP"
        if best_move[0] < my_position[0]:
            return "LEFT"
        if best_move[0] > my_position[0]:
            return "RIGHT"
        if best_move[1] < my_position[1]:
            return "UP"
        if best_move[1] > my_position[1]:
            return "DOWN"

    def _previous_bot_id(self, current_bot_id):
        return current_bot_id - 1 if current_bot_id - 1 >= 0 else self.bots_cycle[-1]
