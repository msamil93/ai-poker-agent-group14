from pypokerengine.players import BasePokerPlayer
import random

CardRanks = "23456789TJQKA"
CardSuits = "CDHS"

class Group14Player(BasePokerPlayer):
    def __init__(self,
                 monte_carlo_trials=100,
                 aggression_thresholds=(0.70, 0.60, 0.57, 0.53),
                 call_threshold_margin=0.045,
                 raise_stack_fraction=0.55,
                 bluff_probability=0.04):
        self.MonteCarloTrials = monte_carlo_trials
        self.AggressionThresholds = aggression_thresholds
        self.CallThresholdMargin = call_threshold_margin
        self.RaiseStackFraction = raise_stack_fraction
        self.BluffProbability = bluff_probability

    def declare_action(self, valid_actions, hole_cards, game_state):
        street_index = {'preflop': 0, 'flop': 1, 'turn': 2, 'river': 3}[game_state['street']]
        pot_size = game_state['pot']['main']['amount']
        stack = next(player['stack'] for player in game_state['seats'] if player['uuid'] == self.uuid)

        equity = self._estimate_equity(hole_cards, game_state['community_card'], len(game_state['seats']))

        call_info = next((a for a in valid_actions if a['action'] == 'call'), None)
        call_amount = call_info.get('amount', 0) if call_info else 0
        pot_odds = call_amount / (pot_size + call_amount) if call_amount else 0

        if equity - pot_odds < self.CallThresholdMargin:
            return 'fold'

        raise_info = next((a for a in valid_actions if a['action'] == 'raise'), None)
        if raise_info and (equity >= self.AggressionThresholds[street_index] or random.random() < self.BluffProbability):
            raise_range = raise_info.get('amount')
            if isinstance(raise_range, dict):
                min_raise, max_raise = raise_range['min'], raise_range['max']
                raise_amount = int(min(self.RaiseStackFraction * stack, 0.8 * pot_size, max_raise))
                return ('raise', max(min_raise, raise_amount))
            else:
                return 'raise'

        return 'call'

    def _estimate_equity(self, hole_cards, board_cards, player_count):
        full_deck = [suit + rank for rank in CardRanks for suit in CardSuits if (suit + rank) not in set(hole_cards + board_cards)]
        wins, ties = 0, 0

        for _ in range(self.MonteCarloTrials):
            drawn = random.sample(full_deck, (player_count - 1) * 2 + (5 - len(board_cards)))
            opponents = [drawn[2 * i:2 * i + 2] for i in range(player_count - 1)]
            full_board = board_cards + drawn[(player_count - 1) * 2:]

            score = self._evaluate_hand(hole_cards + full_board)
            opp_scores = [self._evaluate_hand(op + full_board) for op in opponents]
            top = max([score] + opp_scores)

            if score == top:
                split = opp_scores.count(top)
                if split == 0:
                    wins += 1
                else:
                    ties += 1 / (split + 1)

        return (wins + ties) / self.MonteCarloTrials

    def _evaluate_hand(self, cards):
        values = [CardRanks.index(card[1]) for card in cards]
        suits = [card[0] for card in cards]

        value_counts = sorted([values.count(v) for v in set(values)], reverse=True)
        flush_suit = next((s for s in CardSuits if suits.count(s) >= 5), None)
        flush_values = sorted((v for v, c in zip(values, cards) if c[0] == flush_suit), reverse=True) if flush_suit else []

        unique_vals = sorted(set(values))
        if 12 in unique_vals:
            unique_vals = [-1] + unique_vals
        straight = any(unique_vals[i + 4] - unique_vals[i] == 4 for i in range(len(unique_vals) - 4))

        straight_flush = flush_suit and any(
            flush_values[i + 4] - flush_values[i] == 4
            for i in range(len(flush_values) - 4)
        )

        if straight_flush and max(flush_values[-5:]) == 12: return 9
        if straight_flush: return 8
        if value_counts[0] == 4: return 7
        if value_counts[0] == 3 and value_counts[1] == 2: return 6
        if flush_suit: return 5
        if straight: return 4
        if value_counts[0] == 3: return 3
        if value_counts[0] == 2 and value_counts[1] == 2: return 2
        if value_counts[0] == 2: return 1
        return 0

    def receive_game_start_message(self, game_info): pass
    def receive_round_start_message(self, round_count, hole_cards, seats): pass
    def receive_street_start_message(self, street, game_state): pass
    def receive_game_update_message(self, action, game_state): pass
    def receive_round_result_message(self, winners, hand_info, game_state): pass

def setup_ai():
    return Group14Player()