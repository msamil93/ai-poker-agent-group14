from pypokerengine.players import BasePokerPlayer
import random

class LoosePlayer(BasePokerPlayer):
    def declare_action(self, valid_actions, hole_cards, game_state):
        # If the two cards have the same suit, there's some potential — take action
        if hole_cards[0][0] == hole_cards[1][0]:
            return 'raise' if random.random() > 0.5 else 'call'

        # If both cards are the same rank (like TT, KK), it’s a paired hand — stay aggressive
        if hole_cards[0][1] == hole_cards[1][1]:
            return 'raise' if random.random() > 0.5 else 'call'

        # If either card is high (T, J, Q, K, A), more likely to get involved
        high_cards = ['T', 'J', 'Q', 'K', 'A']
        if hole_cards[0][1] in high_cards or hole_cards[1][1] in high_cards:
            return 'raise' if random.random() > 0.75 else 'call'

        # Weak hand → no action
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
    return LoosePlayer()