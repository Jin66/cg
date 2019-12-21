import pygame
from pygame.constants import RESIZABLE, QUIT

from multiplayer.tron.engine import Position


class TronBasicTV:

    def __init__(self, board_w, board_h):
        self.board_h = board_h
        self.board_w = board_w

        pygame.init()
        size = 1200, 1000
        self.windows = pygame.display.set_mode(size, RESIZABLE)
        pygame.display.set_caption('Tron')

        # Bot positions
        self.bot_positions = {0: [], 1: [], 2: [], 3: []}

        # Determine block size
        screen_w, screen_h = self.windows.get_size()
        screen_w_usefull = screen_w * 0.93
        screen_h_usefull = screen_h * 0.93
        block_w = int(screen_w_usefull / self.board_w)
        block_h = int(screen_h_usefull / self.board_h)
        self.block = min(block_w, block_h)
        self.o_x = int((screen_w - screen_w_usefull) / 2)
        self.o_y = int((screen_h - screen_h_usefull) / 2)

        # Draw blocks
        self.draw_blocks(None)

        # Draw grid
        self.draw_grid()

    def draw_grid(self):
        grid_color = (155, 155, 155)

        for i in range(0, self.board_w + 1):
            pygame.draw.line(self.windows,
                             grid_color,
                             (self.o_x + i * self.block, self.o_y),
                             (self.o_x + i * self.block, self.o_y + self.board_h * self.block),
                             1)
        for i in range(0, self.board_h + 1):
            pygame.draw.line(self.windows,
                             grid_color,
                             (self.o_x, self.o_y + i * self.block),
                             (self.o_x + self.board_w * self.block, self.o_y + i * self.block),
                             1)

    def draw_blocks(self, filter):
        block_color = (190, 190, 190)
        for i in range(0, self.board_w):
            for j in range(0, self.board_h):
                if filter is not None and Position(i, j) not in filter:
                    continue
                pygame.draw.rect(self.windows,
                                 block_color,
                                 (
                                     self.o_x + i * self.block, self.o_y + j * self.block,
                                     self.block, self.block)
                                 )

    def draw_move(self, move):
        idx_bot, direction, position, next_cell = move
        self.bot_positions[idx_bot].append(position)

        blue = (0, 0, 255)
        red = (255, 0, 0)
        green = (0, 255, 0)
        orange = (255, 165, 0)
        map_id_color = [blue, red, green, orange]

        if next_cell is None:
            self.draw_blocks(self.bot_positions[idx_bot])
            self.draw_grid()
            return

        pygame.draw.circle(self.windows,
                           map_id_color[idx_bot],
                           (
                               self.o_x + int((next_cell.x + 0.5) * self.block),
                               self.o_y + int((next_cell.y + 0.5) * self.block)
                           ),
                           int((self.block * 0.6) / 2)
                           )
        if direction == "UP":
            pygame.draw.rect(self.windows,
                             map_id_color[idx_bot],
                             (
                                 self.o_x + (next_cell.x + 0.2) * self.block,
                                 self.o_y + (next_cell.y + 0.4) * self.block,
                                 self.block * 0.6, 1.2 * self.block)
                             )
        if direction == "DOWN":
            pygame.draw.rect(self.windows,
                             map_id_color[idx_bot],
                             (
                                 self.o_x + (next_cell.x + 0.2) * self.block,
                                 self.o_y + (position.y + 0.4) * self.block,
                                 self.block * 0.6, 1.2 * self.block)
                             )
        if direction == "LEFT":
            pygame.draw.rect(self.windows,
                             map_id_color[idx_bot],
                             (
                                 self.o_x + (next_cell.x + 0.4) * self.block,
                                 self.o_y + (next_cell.y + 0.2) * self.block,
                                 self.block * 1.2, 0.6 * self.block)
                             )
        if direction == "RIGHT":
            pygame.draw.rect(self.windows,
                             map_id_color[idx_bot],
                             (
                                 self.o_x + (position.x + 0.4) * self.block,
                                 self.o_y + (next_cell.y + 0.2) * self.block,
                                 self.block * 1.2, 0.6 * self.block)
                             )

    def run(self, moves):
        for move in moves:
            pygame.time.Clock().tick(10)
            self.draw_move(move)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
