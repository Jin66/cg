import sys
import math


# Save humans, destroy zombies!
class Position:
    """Common base class for all located objects"""
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "%d" % self.x + "-%d" % self.y

    def __repr__(self):
        return self.__str__()


class Human(Position):
    """Class for the player which has to kill all zombies"""
    identifier = 0

    def __init__(self, x, y, identifier):
        Position.__init__(self, x, y)
        self.y = y
        self.identifier = identifier

    def __str__(self):
        return Position.__str__(self) + "-{}".format(self.identifier)


class Zombie(Human):
    """Class for the Zombies"""
    x_next = 0
    y_next = 0

    def __init__(self, x, y, id, x_next, y_next):
        Human.__init__(self, x, y, id)
        self.x_next = x_next
        self.y_next = y_next


class GlobalPosition:
    """Class to store a given Global position in the game"""
    ash = []
    mapHumans = {}
    mapZombies = {}
    mapClosestZH = {}
    score = 0

    def __init__(self):
        self.ash = []
        self.mapHumans = {}
        self.mapZombies = {}
        self.mapClosestZH = {}
        self.score = 0

    def __str__(self):
        return "Ash: " + str(self.ash) + " - " + "Humans: " + str(self.mapHumans) + " - " + "Zombies: " + str(
            self.mapZombies) + " score: " + str(self.score)

    def computeNextGlobalPosition(self, position_target, debug):
        nextGlobalPosition = GlobalPosition()

        # 1. Zombies move towards their targets (max 400 units toward closest human)

        # List of human to destroy if the zombie is not dead at the end of the turn.
        humanPossiblyKilled = {}
        # Distance Z -> Ash
        squareDistanceZAsh = {}

        for idZ, positionZ in self.mapZombies.items():
            # Find the closest human
            # Init with ash
            dX = positionZ[0] - self.ash[0]
            dY = positionZ[1] - self.ash[1]
            minDist = dX * dX + dY * dY
            squareDistanceZAsh[idZ] = minDist
            closestH = [self.ash[0], self.ash[1]]
            closestIdH = -1
            if idZ in self.mapClosestZH and self.mapClosestZH[idZ] in self.mapHumans:
                idH = self.mapClosestZH[idZ]
                dX = positionZ[0] - self.mapHumans[idH][0]
                dY = positionZ[1] - self.mapHumans[idH][1]
                distance = dX * dX + dY * dY
                if minDist > distance:
                    minDist = distance
                    closestH = [self.mapHumans[idH][0], self.mapHumans[idH][1]]
                    closestIdH = idH
            else:
                for idH, positionH in self.mapHumans.items():
                    dX = positionZ[0] - positionH[0]
                    dY = positionZ[1] - positionH[1]
                    distance = dX * dX + dY * dY
                    if minDist > distance:
                        minDist = distance
                        closestH = [positionH[0], positionH[1]]
                        closestIdH = idH
            nextGlobalPosition.mapClosestZH[idZ] = closestIdH
            nextGlobalPosition.mapZombies[idZ] = self.go_to_target(positionZ[0], positionZ[1], closestH[0], closestH[1],
                                                                   400, minDist, debug)
            if debug:
                print(nextGlobalPosition.mapClosestZH, file=sys.stderr)
            if nextGlobalPosition.mapZombies[idZ][0] == closestH[0] and nextGlobalPosition.mapZombies[idZ][1] == \
                    closestH[1]:
                humanPossiblyKilled[idZ] = closestIdH
                if debug:
                    print("Zombie :", idZ, "try to kill", closestIdH, file=sys.stderr)

        # 2. Ash moves towards his target.
        nextGlobalPosition.ash = self.go_to_target(self.ash[0], self.ash[1], position_target[0], position_target[1],
                                                   1000,
                                                   None, debug)

        # 3. Any zombie within a 2000 unit range around Ash is destroyed (score updated here)
        zombiesDestroyed = []
        for idZ, positionZ in nextGlobalPosition.mapZombies.items():
            distance = squareDistanceZAsh[idZ]
            if distance <= 4000000:
                zombiesDestroyed.append(idZ)

        # print("Zombies destroyed :", zombiesDestroyed, file=sys.stderr)
        zombieCost = math.pow(len(self.mapHumans), 2) * 10
        # print("Zombie score :", zombieCost, file=sys.stderr)
        fiboScore = self.fibo(len(zombiesDestroyed) + 1)
        for n in range(len(zombiesDestroyed)):
            del nextGlobalPosition.mapZombies[zombiesDestroyed[n]]
            # If a zombie is killed before killing a human, don't eliminate the human.
            if zombiesDestroyed[n] in humanPossiblyKilled:
                del humanPossiblyKilled[zombiesDestroyed[n]]
            nextGlobalPosition.score += zombieCost * fiboScore[n + 2]

        # 4. Zombies eat any human they share coordinates with.
        countHumanKilled = 0
        for idH, positionH in self.mapHumans.items():
            humanKilled = False
            for idZ, idHK in humanPossiblyKilled.items():
                if idH == idHK:
                    # print(idH, "killed", file=sys.stderr)
                    humanKilled = True
                    countHumanKilled += 1
                    break
            if not humanKilled:
                nextGlobalPosition.mapHumans[idH] = positionH
        if debug:
            print(self.score, "-", nextGlobalPosition.score, "-", zombiesDestroyed, "-", zombieCost * countHumanKilled,
                  file=sys.stderr)

        nextGlobalPosition.score += self.score

        # Score less if humans are killed
        nextGlobalPosition.score -= 8 * countHumanKilled

        # Put the score to 0 if all humans are killed
        if len(nextGlobalPosition.mapHumans) == 0:
            nextGlobalPosition.score = 0

        return nextGlobalPosition

    def finalPosition(self):
        return len(self.mapHumans) == 0 or len(self.mapZombies) == 0

    def fibo(self, max_index):
        fib = [0, 1]
        for n in range(2, max_index + 1):
            fib.append(fib[n - 1] + fib[n - 2])
        return fib

    def go_to_target(self, from_x, from_y, to_x, to_y, step_size, square_distance, debug):
        if square_distance is None:
            d_x = from_x - to_x
            d_y = from_y - to_y
            distance = math.sqrt(d_x * d_x + d_y * d_y)
        else:
            distance = math.sqrt(square_distance)

        if distance <= step_size:
            return [to_x, to_y]
        else:
            direction = [to_x - from_x, to_y - from_y]
            direction_normalized = [direction[0] / distance, direction[1] / distance]
            # if debug:
            #     print(distance, direction, file=sys.stderr)
            return [math.floor(from_x + direction_normalized[0] * step_size),
                    math.floor(from_y + direction_normalized[1] * step_size)]


