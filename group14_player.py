from pypokerengine.players import BasePokerPlayer
import random

class Group14Player(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):
        # Rank order from weakest to strongest
        rank_order = '23456789TJQKA'
        community = round_state['community_card']

        # Estimate hand strength: returns 2 (strong), 1 (medium), 0 (weak)
        def estimate_hand_strength(cards):
            values = []
            for card in cards:
                rank = card[1:]  # Assumes card like 'H9', 'DA'
                if rank not in rank_order:
                    continue
                values.append(rank_order.index(rank))
            values = sorted(values, reverse=True)

            if len(cards) >= 2 and cards[0][1:] == cards[1][1:]:
                return 2  # pair → strong
            elif values and values[0] >= rank_order.index('J'):
                return 1  # J, Q, K, A → medium
            else:
                return 0  # otherwise → weak

        # Monte Carlo simulation
        def monte_carlo_win_rate(my_cards, known_community, simulations=50):
            full_deck = [s + r for r in '23456789TJQKA' for s in 'CDHS']
            used = set(my_cards + known_community)
            deck = [card for card in full_deck if card not in used]

            wins = 0
            for _ in range(simulations):
                sample = random.sample(deck, 2 + (5 - len(known_community)))
                opp_hole = sample[:2]
                rem_comm = sample[2:]
                full_comm = known_community + rem_comm

                my_score = estimate_hand_strength(my_cards)
                opp_score = estimate_hand_strength(opp_hole)

                if my_score >= opp_score:
                    wins += 1

            return wins / simulations

        # Score function using A*-style evaluation
        def score(action, win_rate):
            # Increased penalty for fold to encourage more play
            cost = {'fold': -15, 'call': -5, 'raise': -10}
            return win_rate * 100 + cost[action]

        # Estimate win rate
        win_rate = monte_carlo_win_rate(hole_card, community)

        # Evaluate all valid actions
        action_scores = {}
        for action in ['fold', 'call', 'raise']:
            if any(a['action'] == action for a in valid_actions):
                action_scores[action] = score(action, win_rate)

        # Pick action with max score
        best_action = max(action_scores, key=action_scores.get)
        return best_action

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

def setup_ai():
    return Group14Player()
