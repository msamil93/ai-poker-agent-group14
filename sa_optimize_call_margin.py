import random
import copy
import csv
import math
from evaluation_runner import run_match
from group14_player import Group14Player
from call_player import CallPlayer
from raise_player import RaisedPlayer
from equity_based_player import EquityBasedPlayer

# Opponent pool to evaluate against
opponents = {
    "CallPlayer": CallPlayer,
    "RaisedPlayer": RaisedPlayer,
    "EquityBasedPlayer": EquityBasedPlayer,
}

# Build agent using given parameters
def create_agent(params):
    return Group14Player(
        aggression_thresholds=tuple(params["AggressionThresholds"]),
        call_threshold_margin=params["CallThresholdMargin"],
        bluff_probability=params["BluffProbability"]
    )

# Average winrate across all opponent agents
def average_winrate(agent_params, num_games=20):
    total_wr = 0
    for name, Opponent in opponents.items():
        wins, losses, total = run_match(lambda: create_agent(agent_params), Opponent, "Optimized", name, num_games)
        total_wr += wins / total
    return total_wr / len(opponents)

# Simulated annealing to optimize CallThresholdMargin
def optimize_call_margin_sa(iterations=50, base_delta=0.01, initial_temp=1.0, cooling_rate=0.97):
    search_min, search_max = 0.03, 0.05
    current_val = search_min
    temperature = initial_temp

    fixed_params = {
        "AggressionThresholds": [0.71, 0.61, 0.57, 0.55],
        "CallThresholdMargin": current_val,
        "BluffProbability": 0.1
    }

    current_score = best_score = average_winrate(fixed_params, num_games=50)
    best_val = current_val
    log = [(0, current_val, current_score, temperature)]
    print(f"[T0] CallMargin = {current_val:.3f}, Score = {current_score:.4f}, Temp = {temperature:.4f} (initial)")

    for i in range(1, iterations + 1):
        candidate_params = copy.deepcopy(fixed_params)

        # Propose a new value by perturbing current value
        scaled_delta = base_delta * temperature
        change = random.uniform(-scaled_delta, scaled_delta)
        new_val = round(max(search_min, min(search_max, current_val + change)), 3)
        candidate_params["CallThresholdMargin"] = new_val

        # Evaluate new parameter set
        new_score = average_winrate(candidate_params, num_games=50)
        score_diff = new_score - current_score

        # Decide whether to accept the new value
        accept = score_diff >= 0 or random.random() < math.exp(score_diff / temperature)

        if accept:
            current_val = new_val
            current_score = new_score
            fixed_params["CallThresholdMargin"] = current_val
            if new_score > best_score:
                best_score = new_score
                best_val = new_val

        temperature *= cooling_rate
        log.append((i, current_val, current_score, round(temperature, 5)))
        print(f"[T{i}] CallMargin = {current_val:.3f}, Score = {current_score:.4f}, Temp = {temperature:.4f}, {'✓' if accept else '✗'}")

    # Save log to CSV
    filename = "sa_call_threshold_margin.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Iteration", "CallThresholdMargin", "AverageWinrate", "Temperature"])
        writer.writerows(log)

    print(f"\nSaved: {filename}")
    print(f"Best CallThresholdMargin = {best_val}, Winrate = {best_score:.4f}")

if __name__ == "__main__":
    optimize_call_margin_sa(iterations=50)