# Global variables
width = 16000
height = 9000

# Game loop
while True:

    initGlobalPosition = GlobalPosition()

    # Get main player information
    x, y = [int(i) for i in input().split()]
    killer = Human(x, y, 0)
    initGlobalPosition.ash = [x, y]

    # Get humans positions
    humans = []
    minX = width
    maxX = 0
    minY = height
    maxY = 0
    human_count = int(input())
    for i in range(human_count):
        human_id, human_x, human_y = [int(j) for j in input().split()]
        minX = max(0, human_x - 2000) if human_x < minX else minX
        maxX = min(width, human_x + 2000) if human_x > maxX else maxX
        minY = max(0, human_y - 2000) if human_y < minY else minY
        maxY = min(height, human_y + 2000) if human_y > maxY else maxY
        humans.append(Human(human_x, human_y, human_id))
        initGlobalPosition.mapHumans[human_id] = [human_x, human_y]

    # Get zombies positions
    zombies = []
    zombie_count = int(input())
    for i in range(zombie_count):
        zombie_id, zombie_x, zombie_y, zombie_xnext, zombie_ynext = [int(j) for j in input().split()]
        zombies.append(Zombie(zombie_x, zombie_y, zombie_id, zombie_xnext, zombie_ynext))
        initGlobalPosition.mapZombies[zombie_id] = [zombie_x, zombie_y]

    initGlobalPosition.computeNextGlobalPosition(initGlobalPosition.ash, True)

    # Compute a list of path to test
    splitH = 10
    splitW = 10
    print(minX, maxX, maxX - minX, "|", minY, maxY, maxY - minY, file=sys.stderr)
    stepH = int((maxY - minY) / splitH)
    stepW = int((maxX - minX) / splitW)
    targets = []
    print(stepH, "|", stepW, file=sys.stderr)
    for i in range(splitW + 1):
        xT = minX + i * stepW
        for j in range(splitH + 1):
            yT = minY + j * stepH
            targets.append([xT, yT])

    # pr = cProfile.Profile()
    # pr.enable()

    print("Number of targets to test:", len(targets), file=sys.stderr)
    bestScore = -100000
    bestTurn = 10000
    bestTarget = []
    for path in targets:
        debug = False
        if path[0] == 8000 and path[1] == 4500:
            debug = False
        nextGlobalPosition = initGlobalPosition.computeNextGlobalPosition(path, debug)
        final_turn = 0
        for turn in range(15):
            nextGlobalPosition = nextGlobalPosition.computeNextGlobalPosition(path, debug)
            final_turn = turn
            if nextGlobalPosition.finalPosition():
                print(path, ": in", turn + 3, " t, sc", nextGlobalPosition.score, file=sys.stderr)
                break

        if nextGlobalPosition.score > bestScore:
            print(path, ": sc", nextGlobalPosition.score, file=sys.stderr)
            bestScore = nextGlobalPosition.score
            bestTarget = path
            bestTurn = final_turn + 3
        if nextGlobalPosition.score == bestScore and final_turn + 3 < bestTurn:
            print(path, ": sc", nextGlobalPosition.score, file=sys.stderr)
            bestScore = nextGlobalPosition.score
            bestTarget = path
            bestTurn = final_turn + 3
    print("Best target found:", bestTarget, "finish with score", bestScore, "in turn", bestTurn, file=sys.stderr)

    # pr.disable()
    # s = io.StringIO()
    # ps = pstats.Stats(pr, stream=s)
    # ps.print_stats()
    # print(s.getvalue(), file=sys.stderr)

    # Write best destination
    print("%d" % bestTarget[0], "%d" % bestTarget[1])
