import random
import copy
import csv
from evaluation_runner import run_match
from group14_player import Group14Player
from call_player import CallPlayer
from raise_player import RaisedPlayer
from randomplayer import RandomPlayer

# Agents used to evaluate training performance
opponents = {
    "CallPlayer": CallPlayer,
    "RaisedPlayer": RaisedPlayer,
    "RandomPlayer": RandomPlayer,
}

# Random initial configuration
best_params = {
    "AggressionThresholds": [round(random.uniform(0.4, 0.9), 3) for _ in range(4)],
    "CallThresholdMargin": round(random.uniform(0.01, 0.2), 3),
    "RaiseStackFraction": round(random.uniform(0.2, 0.9), 3),
    "BluffProbability": round(random.uniform(0.0, 0.2), 3),
}

# Delta values per parameter (adaptive)
param_deltas = {
    "AggressionThresholds": [0.05, 0.05, 0.05, 0.05],
    "CallThresholdMargin": 0.05,
    "RaiseStackFraction": 0.05,
    "BluffProbability": 0.05,
}

print("Initial parameters:", best_params)

def create_agent(params):
    return Group14Player(
        aggression_thresholds=tuple(params["AggressionThresholds"]),
        call_threshold_margin=params["CallThresholdMargin"],
        raise_stack_fraction=params["RaiseStackFraction"],
        bluff_probability=params["BluffProbability"]
    )

def perturb(params):
    new_params = copy.deepcopy(params)
    key = random.choice(list(params.keys()))

    if key == "AggressionThresholds":
        index = random.randint(0, 3)
        delta = param_deltas[key][index]
        change = random.uniform(-delta, delta)
        new_val = round(max(0.01, min(0.99, new_params[key][index] + change)), 3)
        new_params[key][index] = new_val
        desc = f"{key}[{index}] → {new_val}"
    else:
        delta = param_deltas[key]
        change = random.uniform(-delta, delta)
        new_val = round(max(0.001, min(0.999, new_params[key] + change)), 3)
        new_params[key] = new_val
        desc = f"{key} → {new_val}"

    return new_params, desc, key

def average_winrate(agent_params, num_games=20):
    total_wr = 0
    for name, Opponent in opponents.items():
        wins, losses, total = run_match(lambda: create_agent(agent_params), Opponent, "Optimized", name, num_games)
        wr = wins / total
        total_wr += wr
    return total_wr / len(opponents)

def hill_climb(iterations=100):
    global best_params
    best_score = average_winrate(best_params)
    print(f"Initial average winrate: {round(best_score, 4)}\n")

    with open("hill_climbing_log.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Iteration", "Score", "Change", "Accepted", "CurrentParams"])

        for i in range(iterations):
            candidate, change_desc, changed_key = perturb(best_params)
            score = average_winrate(candidate)

            accepted = False
            if score > best_score:
                best_score = score
                best_params = candidate
                accepted = True

                # Reduce delta for this param
                if changed_key == "AggressionThresholds":
                    index = int(change_desc.split('[')[1].split(']')[0])
                    param_deltas[changed_key][index] = max(param_deltas[changed_key][index] * 0.9, 0.005)
                else:
                    param_deltas[changed_key] = max(param_deltas[changed_key] * 0.9, 0.005)

                print(f"Iteration {i+1} ➤ New parameters accepted.")
                print("  ↪", change_desc)
                print("  ↪ Winrate:", round(best_score, 4))
                print("  ↪ Current:", best_params)
                print()

            else:
                # Slightly increase delta to allow further exploration
                if changed_key == "AggressionThresholds":
                    index = int(change_desc.split('[')[1].split(']')[0])
                    param_deltas[changed_key][index] = min(param_deltas[changed_key][index] * 1.05, 0.2)
                else:
                    param_deltas[changed_key] = min(param_deltas[changed_key] * 1.05, 0.2)

            writer.writerow([
                i + 1,
                round(score, 4),
                change_desc,
                "YES" if accepted else "NO",
                str(best_params)
            ])

    print("Final best parameters:")
    for k, v in best_params.items():
        print(f"{k}: {v}")
    print("Final average winrate:", round(best_score, 4))


if __name__ == "__main__":
    hill_climb(iterations=100)
