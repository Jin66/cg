import logging
import math
import sys
from queue import SimpleQueue


class Board:

    def __init__(self, width=30, height=20, board=None):
        if board is None:
            self.height = height
            self.width = width
            self.bots = {}
            self.bots_alive = {}
            self.cells = [-1] * (self.width * self.height)
            self.adjacent_cells = []
            for idx in range(self.height * self.width):
                self.adjacent_cells.append(self._accessible_neighbors(idx))
        else:
            self.height = board.height
            self.width = board.width
            self.bots = board.bots.copy()
            self.bots_alive = board.bots_alive.copy()
            self.cells = [*board.cells]
            self.adjacent_cells = []
            self.adjacent_cells = [[*adjacent_cells] for adjacent_cells in board.adjacent_cells]

        self.components_map = {}
        self.components = []
        self.articulation_points = []

    def _accessible_neighbors(self, idx_pos):
        neighbors = []
        x = idx_pos % self.width
        y = int((idx_pos - x) / self.width)
        if x > 0:
            neighbors.append(x - 1 + y * self.width)
        if x < self.width - 1:
            neighbors.append(x + 1 + y * self.width)
        if y > 0:
            neighbors.append(x + (y - 1) * self.width)
        if y < self.height - 1:
            neighbors.append(x + (y + 1) * self.width)
        return neighbors

    def update_adjacency_graph(self, idx_pos):
        for neighbor in self._accessible_neighbors(idx_pos):
            if self.cells[idx_pos] != -1 and idx_pos in self.adjacent_cells[neighbor]:
                self.adjacent_cells[neighbor].remove(idx_pos)
            elif self.cells[idx_pos] == -1 and idx_pos not in self.adjacent_cells[neighbor]:
                self.adjacent_cells[neighbor].append(idx_pos)

    def idx_to_pos(self, idx_pos):
        x = idx_pos % self.width
        y = int((idx_pos - x) / self.width)
        return [x, y]

    def cell(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        return self.cells[x + y * self.width]

    def set_cell(self, x, y, value):
        self.cells[x + y * self.width] = value

    def set_bot_position(self, bot_id, pos):
        idx_pos = pos[0] + pos[1] * self.width
        self.set_bot_position_by_idx(bot_id, idx_pos)

    def set_bot_position_by_idx(self, bot_id, idx_pos):
        self.cells[idx_pos] = bot_id
        self.bots[bot_id] = idx_pos
        self.bots_alive[bot_id] = True
        self.update_adjacency_graph(idx_pos)
        self.components_map.clear()
        self.components.clear()
        self.articulation_points.clear()

    def get_legal_moves(self, bot_id):
        return self.adjacent_cells[self.bots[bot_id]]

    def clean_bot(self, id_bot):
        self.bots_alive[id_bot] = False
        cells_idx = []
        for idx in range(self.height * self.width):
            if self.cells[idx] == id_bot:
                self.cells[idx] = -1
                cells_idx.append(idx)
        for cell_idx in cells_idx:
            self.update_adjacency_graph(cell_idx)

    def print(self, level=logging.DEBUG):
        output = ""
        for i in range(self.height):
            for j in range(self.width):
                if self.cell(j, i) == -1:
                    output += "_"
                else:
                    output += str(self.cell(j, i))
            output += "\n"
        logging.log(level, output)

    def compute_graph_components(self):
        for idx in range(self.height * self.width):
            if idx not in self.components_map and self.cells[idx] == -1:
                self.components.append(self._component_from_idx(idx, len(self.components)))

    def _component_from_idx(self, idx, idx_component):
        component = []
        open_set = SimpleQueue()
        open_set.put(idx)
        self.components_map[idx] = idx_component
        while not open_set.empty():
            current_idx = open_set.get()
            component.append(current_idx)
            for neighbor in self.adjacent_cells[current_idx]:
                if neighbor not in self.components_map:
                    open_set.put(neighbor)
                    self.components_map[neighbor] = idx_component
        return component

    def distance_all_accessible_cells(self, idx_pos):
        visited = [False] * (self.height * self.width)
        open_set = [idx_pos]
        counter = 0
        distances = {idx_pos: 0}
        while len(open_set) > counter:
            current_idx = open_set[counter]
            counter += 1
            for neighbor in self.adjacent_cells[current_idx]:
                if not visited[neighbor]:
                    open_set.append(neighbor)
                    visited[neighbor] = True
                    distances[neighbor] = distances[current_idx] + 1
        return distances

    def compute_all_articulation_points_and_components(self):
        for idx in range(self.height * self.width):
            if idx not in self.components_map and self.cells[idx] == -1:
                visited = [False] * self.height * self.width
                depth = [0] * self.height * self.width
                low = [0] * self.height * self.width
                parents = [None] * self.height * self.width
                self._compute_articulation_points(idx, 0, visited, depth, low, parents)

                id_component = len(self.components)
                component = []
                self.components.append(component)
                for idx_v in range(len(visited)):
                    if visited[idx_v]:
                        self.components_map[idx_v] = id_component
                        component.append(idx_v)

    # Biconnected component : https://en.wikipedia.org/wiki/Biconnected_component
    # Algorithm by John Hopcroft and Robert Tarjan (1973)
    def _compute_articulation_points(self, idx_pos, d, visited, depth, low, parents):
        visited[idx_pos] = True
        depth[idx_pos] = d
        low[idx_pos] = d
        child_count = 0
        is_articulation = False

        for neighbor_idx in self.adjacent_cells[idx_pos]:
            if not visited[neighbor_idx]:
                parents[neighbor_idx] = idx_pos
                self._compute_articulation_points(neighbor_idx, d + 1, visited, depth, low, parents)
                child_count = child_count + 1
                if low[neighbor_idx] >= depth[idx_pos]:
                    is_articulation = True
                low[idx_pos] = min(low[idx_pos], low[neighbor_idx])
            elif parents[idx_pos] is not neighbor_idx:
                low[idx_pos] = min(low[idx_pos], depth[neighbor_idx])
        if (parents[idx_pos] is not None and is_articulation) or (parents[idx_pos] is None and child_count > 1):
            self.articulation_points.append(idx_pos)

    def compute_bot_possible_components(self):
        bots_possible_components = {}
        for bot_id, _ in enumerate(self.bots):
            bots_possible_components[bot_id] = {}
            if not self.bots_alive[bot_id]:
                continue
            legal_moves = self.get_legal_moves(bot_id)
            for move in legal_moves:
                try:
                    comp = self.components_map[move]
                except KeyError as e:
                    print('I got a KeyError - reason "%s"' % str(e))
                if self.components_map[move] not in bots_possible_components[bot_id]:
                    bots_possible_components[bot_id][self.components_map[move]] = []
                bots_possible_components[bot_id][self.components_map[move]].append(move)
        return bots_possible_components


class GameTreeNode:
    def __init__(self, bot_id, bots_cycle, board=None, move=None):
        self.bots_cycle = bots_cycle
        self.bot_id = bot_id
        self.board = board
        self.move = move
        self.children = []
        self.score = - math.inf

    def alpha_beta(self, alpha, beta, depth, bot_2_max):
        if depth == 0:
            logging.debug("Evaluate node for %s with move %s", self.bot_id, self.move)
            # self.board.print()
            score = self._evaluate(bot_2_max)
            logging.debug("Score %s", score)
            self.score = score
            return score
        if self.bot_id == bot_2_max:
            logging.debug("My bot node %s", self.move)
            # self.board.print()
            legal_moves = self.board.get_legal_moves(self.bot_id)
            if not legal_moves:
                self.score = - math.inf
                logging.debug("Score for %s: %s no player moves", self.move, self.score)
                return self.score
            for move in legal_moves:
                next_board = Board(board=self.board)
                next_board.set_bot_position_by_idx(self.bot_id, move)
                next_node = GameTreeNode(-1, self.bots_cycle, next_board, move)
                self.children.append(next_node)
            logging.debug("All children built (%s)", len(self.children))
            # for children in self.children:
            # children.board.print()
            max_score = - math.inf
            for children in self.children:
                max_score = max(max_score, children.alpha_beta(alpha, beta, depth - 1, bot_2_max))
                if max_score > beta:
                    self.score = max_score
                    logging.debug("Score for %s: %s", self.move, self.score)
                    return self.score
                alpha = max(alpha, max_score)
            self.score = max_score
            logging.debug("Score for %s: %s", self.move, self.score)
            return max_score

        else:
            logging.debug("Opp bot node for %s", self.move)
            # self.board.print()
            # Create the children with all combinations of opponent moves in one go
            self.children.extend(self._build_opp_children_nodes(bot_2_max))
            if not self.children:
                self.score = math.inf
                logging.debug("Score for %s: %s no opp moves", self.move, self.score)
                return self.score

            min_score = math.inf
            for children in self.children:
                min_score = min(min_score, children.alpha_beta(alpha, beta, depth - 1, bot_2_max))
                if min_score < alpha:
                    self.score = min_score
                    logging.debug("Score for %s: %s", self.move, self.score)
                    return min_score
                beta = min(beta, min_score)
            self.score = min_score
            logging.debug("Score for %s: %s", self.move, self.score)
            return min_score

    def _build_opp_children_nodes(self, bot_2_max):
        current_children = []
        for opp_bot_id in self.bots_cycle:
            if opp_bot_id == bot_2_max or not self.board.bots_alive[opp_bot_id]:
                continue
            legal_moves = self.board.get_legal_moves(opp_bot_id)
            if not legal_moves:
                self.board.clean_bot(opp_bot_id)
            else:
                if current_children:
                    # for each children, create grandchildren for all legal moves
                    new_children = []
                    for children in current_children:
                        for move in legal_moves:
                            next_board = Board(board=children.board)
                            next_board.set_bot_position_by_idx(opp_bot_id, move)
                            next_node = GameTreeNode(bot_2_max, self.bots_cycle, board=next_board)
                            new_children.append(next_node)
                    current_children = new_children
                else:
                    for move in legal_moves:
                        next_board = Board(board=self.board)
                        next_board.set_bot_position_by_idx(opp_bot_id, move)
                        next_node = GameTreeNode(bot_2_max, self.bots_cycle, board=next_board)
                        current_children.append(next_node)
        logging.debug("All children built (%s)", len(current_children))
        # for children in current_children:
        # children.board.print()
        return current_children

    def _evaluate(self, bot_2_max):
        distance_to_all_cells = {}
        bot_closest_to_cell = {}
        for bot_id, bot_pos in self.board.bots.items():
            # To sort if necessary {k: v for k, v in sorted(distance_to_cells.items(), key=lambda item: item[0])}
            distance_to_all_cells[bot_id] = self.board.distance_all_accessible_cells(bot_pos)
            bot_closest_to_cell[bot_id] = 0
        for idx_cell in range(self.board.width * self.board.height):
            best_bot = None
            min_distance = 1000
            for bot_id in self.board.bots:
                if idx_cell in distance_to_all_cells[bot_id]:
                    distance = distance_to_all_cells[bot_id][idx_cell]
                    if distance == min_distance:
                        best_bot = None
                    elif distance < min_distance:
                        best_bot = bot_id
                        min_distance = distance
            if best_bot is not None:
                bot_closest_to_cell[best_bot] += 1
        logging.debug("Bots closest to a given cell %s", bot_closest_to_cell)
        score = 0
        for bot_id in self.board.bots:
            if bot_id == bot_2_max:
                continue
            score += bot_closest_to_cell[bot_2_max] - bot_closest_to_cell[bot_id]
        return score


class GraphBot:

    def __init__(self, width=30, height=20, depth=1):
        self.board = Board(width=width, height=height)
        self.depth = depth
        self.my_id = 0
        self.nb_players = 2  # Default
        self.bots_cycle = [0, 1]
        self.turn = 0

    def get_init_input(self, init):
        nb_players_str, my_id_str = init.split()
        self.nb_players = int(nb_players_str)
        self.my_id = int(my_id_str)
        self.bots_cycle = [i for i in range(self.nb_players) if i != self.my_id]

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
        logging.info("Bot playing %s", self.my_id)
        self.board.print(logging.INFO)

        # Compute graph indicators / structural elements
        self.board.compute_all_articulation_points_and_components()
        logging.debug("Component: %s", self.board.components)
        logging.debug("Components map: %s", self.board.components_map)
        logging.debug("Articulation: %s", self.board.articulation_points)

        # Computes bots components
        bot_possible_components = self.board.compute_bot_possible_components()
        bots_components = self._bots_components(bot_possible_components)
        logging.info("Bots component : %s", bots_components)

        # I am alone ?
        alone = self.__am_i_alone(bots_components)
        logging.info("Am I alone ? %s", alone)

        # Find the best move !
        my_components = bots_components[self.my_id]
        logging.debug("My components: %s ", my_components)
        best_move = None
        if len(my_components) == 0:
            logging.info("No more room to move !")
            best_move = -1
        elif alone:
            best_move = self._get_space_filling_move(my_components, bot_possible_components)
        else:
            root_game_node = GameTreeNode(self.my_id, self.bots_cycle, board=self.board)
            root_game_node.alpha_beta(-math.inf, math.inf, self.depth, self.my_id)
            logging.info("Results alpha beta search : ")
            max_score = -math.inf
            for children in root_game_node.children:
                logging.info("%s: %s", children.move, children.score)
                if children.score >= max_score:
                    max_score = children.score
                    best_move = children.move
            logging.info("Best move alpha beta (depth:%s) search: %s", self.depth, best_move)

        # Move
        best_move_pos = self.board.idx_to_pos(best_move)
        my_position = self.board.idx_to_pos(self.board.bots[self.my_id])
        move_direction = None
        if best_move_pos[0] < my_position[0]:
            move_direction = "LEFT"
        if best_move_pos[0] > my_position[0]:
            move_direction = "RIGHT"
        if best_move_pos[1] < my_position[1]:
            move_direction = "UP"
        if best_move_pos[1] > my_position[1]:
            move_direction = "DOWN"
        logging.info("Choose to move %s (%s)", move_direction, best_move)
        return move_direction

    def _bots_components(self, bot_possible_components):
        bots_components = {idx: set() for idx in range(self.nb_players)}
        for bot_id, components_by_move in bot_possible_components.items():
            bots_components[bot_id].update(components_by_move.keys())
        logging.debug("Bots components: %s", bots_components)
        return bots_components

    def __am_i_alone(self, bots_components):
        is_alone = True
        my_components = bots_components[self.my_id]
        for bot_id, components in bots_components.items():
            if bot_id == self.my_id:
                continue
            if not my_components.isdisjoint(components):
                is_alone = False
                break
        return is_alone

    def _get_space_filling_move(self, my_components, bot_possible_components):
        best_move = None

        # If several components available, find the biggest one to explore
        best_component = next(iter(my_components))
        if len(my_components) > 1:
            max_size = 0
            for idx_component in my_components:
                size = len(self.board.components[idx_component])
                if size > max_size:
                    max_size = size
                    best_component = idx_component
        moves = bot_possible_components[self.my_id][best_component]
        logging.debug("Selected component: %s, for move: %s", best_component, moves)

        best_score = -100
        for move in moves:
            score = 5 - len(self.board.adjacent_cells[move])
            score -= 10 if move in self.board.articulation_points else 0
            if score > best_score:
                best_score = score
                best_move = move

        return best_move


logging.basicConfig(stream=sys.stderr, level=logging.INFO)

bot = None
turn = 0
# Game loop
while True:

    if turn == 0:
        bot = GraphBot(depth=3)
        bot.get_init_input(input())
        if bot.nb_players == 2:
            bot.depth = 3
        elif bot.nb_players == 3:
            bot.depth = 2
        else:
            bot.depth = 1
    else:
        input()

    main_inputs = []
    for i in range(bot.nb_players):
        main_inputs.append(input())
    print("Main inputs:", main_inputs, file=sys.stderr)
    bot.get_main_input(main_inputs)

    print(bot.get_next_play())
    turn += 1
