from strategy import BasicStrategy

class BlackjackInterface:
    def __init__(self, blackjack_game=None,card_counter=None,deck=None):
        self.blackjack_game = blackjack_game
        self.deck = deck
        self.card_counter = card_counter
        self.basic_strategy = BasicStrategy()  # You may need to adjust this depending on your existing code
        self.hand_number = 0
        self.current_player = None
        
    def run_simulation_round(self):
        dealer_card, player_cards = self.get_current_hands()
        bust_probability = self.card_counter.calculate_bust_probability(self.card_counter.running_count)
        return dealer_card, player_cards, bust_probability
    
    def player_action(self, action):
        # Implement player action logic here
        pass
    
    def get_current_hands(self):
        dealer_hand = self.blackjack_game.dealer.current_hand
        player_cards = [player.current_hand for player in self.blackjack_game.players]
        return dealer_hand, player_cards
    
    def update_count(self, card_value):
        self.card_counter.update_count(card_value)
        
    def calculate_bust_probability(self):
        return self.card_counter.calculate_bust_probability(self.card_counter.running_count)
