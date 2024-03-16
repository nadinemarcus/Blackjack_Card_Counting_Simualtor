from strategy import BasicStrategy  # Assuming BasicStrategy is in the same directory

class InputOutput():
    '''InputOutput class to control any input or output while playing
       Blackjack. Options to print to terminal or not for large simulations.
       Segregation of code into its own class allows a UI to be implemented
       here in the future'''
    def __init__(self, gui_instance, card_counter, simulator_interface):
        self.gui_instance = gui_instance
        self.card_counter = card_counter
        self.simulator_interface = simulator_interface
        self.basicstrategy = BasicStrategy()  # Assuming BasicStrategy is in the same directory

    def display_message(self, msg):
        self.gui_instance.display_msg(msg)

    def welcome(self):
        self.display_message('Welcome to Blackjack')

    
    def can_double_down(self, player):
        if player.bankroll < player.bet * 2:
            self.display_message('Bankroll not enough to double')
            return False
        elif len(player.current_hand) > 2:
            self.display_message('You cannot double down unless you are on the first '
                                 'turn')
            return False
        else:
            return True

    def can_surrender(self, player):
        if len(player.current_hand) <= 2:
            return True
        else:
            self.display_message('You cannot surrender unless you are on the first '
                                 'turn')
            return False

    def can_insure(self, player, dealer, deck_obj):
        if deck_obj.card_num_or_face(dealer.current_hand[0]) != 'Ace':
            self.display_message('You can only insure if dealer has face up Ace')
            return False
        elif player.bankroll < (player.bet + player.bet//2):
            self.display_message('You do not have enough bankroll to insure')
            return False
        elif player.insurance_bet != 0:
            self.display_message('You have already taken insurance on this hand')
            return False
        else:
            return True

    def hand_to_print(self, deck_obj, player_hand):
        str_to_print = deck_obj.read_card(player_hand[0])
        for hand in player_hand[1:]:
            str_to_print += ' and {}'.format(deck_obj.read_card(hand))
        return str_to_print

    def new_card_dealt(self, player_name, player_num):
        pass

    def player_current_hand(self, player, deck_obj):
        str_to_print = 'Player {} ({}): You have {} - {}'.format(
            player.num, player.name,
            self.hand_to_print(deck_obj, player.current_hand),
            player.hand_values)
        self.display_message(str_to_print)

    def player_current_hand_vs_dealer(self, player, dealer, deck_obj):
        str_to_print = 'Player {} ({}): You have {} - {} vs dealer {}'.format(
            player.num, player.name,
            self.hand_to_print(deck_obj, player.current_hand),
            player.hand_best_value, dealer.hand_best_value)
        self.display_message(str_to_print)

    def dealer_current_hand(self, dealer, deck_obj):
        self.display_message('Dealer has a ' +
                             deck_obj.read_card(dealer.current_hand[0]))

    def blackjack(self):
        self.display_message('Blackjack!')

    def bust(self):
        self.display_message('Bust!')

    def display_card_image(self, card_img, player):
        # Assuming you have a GUI component (e.g., a Label) dedicated to displaying the card image
        # This could be part of your GUI class and passed into bj_io during initialization
        # For example, self.card_image_label is a Label in your GUI where you want to display the card image
        if player.num == 1:  # Assuming player.num indicates which player it is
            self.gui_instance.card_image_label_player1.config(image=card_img)
            self.gui_instance.card_image_label_player1.image = card_img  # Keep a reference
        else:
            # For other players, you would update the respective labels similarly
            pass

        # Optionally, update any messages or other GUI elements to indicate whose turn it is, the card drawn, etc.
        self.gui_instance.action_message_label.config(text=f"Player {player.num} drew a card.")


    '''def hit(self, new_card, deck, player):
        # Assuming new_card is an index, first get the card name from the deck object
        card_img = deck.get_card_img(new_card)  
        # Display the card image in the GUI
        self.display_card_image(card_img, player)'''
        
    def double_down(self, new_card, deck_obj, player):
        self.display_message('Player {} ({}) double down. Player bet doubled from '
                             '${} to ${}'.format(player.num, player.name,
                                                 player.bet//2, player.bet))
        self.display_message('HIT: next card {} - {}'.format(deck_obj.get_card(new_card)))
            # Check if they got a blackjack or went bust and if so tell them
        if player.hand_values == 'Blackjack':
            self.blackjack()
        elif min(player.hand_values) > 21:  # player went bust
            self.bust()

    def split(self, player):
        self.display_message('Player {} ({}) split'.format(player.num, player.name))

    def surrender(self, player):
        self.display_message('Player {} ({}) surrender. Half bet (${}) forfeited'.
                             format(player.num, player.name, player.bet//2))

    def insurance(self, player):
        pass

    def dealer_flip_card(self, dealer, deck_obj):
        self.display_message('Dealer goes:')
        self.display_message('Dealer has {}'.format(
            deck_obj.read_card(dealer.current_hand[0])))
        self.display_message('Dealer flips over {} - {}'.format(
            deck_obj.read_card(dealer.current_hand[1]),
            dealer.hand_values))

    def payout(self, player, player_payout, original_bankroll, new_bankroll):
        self.display_message('Bet of ${} payout {}x. Bankroll ${}->${}'.format(
            player.bet, player_payout, original_bankroll, new_bankroll))

    def insurance_payout(self, player, insurance_payout):
        if insurance_payout > 0:  # Insurance bet taken and won
            self.display_message('Insurance bet of ${} won. Paid out ${}'.format(
                player.insurance_bet, insurance_payout))
        elif insurance_payout < 0:  # Insurance bet taken and loss
            self.display_message('Insurance bet of ${} lost'.format(
                player.insurance_bet))
        else:  # No insurance bet taken
            pass

    def start_hand(self, round):
        self.display_message('Hand {}'.format(round))

    def end_hand(self, round):
        self.display_message('Hand {} finished\n'.format(round))

    def get_user_bets(self, player, human_player=True):
        collecting_input = True
        while collecting_input:
            # Get user input
            if human_player:
                bet = input('Player {} ({}) place your bet (Bankroll ${}): '.
                            format(player.num, player.name, player.bankroll))
            else:
                bet = self.card_counter.get_suggested_bet()
                self.display_message(('Player {} ({}) has bankroll ${} and bet ${}): '
                                      .format(player.num, player.name,
                                              player.bankroll, bet)))
            try:
                bet = int(bet)
            except TypeError:
                self.display_message('Incorrect input, please input an integer')

            # Check they have enough
            if player.bankroll < bet:
                self.display_message('{} you do not have enough bankroll to bet ${}. '
                                     'Current bankroll ${}'.format(player.name, bet,
                                                                   player.bankroll))
            else:
                collecting_input = False

        self.display_message('')
        return bet
