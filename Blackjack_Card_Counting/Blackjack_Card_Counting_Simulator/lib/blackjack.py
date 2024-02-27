import random

from formatting import colour
from bj_io import InputOutput
from players import *
from card_count import Card_Counter
from strategy import BasicStrategy

class Deck():
    '''Deck class used to store and manipulate a data type emulating a
    playing card deck'''

    def __init__(self, num_of_decks=1):
        self.deck = [i % 52 for i in range(num_of_decks*52)]
        self.discard_deck = []

    def shuffle(self):
        random.shuffle(self.deck)

    # Other methods...

class Blackjack():
    '''Blackjack game simulator. Default ruleset is based off of a liberal
    Vegas shoe but customisable'''

    def __init__(self, players, num_of_decks=6,
                 blackjack_payout=1.5, win_payout=1, push_payout=0,
                 loss_payout=-1, surrender_payout=-0.5,
                 dealer_stand_on_hard=17, dealer_stand_on_soft=17,
                 shuffle_deck=True,
                 late_surrender=True, early_surrender=False,
                 player_bankroll=1000, reshuffle_penetration=0.75,
                 human_player=True, print_to_terminal=True,
                 min_bet=1, bet_spread=8,
                 dealer_peeks_for_bj=False,
                 strategy_name='hi_lo'):

        self.num_of_decks = num_of_decks

        # Card counting class initialization
        self.card_counter = Card_Counter(self, total_decks=num_of_decks,
                                         strategy_name=strategy_name,
                                         min_bet=min_bet,
                                         bet_spread=bet_spread,
                                         num_players=len(players))

        # Other initialization...

    def deal_card(self, player, update_values=True):
        # Deal new card
        new_card = self.deck_obj.deck.pop()
        player.current_hand.append(new_card)

        # Update hand values
        if update_values:
            self.update_hand_values(player)

        # Send new card to card_counter class
        self.card_counter.next_card(new_card)

        return new_card

    def discard_hand(self, player):
        while len(player.current_hand) > 0:
            discarded_card = player.current_hand.pop()
            self.deck_obj.discard_deck.append(discarded_card)

            # Update card count for discarded card
            self.card_counter.card_discarded(discarded_card)

    def play_hand(self):
        # Existing code...

        # 10. Put all cards into discard deck
        self.discard_all_hands()

        # Update card count for all discarded cards
        for player in self.players:
            self.card_counter.cards_discarded(player.current_hand)
            player.current_hand = []

        # Existing code...

    def play_round(self):
        self.take_bets()

        self.play_hand()

        # Update card count for remaining cards at the end of the round
        self.card_counter.round_end()
