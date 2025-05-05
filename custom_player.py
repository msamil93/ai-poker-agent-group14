from pypokerengine.players import BasePokerPlayer
import random

# Define card ranks and suits used for indexing and evaluations
CardRanks = "23456789TJQKA"
CardSuits = "CDHS"

class CustomPlayer(BasePokerPlayer):
    # Number of simulations used to estimate win probability (higher = more accurate, slower)
    MonteCarloTrials = 100

    # Thresholds to trigger a raise at each stage of the game (preflop, flop, turn, river)
    AggressionThresholds = (0.72, 0.61, 0.57, 0.55)

    # Minimum margin (equity - pot odds) required to justify a call
    CallThresholdMargin = 0.045

    # Probability of bluffing when equity is low
    BluffProbability = 0.04

    def declare_action(self, valid_actions, hole_cards, round_state):
       
        street_index = {'preflop': 0, 'flop': 1, 'turn': 2, 'river': 3}[round_state['street']]

        pot_size = round_state['pot']['main']['amount']

        stack = next(player['stack'] for player in round_state['seats'] if player['uuid'] == self.uuid)

        # Estimate win probability through simulation
        equity = self._estimate_equity(hole_cards, round_state['community_card'], 2))

        # Calculate pot odds for calling
        call_info = next((a for a in valid_actions if a['action'] == 'call'), None)
        call_amount = call_info.get('amount', 0) if call_info else 0
        pot_odds = call_amount / (pot_size + call_amount) if call_amount else 0

        # Fold if the expected gain doesn't beat the margin threshold
        if equity - pot_odds < self.CallThresholdMargin:
            return 'fold'

        # Consider raising if equity is strong or by bluff chance
        raise_info = next((a for a in valid_actions if a['action'] == 'raise'), None)
        if raise_info and (equity >= self.AggressionThresholds[street_index] or random.random() < self.BluffProbability):
            return 'raise'

        # Default to call if none of the above triggers
        return 'call'

    def _estimate_equity(self, hole_cards, board_cards, player_count):
        # Create a deck without known cards
        full_deck = [suit + rank for rank in CardRanks for suit in CardSuits if (suit + rank) not in set(hole_cards + board_cards)]
        wins, ties = 0, 0

        # Run multiple MC simulations by randomly completing the board and assigning opponent hands
        for _ in range(self.MonteCarloTrials):
            drawn = random.sample(full_deck, 2 + (5 - len(board_cards)))
            opponent = drawn[:2]
            full_board = board_cards + drawn[2:]

            # Evaluate both hands
            my_score = self._evaluate_hand(hole_cards + full_board)
            opp_score = self._evaluate_hand(opponent + full_board)

            # Count wins and ties
            if my_score > opp_score:
                wins += 1
            elif my_score == opp_score:
                ties += 0.5

        # Return average expected equity
        return (wins + ties) / self.MonteCarloTrials

    def _evaluate_hand(self, cards):
        # Convert cards to numerical values for easier comparison
        values = [CardRanks.index(card[1]) for card in cards]
        suits = [card[0] for card in cards]

        # Count how many times each value appears
        value_counts = sorted([values.count(v) for v in set(values)], reverse=True)

        # Check for flush possibility
        flush_suit = next((s for s in CardSuits if suits.count(s) >= 5), None)
        flush_values = sorted((v for v, c in zip(values, cards) if c[0] == flush_suit), reverse=True) if flush_suit else []

        # Detect straight by checking for 5 consecutive values (treat Ace as low as well)
        unique_vals = sorted(set(values))
        if 12 in unique_vals:
            unique_vals = [-1] + unique_vals
        straight = any(unique_vals[i + 4] - unique_vals[i] == 4 for i in range(len(unique_vals) - 4))

        # Check for straight flush
        straight_flush = flush_suit and any(
            flush_values[i + 4] - flush_values[i] == 4
            for i in range(len(flush_values) - 4)
        )

        # Hand strength scoring from strongest (9) to weakest (0)
        if straight_flush and max(flush_values[-5:]) == 12: return 9  # Royal flush
        if straight_flush: return 8
        if value_counts[0] == 4: return 7  # Four of a kind
        if value_counts[0] == 3 and value_counts[1] == 2: return 6  # Full house
        if flush_suit: return 5 # Flush (5 cards of the same suit)
        if straight: return 4
        if value_counts[0] == 3: return 3 # Three of a Kind
        if value_counts[0] == 2 and value_counts[1] == 2: return 2  # Two pair
        if value_counts[0] == 2: return 1  # One pair
        return 0  # High card

    def receive_game_start_message(self, game_info): pass
    def receive_round_start_message(self, round_count, hole_cards, seats): pass
    def receive_street_start_message(self, street, round_state): pass
    def receive_game_update_message(self, action, round_state): pass
    def receive_round_result_message(self, winners, hand_info, round_state): pass

def setup_ai():
    return CustomPlayer()