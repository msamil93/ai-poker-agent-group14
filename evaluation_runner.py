from pypokerengine.api.game import setup_config, start_poker
from group14_player import Group14Player
from raise_player import RaisedPlayer
from randomplayer import RandomPlayer

def run_match(agent1, agent2, name1, name2, num_games=100):
    agent1_wins = 0
    agent2_wins = 0

    for i in range(num_games):
        config = setup_config(max_round=50, initial_stack=10000, small_blind_amount=20)
        config.register_player(name=name1, algorithm=agent1())
        config.register_player(name=name2, algorithm=agent2())
        result = start_poker(config, verbose=0)

        final_stacks = {p['name']: p['stack'] for p in result['players']}
        if final_stacks[name1] > final_stacks[name2]:
            agent1_wins += 1
        elif final_stacks[name2] > final_stacks[name1]:
            agent2_wins += 1
        # draws are ignored

    return agent1_wins, agent2_wins, num_games


def main():
    results = []

    matchups = [
        (Group14Player, RandomPlayer, "Group14", "Random"),
        (Group14Player, RaisedPlayer, "Group14", "Raised")
    ]

    for agent1, agent2, name1, name2 in matchups:
        print(f"Running: {name1} vs {name2}")
        wins1, wins2, total = run_match(agent1, agent2, name1, name2, num_games=100)
        results.append((name1 + " vs " + name2, wins1, wins2, total))

    print("\n=== Match Results ===")
    print(f"{'Matchup':<25} {'Agent1 Wins':<12} {'Agent2 Wins':<12} {'Total Games'}")
    for row in results:
        matchup, w1, w2, total = row
        print(f"{matchup:<25} {w1:<12} {w2:<12} {total}")

if __name__ == "__main__":
    main()
