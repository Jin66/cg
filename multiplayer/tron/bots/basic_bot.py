import enum

from multiplayer.tron.bots.abstract_bot import AbstractBot


class InputMode(enum.Enum):
    DistanceSquare = 1
    DistanceDiag = 2
    AccessibleCells = 3
    BotsPosition = 4


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

    def get_cell_state(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        return self.cells[x + y * self.width]

    def set_cell_state(self, x, y, value):
        self.cells[x + y * self.width] = value

    def cell(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        return [x, y]

    def close_cell(self, x, y, dx, dy):
        state = self.get_cell_state(x + dx, y + dy)
        return self.cell(x + dx, y + dy) if state == -1 else None

    def pos_to_cell_index(self, x, y):
        return x + y * self.width

    def clean(self, id_bot):
        cells = []
        for i in range(self.height):
            for j in range(self.width):
                if self.get_cell_state(j, i) == id_bot:
                    self.set_cell_state(j, i, -1)
                    cells.append(tuple([j, i]))
        for cell in cells:
            self.update_accessible_neighbors(cell)

    def distances_limit(self, pos, move):
        dx, dy = move
        cell_x = pos[0] + dx
        cell_y = pos[1] + dy
        distance = 0
        while self.get_cell_state(cell_x, cell_y) is not None and self.get_cell_state(cell_x, cell_y) == -1:
            cell_x += dx
            cell_y += dy
            distance += 1
        return distance

    def print(self):
        output = ""
        for i in range(self.height):
            for j in range(self.width):
                if self.get_cell_state(j, i) == -1:
                    output += "_"
                else:
                    output += str(self.get_cell_state(j, i))
            output += "\n"
        print(output)

    def accessible_neighbors(self, pos):
        neighbors = []
        if pos[0] > 0 and self.get_cell_state(pos[0] - 1, pos[1]) == -1:
            neighbors.append(tuple([pos[0] - 1, pos[1]]))
        if pos[0] < self.width - 1 and self.get_cell_state(pos[0] + 1, pos[1]) == -1:
            neighbors.append(tuple([pos[0] + 1, pos[1]]))
        if pos[1] > 0 and self.get_cell_state(pos[0], pos[1] - 1) == -1:
            neighbors.append(tuple([pos[0], pos[1] - 1]))
        if pos[1] < self.height - 1 and self.get_cell_state(pos[0], pos[1] + 1) == -1:
            neighbors.append(tuple([pos[0], pos[1] + 1]))
        return neighbors

    def update_accessible_neighbors(self, pos):
        for neighbor in self.neighbors[pos]:
            if self.get_cell_state(pos[0], pos[1]) is not -1 and self.neighbors[neighbor].__contains__(pos):
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


class BasicBot(AbstractBot):
    width = 30
    height = 20

    def __init__(self):
        self.board = Board(self.width, self.height)
        self.positions = []
        self.my_id = 0
        self.nb_players = 2  # Default
        self.turn = 0
        self.debug = False

    def get_init_input(self, init):
        nb_players_str, my_id_str = init.split()
        self.nb_players = int(nb_players_str)
        self.my_id = int(my_id_str)
        self.positions = [[-1, -1] for i in range(self.nb_players)]

    def get_main_input(self, main_lines):
        line_number = 0
        for line in main_lines:
            x0, y0, x1, y1 = line.split()
            if self.turn == 0 and (int(x0) != int(x1) or int(y0) != int(y1)):
                self.board.set_cell_state(int(x0), int(y0), line_number)
            if int(x1) < 0:
                self.board.clean(line_number)
            else:
                x1 = int(x1)
                y1 = int(y1)
                self.positions[line_number] = [x1, y1]
                self.board.set_cell_state(x1, y1, line_number)
                self.board.update_accessible_neighbors(tuple([x1, y1]))
            line_number += 1
        self.turn += 1

    def get_next_play(self):
        me = self.positions[self.my_id]

        # Neighbor cells
        close_cells = {
            "LEFT": self.board.close_cell(me[0], me[1], -1, 0),
            "RIGHT": self.board.close_cell(me[0], me[1], 1, 0),
            "DOWN": self.board.close_cell(me[0], me[1], 0, 1),
            "UP": self.board.close_cell(me[0], me[1], 0, -1)
        }
        if self.debug:
            print(close_cells)

        # Compute accessible_cells
        accessible_cells_directions = {}
        for direction, close_cell in close_cells.items():
            accessible_cells = []
            if close_cell is not None:
                for _, accessible_cells_saved in accessible_cells_directions.items():
                    if accessible_cells_saved.__contains__(tuple(close_cell)):
                        accessible_cells = accessible_cells_saved
                        break
                if len(accessible_cells) == 0 and close_cell is not None:
                    accessible_cells = self.board.multiple_accessible_path(close_cell)
            accessible_cells_directions[direction] = accessible_cells

        score = {
            direction: len(accessible_cells)
            for direction, accessible_cells in accessible_cells_directions.items()
        }
        if self.debug:
            print(score, " ", min(score, key=score.get))

        # Select the direction in which the bot has the maximum cell accessible
        return max(score, key=score.get)
