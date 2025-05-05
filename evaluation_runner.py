from pypokerengine.api.game import setup_config, start_poker
from custom_player import CustomPlayer
from raise_player import RaisedPlayer
from randomplayer import RandomPlayer
from call_player import CallPlayer
from loose_player import LoosePlayer
from tight_player import TightPlayer
from passive_player import PassivePlayer
from equity_based_player import EquityBasedPlayer

def run_match(agent1, agent2, name1, name2, num_games=50):
    agent1_wins = 0
    agent2_wins = 0

    for i in range(num_games):
        config = setup_config(max_round=1000, initial_stack=10000, small_blind_amount=20)
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
        #(Group14Player, RandomPlayer, "Group14", "Random"),
        # (Group14Player, RaisedPlayer, "Group14", "Raised"),
        # (Group14Player, CallPlayer, "Group14", "Call"),
        #(Group14Player, LoosePlayer, "Group14", "Loose"),
        #(Group14Player, TightPlayer, "Group14", "Tight"),
        (CustomPlayer, CustomPlayer, "Group14", "Self"),
        (Customplayer, EquityBasedPlayer, "Group14", "equityBased")
    ]

    for agent1, agent2, name1, name2 in matchups:
        print(f"Running: {name1} vs {name2}")
        wins1, wins2, total = run_match(agent1, agent2, name1, name2, num_games=500)
        results.append((name1 + " vs " + name2, wins1, wins2, total))

    print("\n=== Match Results ===")
    print(f"{'Matchup':<25} {'Agent1 Wins':<12} {'Agent2 Wins':<12} {'Total Games'}")
    for row in results:
        matchup, w1, w2, total = row
        print(f"{matchup:<25} {w1:<12} {w2:<12} {total}")

if __name__ == "__main__":
    main()
