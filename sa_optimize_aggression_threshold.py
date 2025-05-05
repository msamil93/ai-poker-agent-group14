import random
import copy
import csv
import math
from evaluation_runner import run_match
from group14_player import Group14Player
from call_player import CallPlayer
from raise_player import RaisedPlayer
from randomplayer import RandomPlayer
from equity_based_player import EquityBasedPlayer

# Opponent agents used for evaluation
opponents = {
    "CallPlayer": CallPlayer,
    "RaisedPlayer": RaisedPlayer,
    "EquityBasedPlayer": EquityBasedPlayer
}

def create_agent(params):
    return Group14Player(
        aggression_thresholds=tuple(params["AggressionThresholds"]),
        call_threshold_margin=params["CallThresholdMargin"],
        bluff_probability=params["BluffProbability"]
    )

def average_winrate(agent_params, num_games=100):
    total_wr = 0
    for name, Opponent in opponents.items():
        wins, losses, total = run_match(lambda: create_agent(agent_params), Opponent, "Optimized", name, num_games)
        wr = wins / total
        total_wr += wr
    return total_wr / len(opponents)

def optimize_aggression_index_sa(index, iterations=100, delta=0.03, initial_temp=1.0, cooling_rate=0.97):
    # Arama sınırları her index için ayrı
    bounds = {
        0: (0.6, 0.8),
        1: (0.6, 0.7),
        2: (0.5, 0.7),
        3: (0.5, 0.6),
    }
    search_min, search_max = bounds[index]
    current_val = search_min
    temperature = initial_temp

    # Fixed parameters
    fixed_params = {
        "AggressionThresholds": [0.5, 0.5, 0.5, 0.5],
        "CallThresholdMargin": 0.02,
        "BluffProbability": 0.1,
    }
    fixed_params["AggressionThresholds"][index] = current_val
    current_score = best_score = average_winrate(fixed_params, num_games=50)
    best_val = current_val

    log = [(0, current_val, current_score, temperature)]
    print(f"[T0] Threshold[{index}] = {current_val:.3f}, Score = {current_score:.4f}, Temp = {temperature:.4f}, ✔ (initial)")

    for i in range(1, iterations + 1):
        candidate_params = copy.deepcopy(fixed_params)

        change = random.uniform(-delta, delta)
        new_val = round(max(search_min, min(search_max, current_val + change)), 3)
        candidate_params["AggressionThresholds"][index] = new_val
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
            fixed_params["AggressionThresholds"][index] = current_val
            if new_score > best_score:
                best_score = new_score
                best_val = new_val

        temperature *= cooling_rate
        log.append((i, current_val, current_score, round(temperature, 5)))
        print(f"[T{i}] Threshold[{index}] = {current_val:.3f}, Score = {current_score:.4f}, Temp = {temperature:.4f}, {'✔' if accept else '✘'}")

    filename = f"sa_aggression_{index}.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Iteration", f"Aggression[{index}]", "AverageWinrate", "Temperature"])
        writer.writerows(log)

    print(f"\nSaved: {filename}")
    print(f"Best Aggression[{index}] = {best_val}, Winrate = {best_score:.4f}")

if __name__ == "__main__":
    print(f"\n=== Simulated Annealing: AggressionThreshold[1] ===")
    optimize_aggression_index_sa(1, iterations=30)