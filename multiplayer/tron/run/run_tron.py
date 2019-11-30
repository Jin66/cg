import numpy as np

from multiplayer.tron.bots.basic_bot import BasicBot
from multiplayer.tron.bots.nn_bot import NNBot, InputMode
from multiplayer.tron.engine import GameEngine

if __name__ == '__main__':

    w1 = np.array(
        [2.85279164, 1.93618624, 1.0547554, 1.39014364, - 4.56926338, 2.39373373,
         1.10432385, 2.94699784, - 2.12454727, 3.85237977, - 2.79221437, - 4.50583572,
         0.04652633, 0.22887937, - 0.85909617, 2.5549219, - 2.49903568, - 3.32639124,
         - 3.59052225, - 2.45729888, 3.2055761, - 3.60647563, 2.78085956, 3.59177621,
         - 1.04766775, - 1.10584241, 4.35052141, 3.48702676, 4.04013062, 2.23195732,
         - 0.81632495, - 3.50685916, 4.35052141, 3.48702676, 4.04013062, 2.23195732,
         - 0.81632495, - 3.50685916, 4.35052141, 3.48702676, 4.04013062, 2.23195732,
         - 0.81632495, - 3.50685916, 4.35052141, 3.48702676, 4.04013062, 2.23195732]
    )

    w2 = np.array(
        [-1.66881079, -1.2762851, 2.87003592, 2.34478161, -12.15087071,
         -0.12754752, -0.14979787, -3.32554546, 1.90426005, 0.20058309,
         1.26654878, -3.71082981, -1.59254577, 1.02956717, 2.75967048,
         -7.0029344, 3.3381034, 3.12634522, 1.84442842, 0.63765788,
         6.71882033, -8.22438905, -1.5904121, 5.23726244, 5.05598949,
         -1.94597497, 2.08656251, 2.64218847, -1.0364427, 5.20506278,
         -4.08777149, 6.06590041, 1.68931708, -4.29240033, -1.57182941,
         1.85658392, 0.7052871, 1.77874015, 2.18145781, 8.5710168,
         -1.90419708, -3.88373893, -1.20608509, 0.51515518, -1.12798507,
         8.37242986, -3.76990631, -12.46569119]
    )

    bot1 = NNBot(weights=w1, input_modes=[InputMode.DistanceSquare, InputMode.DistanceDiag, InputMode.AccessibleCells])
    bot2 = NNBot(weights=w2, input_modes=[InputMode.DistanceSquare, InputMode.DistanceDiag, InputMode.AccessibleCells])

    botRandom1 = NNBot(can_lose_stupidly=False, input_modes=[InputMode.DistanceSquare, InputMode.BotsPosition])
    botRandom2 = NNBot(can_lose_stupidly=False, input_modes=[InputMode.DistanceSquare, InputMode.BotsPosition])

    number_games = 2
    for i in range(number_games):
        game_engine = GameEngine(debug=True)
        results = game_engine.run([botRandom1, botRandom2, BasicBot()])
        print(results)