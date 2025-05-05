import random
import copy
from evaluation_runner import run_match
from group14_player import Group14Player
from call_player import CallPlayer
from raise_player import RaisedPlayer
from loose_player import LoosePlayer
from tight_player import TightPlayer
from randomplayer import RandomPlayer

# Opponent agents used for evaluation
opponents = {
    "CallPlayer": CallPlayer,
    "RaisedPlayer": RaisedPlayer,
    "RandomPlayer": RandomPlayer,
}

# Starting parameters — conservative values based on intuition
best_params = {
    "AggressionThresholds": [0.75, 0.65, 0.60, 0.55],
    "CallThresholdMargin": 0.02,
    "RaiseStackFraction": 0.52,
    "BluffProbability": 0.01,
}

def create_agent(params):
    return Group14Player(
        aggression_thresholds=tuple(params["AggressionThresholds"]),
        call_threshold_margin=params["CallThresholdMargin"],
        raise_stack_fraction=params["RaiseStackFraction"],
        bluff_probability=params["BluffProbability"]
    )

def perturb(params, discount=0.5):
    new_params = copy.deepcopy(params)
    key = random.choice(list(params.keys()))

    if key == "AggressionThresholds":
        index = random.randint(0, 3)
        change = random.uniform(-0.05, 0.05) * discount
        new_params["AggressionThresholds"][index] = round(
            max(0.01, min(0.99, new_params["AggressionThresholds"][index] + change)), 3)
    else:
        change = random.uniform(-0.05, 0.05) * discount
        new_params[key] = round(max(0.001, min(0.999, new_params[key] + change)), 3)

    return new_params

def average_winrate(agent_params, num_games=20):
    total_wr = 0
    for name, Opponent in opponents.items():
        wins, losses, total = run_match(lambda: create_agent(agent_params), Opponent, "Optimized", name, num_games)
        wr = wins / total
        total_wr += wr
    return total_wr / len(opponents)

def hill_climb(iterations=100, discount=0.5):
    global best_params
    best_score = average_winrate(best_params)
    print("Initial avg winrate:", round(best_score, 4))

    log_lines = []
    log_lines.append(best_score)

    for i in range(iterations):
        candidate = perturb(best_params, discount=discount)
        score = average_winrate(candidate)

        print(f"Iteration {i+1}: score={round(score,4)} | current best={round(best_score,4)}")
        log_lines.append(score)

        if score > best_score:
            print("  ➤ New parameters accepted.")
            best_score = score
            best_params = candidate

    print("\nBest configuration found:")
    for k, v in best_params.items():
        print(f"{k}: {v}")
    print("Final average winrate:", round(best_score, 4))

    with open("hill_climbing_log.csv", "w") as f:
        f.write("Iteration,Score\n")
        for idx, score in enumerate(log_lines):
            f.write(f"{idx},{score}\n")

if __name__ == "__main__":
    hill_climb(iterations=100, discount=0.5)