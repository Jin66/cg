import sys
from typing import List, Tuple, Dict


class Position:
    x = -1
    y = -1
    state = ""
    bot = ""
    visited = False
    unknown_neighbors = 0

    def __init__(self, x, y, state, bot):
        self.x = x
        self.y = y
        self.state = state
        self.bot = bot

    def __repr__(self):
        return str(self.x) + "-" + str(self.y)

    def distance(self, target):
        return abs(self.x - target.x) + abs(self.y - target.y)


class Board:
    width = 0
    height = 0
    score = 0
    cells: List[List[Position]] = []

    def __init__(self, width, height):
        self.width = width
        self.height = height
        for y in range(height):
            self.cells.append([])
            for x in range(width):
                self.cells[y].append(Position(x, y, "%", ""))

    def __repr__(self):
        toPrint = ""
        for y in range(height):
            for x in range(width):
                if self.cell(x, y).bot:
                    toPrint += self.cell(x, y).bot
                elif self.cell(x, y).state == "_" and not self.cell(x, y).visited:
                    toPrint += "*"
                else:
                    toPrint += self.cell(x, y).state
            toPrint += "\n"
        return toPrint

    def cell(self, x, y):
        return self.cells[y][x]

    def clean_and_score(self):
        self.score = 0
        for y in range(height):
            for x in range(width):
                cell = self.cell(x, y)
                cell.bot = None
                self.score += 1 if cell.visited else 0
                cell.unknown_neighbors = len(self.unknown_cells(cell))

    def neighbors(self, pos):
        neighbors: List[Tuple[Position, str]] = [
            (self.cell(pos.x, pos.y + 1) if pos.y + 1 < height else self.cell(pos.x, 0), "S"),
            (self.cell(pos.x, pos.y - 1) if pos.y - 1 >= 0 else self.cell(pos.x, height - 1), "N"),
            (self.cell(pos.x + 1, pos.y) if pos.x + 1 < width else self.cell(0, pos.y), "E"),
            (self.cell(pos.x - 1, pos.y) if pos.x - 1 >= 0 else self.cell(width - 1, pos.y), "W")
        ]
        return neighbors

    def accessible_cells(self, pos) -> List[Position]:
        return [neighbor[0] for neighbor in self.neighbors(pos) if neighbor[0].state == "_"]

    def unknown_cells(self, pos) -> List[Position]:
        return [neighbor[0] for neighbor in self.neighbors(pos) if neighbor[0].state == "%"]

    def multiple_accessible_path(self, pos):
        closed_set: set[Position] = set()
        openSet: set[Position] = set()
        openSet.add(pos)
        came_from: Dict[Position, Position] = {}
        gScore: Dict[Position, int] = {pos: 0}
        while openSet:
            current: Position = openSet.pop()
            closed_set.add(current)
            for neighbor in self.accessible_cells(current):
                if closed_set.__contains__(neighbor):
                    continue
                neighborGScore = gScore[current] + 1
                if not openSet.__contains__(neighbor):
                    openSet.add(neighbor)
                elif neighborGScore >= gScore[neighbor]:
                    continue
                came_from[neighbor] = current
                gScore[neighbor] = neighborGScore

        return came_from, closed_set

    @staticmethod
    def build_path(position, came_from):
        path = [position]
        current = position
        while current in came_from.keys():
            current = came_from[current]
            path.append(current)
        return path


height = int(input())  # guess : height
width = int(input())  # guess : width
board = Board(width, height)
countBots = int(input())  # guess : number of bots
print("Width: ", width, " Height: ", height, " CountBots: ", countBots, file=sys.stderr)

# Game Loop
while True:
    # Clean board from old bot position
    board.clean_and_score()

    # Border my position char with # and _
    borders = {"N": input(), "E": input(), "S": input(), "W": input()}
    # print(" N:", borders["N"],
    #      " E:", borders["E"],
    #      " S:", borders["S"],
    #      " W: ", borders["W"],
    #      file=sys.stderr)

    bots: List[Position] = []
    for i in range(countBots - 1):
        x, y = [int(j) for j in input().split()]
        bots.append(board.cell(x, y))
        board.cell(x, y).state = "_"
        board.cell(x, y).bot = str(i)

    xM, yM = [int(j) for j in input().split()]
    myPosition = board.cell(xM, yM)
    myPosition.state = "_"
    myPosition.bot = "M"
    myPosition.visited = True

    print("M: ", myPosition, " bots: ", bots, " score: ", board.score, file=sys.stderr)

    maxScore = 0
    for position, direction in board.neighbors(myPosition):
        board.cell(position.x, position.y).state = borders[direction]

    paths_map, closed_set = board.multiple_accessible_path(myPosition)
    maxScore = -100000
    minDist = 1000
    move_position = None
    target = None
    for pos in closed_set:
        path = board.build_path(pos, paths_map)
        if len(path) == 1:
            continue
        score = 0
        scAlertBot = 0
        scVisited = 0
        for p in path:
            distP = myPosition.distance(p)
            scVisited += 50 + p.unknown_neighbors - distP if not p.visited else 0
            scAlertBot -= 10000 if p in bots else 0
        dist = myPosition.distance(pos)
        scDistBot = 0
        scMovePosition = 0
        for bot in bots:
            distB = pos.distance(bot)
            scDistBot += distB
            scMovePosition -= 10000 if path[-2].distance(bot) == 1 else 0
        score = scDistBot + scAlertBot + scVisited + scMovePosition

        # Prevent problem when the m

        if maxScore < score or (maxScore == score and dist < minDist):
            # print(pos, ": ", scVisited, "|", scAlertBot, "|", scDistBot, file=sys.stderr)
            maxScore = score
            move_position = path[-2]
            target = pos
            minDist = dist

    print("Target : ", target, " by: ", move_position, " with score ", maxScore, file=sys.stderr)

    if not move_position:
        print("B")
    elif move_position.x < myPosition.x or (
            move_position.x > myPosition.x == 0 and move_position.x == width - 1):
        print("E")
    elif move_position.x > myPosition.x or (
            move_position.x < myPosition.x == width - 1 and move_position.x == 0):
        print("A")
    elif move_position.y < myPosition.y:
        print("C")
    elif move_position.y > myPosition.y:
        print("D")
    else:
        print("B")

    if target:
        board.cell(target.x, target.y).state = "T"
    print(board, file=sys.stderr)
    if target:
        board.cell(target.x, target.y).state = "_"

# A  go east
# B  wait
# C  go north
# D  go south
# E  go west
