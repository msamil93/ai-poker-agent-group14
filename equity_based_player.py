from pypokerengine.players import BasePokerPlayer
import random

CardRanks = "23456789TJQKA"
CardSuits = "CDHS"

class EquityBasedPlayer(BasePokerPlayer):
    def __init__(self, trials=100, call_threshold=0.5, raise_threshold=0.7):
        self.trials = trials
        self.call_threshold = call_threshold
        self.raise_threshold = raise_threshold

    def declare_action(self, valid_actions, hole_cards, game_state):
        community = game_state['community_card']
        num_players = len(game_state['seats'])
        equity = self.estimate_equity(hole_cards, community, num_players)

        raise_info = next((a for a in valid_actions if a['action'] == 'raise'), None)
        call_info = next((a for a in valid_actions if a['action'] == 'call'), None)

        if equity >= self.raise_threshold and raise_info:
            return 'raise'
        elif equity >= self.call_threshold and call_info:
            return 'call'
        else:
            return 'fold'

    def estimate_equity(self, hole_cards, board_cards, player_count):
        full_deck = [suit + rank for rank in CardRanks for suit in CardSuits 
                     if (suit + rank) not in set(hole_cards + board_cards)]
        wins, ties = 0, 0

        for _ in range(self.trials):
            drawn = random.sample(full_deck, (player_count - 1) * 2 + (5 - len(board_cards)))
            opponents = [drawn[2 * i:2 * i + 2] for i in range(player_count - 1)]
            full_board = board_cards + drawn[(player_count - 1) * 2:]

            my_score = self.evaluate_hand(hole_cards + full_board)
            opp_scores = [self.evaluate_hand(op + full_board) for op in opponents]
            top = max([my_score] + opp_scores)

            if my_score == top:
                ties += 1 if opp_scores.count(top) else 0
                wins += 0 if opp_scores.count(top) else 1

        return (wins + 0.5 * ties) / self.trials

    def evaluate_hand(self, cards):
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
