from pypokerengine.players import BasePokerPlayer
import random

class TightPlayer(BasePokerPlayer):
    def declare_action(self, valid_actions, hole_cards, game_state):
        # If the hand is a premium pair (Aces, Kings, Queens), raise aggressively
        strong_pairs = ['A', 'K', 'Q']
        if hole_cards[0][1] == hole_cards[1][1] and hole_cards[0][1] in strong_pairs:
            return 'raise'

        # If both cards are suited and high (like AK suited, KQ suited), just call
        high_cards = ['T', 'J', 'Q', 'K', 'A']
        if hole_cards[0][0] == hole_cards[1][0] and \
           hole_cards[0][1] in high_cards and hole_cards[1][1] in high_cards:
            return 'call'

        # Everything else → fold without hesitation
        return 'fold'

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_cards, seats):
        pass

    def receive_street_start_message(self, street, game_state):
        pass

    def receive_game_update_message(self, action, game_state):
        pass

    def receive_round_result_message(self, winners, hand_info, game_state):
        pass

def setup_ai():
    return TightPlayer()