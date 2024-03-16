class Player():
    '''Player class to emulate blackjack player'''
    def __init__(self, name, num, bankroll=0):
        self.name = name
        self.num = num
        self.bankroll = bankroll
        self.bet = 0
        self.current_hand = []
        self.hand_values = []
        self.hand_best_value = 0
        self.insurance_bet = 0
        
        self.busted = False
        self.blackjack = False
        self.children = []

    def update_bankroll(self, cash_to_add):
        self.bankroll += cash_to_add

    def get_bankroll(self):
        return self.bankroll

    def update_children(self, child):
        self.children.append(child)

    def get_num_children(self):
        return len(self.children)

    def reset_children(self):
        self.children = []

    def place_bet(self, bet_amount):
        if bet_amount <= self.bankroll:
            self.bet = bet_amount
            self.bankroll -= bet_amount
        else:
            print(f"Not enough bankroll. Current bankroll: {self.bankroll}")

    def update_hand_values(self, game):
        self.hand_values = game.get_player_value(self.current_hand)
        if self.hand_values > 21:
            self.busted = True
        elif self.hand_values == 21:
            self.blackjack = True
        # Dealer's best hand value is the highest value not exceeding 21
        self.hand_best_value = max(value for value in self.hand_values if value < 21)        

class Player_Split(Player):
    '''Player Split class emulates player after splitting a hand. Inherits
    from player parent'''
    # Player parent variable to reference
    def __init__(self, player_parent, player1_or_2):
        self.player_parent = player_parent  # Store parent player
        self.player_parent.update_children(self)  # Update parent variable
        self.name = player_parent.name + ' Hand ' + \
            str(self.player_parent.get_num_children())

        self.num = player_parent.num
        self.bankroll = player_parent.bankroll
        self.bet = player_parent.bet
        # Split takes first card only
        self.current_hand = [player_parent.current_hand[player1_or_2-1]]
        self.hand_values = player_parent.hand_values
        self.hand_best_value = player_parent.hand_best_value
        self.insurance_bet = 0

        self.blackjack = False
        self.busted = False
        
    def update_bankroll(self, cash_to_add):
        self.player_parent.update_bankroll(cash_to_add)  # Update prnt broll

    def get_bankroll(self):
        return self.player_parent.get_bankroll()

    def update_children(self, child):
        self.player_parent.update_children(child)

    def get_num_children(self):
        return self.player_parent.get_num_children()


class Dealer(Player):
    '''Dealer class to emulate the dealers current hand. Inherits'''
    def __init__(self):
        super().__init__("Dealer", 0)
        self.current_hand = []
        self.hand_values = []
        self.hand_best_value = 0
        self.stand_threshold = 17  # Dealer stands on 17 or above
        self.busted = False
        self.blackjack = False
        
    # Override the player_hit method for the dealer
    def player_hit(self, game):
        # Dealer hits until their hand value is 17 or above
        while self.hand_best_value < self.stand_threshold:
            new_card = game.deal_card(self)
            game.inputoutput.hit(new_card, game.deck_obj, self)
            game.update_hand_values(self)  # Update dealer's hand values
            # Check if dealer busts
            if min(self.hand_values) > 21:
                game.inputoutput.bust()  # Display bust message
                break  # Exit loop if dealer busts

    # Override the update_hand_values method for the dealer
    def update_hand_values(self, game):
        self.hand_values = game.get_player_value(self.current_hand)
        if self.hand_values > 21:
            self.busted = True
        elif self.hand_values == 21:
            self.blackjack = True
        # Dealer's best hand value is the highest value not exceeding 21
        self.hand_best_value = max(value for value in self.hand_values if value <= 21)