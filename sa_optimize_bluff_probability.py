import random
import copy
import csv
import math
from evaluation_runner import run_match
from group14_player import Group14Player
from call_player import CallPlayer
from raise_player import RaisedPlayer
from equity_based_player import EquityBasedPlayer

# Define opponent agents used in evaluation
opponents = {
    "CallPlayer": CallPlayer,
    "RaisedPlayer": RaisedPlayer,
    "EquityBasedPlayer": EquityBasedPlayer,
}

def create_agent(params):
    return Group14Player(
        aggression_thresholds=tuple(params["AggressionThresholds"]),
        call_threshold_margin=params["CallThresholdMargin"],
        bluff_probability=params["BluffProbability"]
    )

def average_winrate(agent_params, num_games=20):
    total_wr = 0
    for name, Opponent in opponents.items():
        wins, losses, total = run_match(lambda: create_agent(agent_params), Opponent, "Optimized", name, num_games)
        wr = wins / total
        total_wr += wr
    return total_wr / len(opponents)

def optimize_bluff_probability_sa(iterations=50, base_delta=0.02, initial_temp=1.0, cooling_rate=0.95):
    search_min, search_max = 0.02, 0.06
    current_val = 0.05
    temperature = initial_temp

    fixed_params = {
        "AggressionThresholds": [0.71, 0.61, 0.57, 0.55],
        "CallThresholdMargin": 0.045,
        "BluffProbability": current_val
    }

    current_score = best_score = average_winrate(fixed_params, num_games=50)
    best_val = current_val

    log = [(0, current_val, current_score, temperature)]
    print(f"[T0] BluffProb = {current_val:.3f}, Score = {current_score:.4f}, Temp = {temperature:.4f}, (initial)")

    for i in range(1, iterations + 1):
        candidate_params = copy.deepcopy(fixed_params)

        # Delta scaled by current temperature
        scaled_delta = base_delta * temperature
        change = random.uniform(-scaled_delta, scaled_delta)
        new_val = round(max(search_min, min(search_max, current_val + change)), 3)
        candidate_params["BluffProbability"] = new_val
        new_score = average_winrate(candidate_params, num_games=50)
        score_diff = new_score - current_score

        accept = False
        if score_diff >= 0:
            accept = True
        else:
            probability = math.exp(score_diff / temperature)
            if random.random() < probability:
                accept = True

        if accept:
            current_val = new_val
            current_score = new_score
            fixed_params["BluffProbability"] = current_val
            if new_score > best_score:
                best_score = new_score
                best_val = new_val

        temperature *= cooling_rate
        log.append((i, current_val, current_score, round(temperature, 5)))
        print(f"[T{i}] BluffProb = {current_val:.3f}, Score = {current_score:.4f}, Temp = {temperature:.4f}, {'\u2713' if accept else '\u2717'}")

    filename = f"sa_bluff_probability.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Iteration", "BluffProbability", "AverageWinrate", "Temperature"])
        writer.writerows(log)

    print(f"\nSaved: {filename}")
    print(f"Best BluffProbability = {best_val}, Winrate = {best_score:.4f}")

if __name__ == "__main__":
    optimize_bluff_probability_sa(iterations=50)