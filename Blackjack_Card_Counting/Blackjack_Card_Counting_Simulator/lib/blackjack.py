import os
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import Button, Label, Entry
from tkinter import messagebox

from BlackjackInterface import BlackjackInterface
from bj_io import InputOutput
from card_count import Card_Counter
from players import *
from formatting import colour
import random


class Deck:
    '''Deck class used to store and manipulate a data type emulating a
    playing card deck'''
    def __init__(self, num_of_decks=1):
        self.deck = [i % 52 for i in range(num_of_decks * 52)]
        self.discard_deck = []
        self.cards = []
        
        self.pils = []

    def shuffle(self):
        random.shuffle(self.deck)

    def card_num_or_face(self, num):
        num_or_face = {0: 'Ace', 1: '2', 2: '3', 3: '4', 4: '5', 5: '6',
                       6: '7', 7: '8', 8: '9', 9: '10', 10: 'Jack',
                       11: 'Queen', 12: 'King'}
        return num_or_face[num % 13]

    def card_suit(self, num):
        suits = {0: 'Hearts', 1: 'Diamonds', 2: 'Clubs', 3: 'Spades'}
        return suits[num // 13]

    def new_card_suit(self, num):
        suits = {0: '\u2665',  # Hearts
                 1: '\u2662',  # Diamonds
                 2: '\u2663',  # Clubs
                 3: '\u2664'}  # Spades
        return suits[num // 13]
    
    def get_pils_image(self, ind):
        return self.pils[ind]
    
    def get_card_image(self, ind):
        return self.cards[ind]

    def get_card_value(self, card_index):
        # Assuming card_index is the position of the card in a sorted deck from 0 to 51
        # where 0-12 are Aces to Kings of hearts, 13-25 are Aces to Kings of diamonds, etc.
        if card_index in [48,49,50,51]:
            rank = 0
        else:
            rank = card_index // 4 + 1
        # Now, map this rank to the game's value
        if rank == 0: # Ace
            return 11 # or 1, depending on how you want to treat it
        elif 1 <= rank <= 9: # Number cards
            return rank + 1 # Adding one because ranks start at 0
        else: # Face cards
            return 10 # Jack, Queen, King

    def load_cards(self):
        card_values = {
            0: 'Ace', 1: '2', 2: '3', 3: '4', 4: '5', 5: '6',
            6: '7', 7: '8', 8: '9', 9: '10', 10: 'Jack',
            11: 'Queen', 12: 'King'
        }

        self.cards = []
        ranks = [str(rank) for rank in range(2, 11)] + ['jack', 'queen', 'y_king', 'z_ace']
        suits = ['clubs', 'diamonds', 'hearts', 'spades']

        # Create a mapping of card names to images
        self.card_images = {}

        for rank in ranks:
            for suit in suits:
                img_path = os.path.join("classic-cards", f"{rank}_of_{suit}.png")
                img = Image.open(img_path)
                img = img.resize((100, 150))
                self.pils.append(img)
                self.cards.append(ImageTk.PhotoImage(img))
                
                # Map the card name to the image object
                self.card_images[f"{rank}_of_{suit}"] = img

        # Now the deck is populated with PhotoImage objects in the same order as card_values
        return self.cards


class Blackjack:
    def __init__(self, players, num_of_decks=6,
                 blackjack_payout=1.5, win_payout=1, push_payout=0,
                 loss_payout=-1, surrender_payout=-0.5,
                 dealer_stand_on_hard=17, dealer_stand_on_soft=17,
                 shuffle_deck=True,
                 late_surrender=True, early_surrender=False,
                 player_bankroll=1000, reshuffle_penetration=0.75,
                 human_player=True, print_to_terminal=True,
                 min_bet=25, bet_spread=8,
                 dealer_peeks_for_bj=False,
                 strategy_name='hi_lo'):

        self.blackjack_interface = None
        self.simulator_interface = None
        self.blackjack_game = None
        self.deck_obj = Deck(num_of_decks)
        self.deck_obj.cards = self.deck_obj.load_cards()
        
        self.remaining_cards = {value: num_of_decks*4 for value in range(2,11)}
        self.remaining_cards[1] = num_of_decks*4
        self.remaining_cards[10] *= 4
        
        self.num_of_decks = num_of_decks
        self.human_player = human_player
        self.min_bet = min_bet
        self.bet_spread = bet_spread
        self.dealer_peeks_for_bj = dealer_peeks_for_bj
        self.strategy_name = strategy_name
        self.round = 0
        self.hand_number = 0
        self.turn_complete = False
        
        # Create player objects for each player
        self.players = []
        for i, player_name in enumerate(players):
            self.players.append(Player(name=player_name, num=i + 1,
                                        bankroll=player_bankroll))

        # Card counting class to initiate
        self.card_counter = Card_Counter(self, total_decks=self.num_of_decks,
                                         strategy_name=strategy_name,
                                         min_bet=self.min_bet,
                                         bet_spread=self.bet_spread,
                                         num_players=len(self.players))

        # Initiate input/output means
        self.inputoutput = InputOutput(self, self.card_counter, self.simulator_interface)

        # Create dealer object
        self.dealer = Dealer()

        # Initiate payout parameters
        self.blackjack_payout = blackjack_payout
        self.win_payout = win_payout
        self.push_payout = push_payout
        self.loss_payout = loss_payout
        self.surrender_payout = surrender_payout

        # Other rules
        self.dealer_stand_on_hard = dealer_stand_on_hard
        self.dealer_stand_on_soft = dealer_stand_on_soft

        # Surrender rules - late is the norm. Early is +0.6% advantage
        self.late_surrender = late_surrender
        self.early_surrender = early_surrender

        # Shuffle parm
        self.reshuffle_penetration = reshuffle_penetration

        # Shuffle deck
        if shuffle_deck:
            self.shuffle()

    def initialize_game(self):
        if self.blackjack_game is not None:
            raise ValueError("Game is already initialized.")

        # Deal initial cards to players and dealer
        for _ in range(2):  # Deal two cards to each player and the dealer
            self.deal_card(self.dealer)
            self.deal_card(self.players[0])

        if self.dealer_peeks_for_bj and \
           self.dealer.hand_best_value == 'Blackjack':
            pass
        '''else:
            # 7. Players are prompted on move
            for i, player in enumerate(self.players):
                self.player_play(player, i)'''
                
        return self
    
    def shuffle(self, discard_top_card=True, re_add_discard_deck=False):
        if re_add_discard_deck:  # Add discard deck back
            for _ in range(len(self.deck_obj.discard_deck)):
                self.deck_obj.deck.append(self.deck_obj.discard_deck.pop())
            self.card_counter.deck_refreshed()  # inform card_counter class

        self.deck_obj.shuffle()  # Shuffle deck
        if discard_top_card:  # Discard top card
            self.deck_obj.discard_deck.append(self.deck_obj.deck.pop())

    
    '''def take_bets(self):
        # Method to handle the betting phase of the game
        for player in self.players:
            player.bet = player.place_bet()'''

    def deal_card(self, player, update_values=True):
        new_card_index = self.deck_obj.deck.pop()  
        new_card_value = self.deck_obj.get_card_value(new_card_index)
        player.current_hand.append(new_card_index)  
        player.hand_values.append(new_card_value)
        
        if new_card_value in self.remaining_cards:
            self.remaining_cards[new_card_value] -= 1
            
        if update_values:
            self.update_hand_values(player)

        self.blackjack_interface.card_counter.next_card(new_card_index)

        return new_card_index
    

    def update_hand_values(self, player):
        player.hand_values = self.get_player_value(player.current_hand)
        print(f"{player.name}: {player.current_hand}, {player.hand_values}")
        player.hand_best_value = self.best_player_value(player)

    def is_blackjack(self, card1, card2):
        if (card1 < 0) or (card2 < 0):  # If ace in value calc
            return False
        card1_value = self.deck_obj.get_card_value(card1)
        card2_value = self.deck_obj.get_card_value(card2)

        # Ace = 0, 10-King = 9-12
        condition = \
            ((card1_value == 0 and 9 <= card2_value <= 13) or
             (card2_value == 0 and 9 <= card1_value <= 13))
        return condition

    def get_player_value(self, player_hand):
        total = 0
        aces = 0
        for card in player_hand:
            card_value = self.deck_obj.get_card_value(card)
            if card_value == 11:  # Ace
                aces += 1
                total += card_value
            else:
                total += card_value
        # Consider Ace as 1 if using it as 11 would cause the total > 21
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return [total]

    def best_player_value(self, player):
        # If Blackjack
        if 'Blackjack' in player.hand_values:
            return 'Blackjack'

        # If only 1 then return value
        if len(player.hand_values) == 1:
            return player.hand_values[0]
        else:  # Max value less than 21
            best_value = player.hand_values[0]
            for value in player.hand_values[1:]:
                if value > best_value and value <= 21:
                    best_value = value
            return best_value

    def get_dealer_input(self, dealer_value):
        # Dealer play adjusted by ruleset inputs

        # Hard values
        if len(dealer_value) == 1:
            if dealer_value[0] >= self.dealer_stand_on_hard:
                return 1  # STAND
            else:
                return 0  # HIT

        # Soft values
        for value in dealer_value:
            if self.dealer_stand_on_soft <= value <= 21:
                return 1  # STAND
        return 0  # HIT

    def player_play(self, player, player_action, i=None,print_to_console=False):
        self.turn_complete == False
        if not self.turn_complete:
            if 'Blackjack' in player.hand_values:  # player has blackjack
                player.blackjack = True
                self.turn_complete = True
            elif min(player.hand_values) > 21:  # player went bust
                player.busted = True
                self.turn_complete = True
            else:
                # Check if player can split
                split = False

                if len(player.current_hand) == 2:
                    card1 = self.deck_obj.get_card_value(
                        player.current_hand[0])
                    card2 = (self.deck_obj.get_card_value(
                        player.current_hand[1]))
                    if card1 == card2 and card1 != 10:
                        split = True

                # Check if player can insure
                '''can_insure = False
                if self.dealer.current_hand[0] % 13 == 0:
                    if len(player.current_hand) == 2:
                        can_insure = True'''
                        
                if player_action == 0:  # HIT
                    print_to_console = False  # Don't print full hand next run
                    new_card = self.deal_card(player)  # Deal next card
                    return new_card
                    #self.inputoutput.hit(new_card, self.deck_obj, player)

                elif player_action == 1:  # STAND
                    self.turn_complete = True
                elif player_action == 2:  # DOUBLE DOWN
                    # Double player's bet
                    assert (player.bankroll >= player.bet * 2) and (len(
                        player.current_hand) <= 2)
                    player.bet = player.bet * 2

                    # Deal new card
                    new_card = self.deal_card(player)  # Deal next card
                    self.turn_complete = True  # User's turn complete

                    # Output double down to player
                    self.inputoutput.double_down(new_card, self.deck_obj,
                                                 player)

                elif player_action == 3:  # SPLIT
                    assert (len(player.current_hand) == 2) and (
                            player.bankroll >= player.bet)
                    new_player = Player_Split(player, player.num)

                    # Transfer second card from first player's hand to new
                    # player's hand
                    new_player.current_hand.append(player.current_hand.pop())
                    player.current_hand.append(
                        self.deal_card(player))  # Deal next card
                    new_player.current_hand.append(
                        self.deal_card(new_player))  # Deal next card

                    # Deduct bet from bankroll for new player
                    new_player.bet = player.bet
                    player.bankroll -= player.bet

                    # Output split to player
                    self.inputoutput.split(new_player, self.deck_obj)

                    # Play new player's hand
                    self.player_play(new_player, print_to_console=False)

                elif player_action == 4:  # INSURANCE
                    assert (player.bankroll >= player.bet / 2)
                    player.insurance_bet = player.bet / 2

                    self.inputoutput.insurance(player, self.dealer,
                                               self.deck_obj)

                elif player_action == 5:  # SURRENDER
                    assert self.late_surrender
                    player.surrender = True

                    self.inputoutput.surrender(player)

                    # End player's turn
                    self.turn_complete = True

    def dealer_play(self):
        # Dealer must hit if below 17
        if min(self.dealer.hand_values) < 17:
            new_card = self.deal_card(self.dealer, update_values=True)
            return 'HIT', new_card
        return 'STAND', None

    def compare_hands(self, player, dealer):
        # Takes in hands and returns and payout

        if player.hand_best_value == 'Blackjack':  # Player blackjack
            if dealer.hand_best_value == 'Blackjack':  # Dealer blackjack
                return self.push_payout, 'tie'
            else:
                return self.blackjack_payout

        if dealer.hand_best_value == 'Blackjack':  # Dealer only blackjack
            if player.hand_best_value == 'Surrender' and self.early_surrender:
                return self.surrender_payout, 'Dealer'
            else:
                return self.loss_payout, 'Dealer'

        if player.hand_best_value == 'Surrender':  # Late surrender
            return self.surrender_payout, 'Dealer'

        if player.hand_best_value > 21:  # Player went bust
            return self.loss_payout, 'Dealer'
        elif dealer.hand_best_value > 21:  # Dealer went bust
            return self.win_payout, 'Player'

        if dealer.hand_best_value == player.hand_best_value:  # Same value
            return self.push_payout, 'tie'
        elif player.hand_best_value > dealer.hand_best_value:  # Player >
            return self.win_payout, 'Player'
        elif player.hand_best_value < dealer.hand_best_value:  # Dealer >
            return self.loss_payout, 'Dealer'
        else:
            raise ValueError('Error: player and dealer best value not \
                compatible')
    
    def settle_bets(self):
        dealer_value = self.dealer.hand_best_value

        for player in self.players:
            player_payout, winner = self.compare_hands(player, self.dealer)
            original_bankroll = player.bankroll
            player.bankroll += player_payout * player.bet
            # Any insurance
            #insurance_payout = self.check_insurance_payout(player)
            #player.bankroll += insurance_payout
            # Reset player bet
            player.bet = 0
            player.insurance_bet = 0
            player_value = player.hand_best_value

            #if player.surrender:
             #   player.bankroll += player.bet * self.surrender_payout
                #self.inputoutput.settle_surrender(player, self.deck_obj)

            if player_value == 'Blackjack':
                if dealer_value == 'Blackjack':
                    player.bankroll += player.bet
                    #self.inputoutput.settle_push(player, self.deck_obj)
                else:
                    player.bankroll += player.bet * self.blackjack_payout
                    #self.inputoutput.settle_blackjack(player, self.deck_obj)

            elif player_value == 'Surrender':
                player.bankroll += player.bet * self.surrender_payout
                #self.inputoutput.surrender(player)

            elif player_value > 21:
                player.bankroll += player.bet * self.loss_payout
                #self.inputoutput.settle_bust(player, self.deck_obj)

            elif dealer_value == 'Blackjack':
                if player_value == 'Surrender' and self.early_surrender:
                    player.bankroll += player.bet * self.surrender_payout
                else:
                    player.bankroll += player.bet * self.loss_payout

            elif dealer_value > 21:
                player.bankroll += player.bet * self.win_payout
                #self.inputoutput.settle_win(player, self.deck_obj)

            elif player_value > dealer_value:
                player.bankroll += player.bet * self.win_payout
                #self.inputoutput.settle_win(player, self.deck_obj)

            elif player_value == dealer_value:
                player.bankroll += player.bet * self.push_payout
                #self.inputoutput.settle_push(player, self.deck_obj)

            else:
                player.bankroll += player.bet * self.loss_payout
                #self.inputoutput.settle_loss(player, self.deck_obj)
            self.players[0].bankroll = player.bankroll
            return winner

    def play_round(self):
        self.round += 1
        self.deck_obj.shuffle()

        self.take_bets()

        for _ in range(2):
            for player in self.players + [self.dealer]:
                self.deal_card(player)

        for player in self.players:
            if player.hand_best_value == 21:
                continue
            self.player_play(player)

        if not any(player.hand_best_value == 21 for player in self.players):
            self.dealer_play()

        self.settle_bets()
        
    def end_round(self):
        # 10. Put all cards into discard deck
        self.discard_all_hands()

        # 12. Check if deck needs to be reshuffled
        pen = self.num_of_decks*52 * (1 - self.reshuffle_penetration)
        if len(self.deck_obj.deck) <= pen:
            self.shuffle(re_add_discard_deck=True)

        return self.settle_bets()
        # 13. End round
        #self.inputoutput.end_hand(self.round)

    def discard_hand(self, player):
        while len(player.current_hand) > 0:
            self.deck_obj.discard_deck.append(player.current_hand.pop())
    
    def discard_all_hands(self):
        for player in self.players:
            self.discard_hand(player)
        self.discard_hand(self.dealer)
    
    def is_game_over(self):
        # Example condition: game over if all players have no bankroll
        return all(player.bankroll <= 0 for player in self.players)

    def simulate(self, num_rounds=1000):
        for _ in range(num_rounds):
            self.play_round()

    def calculate_bust_probability(self, player):
        remaining_cards_count = sum(self.remaining_cards.values())
        current_hand_value = min(player.hand_values)  # Use the minimum value to consider aces as 1
        cards_needed_for_bust = 21 - current_hand_value
        bust_cards_count = sum(count for value, count in self.remaining_cards.items() if value > cards_needed_for_bust)
        return bust_cards_count / remaining_cards_count
          
    def main(self):
        self.simulate()


if __name__ == "__main__":
    bj = Blackjack(["Player1"])
    bj.blackjack_game = bj
    bj.main()