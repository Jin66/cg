import sys
import math
import re

sizeAlphabet = 27
letters = {" ": 0, "A": 1, "B": 2, "C": 3, "D": 4,
           "E": 5, "F": 6, "G": 7, "H": 8, "I": 9,
           "J": 10, "K": 11, "L": 12, "M": 13,
           "N": 14, "O": 15, "P": 16, "Q": 17,
           "R": 18, "S": 19, "T": 20, "U": 21,
           "V": 22, "W": 23, "X": 24, "Y": 25, "Z": 26}

magic_phrase = input()
print(magic_phrase, file=sys.stderr)

# Find repetitive pattern
pattern = "(.+?)\\1+"
possibleLoops = []
patternsFound = re.s(pattern, magic_phrase)
for patternFound in patternsFound:
    print("Group: ",
          patternFound.group(1),
          patternFound.start(1),
          patternFound.end(1),
          patternFound.end(0),
          file=sys.stderr)

# Find repetitive pattern
allmatch = re.findall("(.+?)\\1+", magic_phrase)
print(allmatch, file=sys.stderr)


# magic_number = [letters[letter] for letter in magic_phrase]
# print(magic_number,file= sys.stderr)

class GameState:
    runes = [0 for i in range(30)]

    def __init__(self, gameState=None):
        if gameState:
            runes = [gameState.runes[i] for i in range(30)]

    def __repr__(self):
        output = ""
        for rune in runes:
            output += str(rune)
        return output


def costLetter(runeValue, letter):
    index = letters[letter]
    c1 = (index - runeValue) % sizeAlphabet
    c2 = (runeValue - index) % sizeAlphabet
    if c1 >= c2:
        return -c2
    else:
        return c1


initGameState = GameState()
runes = [0 for i in range(30)]
currentPosition = 0
output = ""
for letter in magic_phrase:
    minCost = 10000
    bestOutput = ""
    bestMove = 0
    bestChange = 0
    for runeId in range(30):
        move = runeId - currentPosition
        costletter = costLetter(runes[runeId], letter)
        # print(runeId, move, costletter, file=sys.stderr)
        if abs(move) + abs(costletter) < minCost:
            # print("Best: ", runeId, move, costletter, file=sys.stderr)
            minCost = abs(move) + abs(costletter)
            bestOutput = ""
            if move < 0:
                bestOutput += "<" * -move
            elif move > 0:
                bestOutput += ">" * move
            bestMove = move
            if costletter < 0:
                bestOutput += "-" * -costletter
            elif costletter > 0:
                bestOutput += "+" * costletter
            bestChange = (runes[runeId] + costletter) % sizeAlphabet
    # print(bestOutput, bestMove, minCost, bestChange, file=sys.stderr)
    output += bestOutput + "."
    runes[currentPosition + bestMove] = bestChange
    currentPosition += bestMove
    # print(output, currentPosition, file=sys.stderr)

# print("------------->+++++++[<.+.->+]")
# print("+>-[<.>-]")
print(output)
