import os
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import Button, Label
from blackjack import Blackjack
from card_count import Card_Counter

class BlackjackSimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Blackjack Simulator with Card Counting")
        self.geometry("800x800")

        self.load_cards()

        self.random = np.random.RandomState()
        self.running_count = 0
        self.actionButton = None
        self.dealerLabel = None
        self.playerLabel = None
        self.countLabel = None
        self.valueLabel = None
        self.scoreLabel = None
        self.bustProbLabel = None
        self.hitButton = None
        self.standButton = None
        self.doubleDownButton = None
        self.splitButton = None
        self.surrenderButton = None
        self.insuranceButton = None
        
        self.counting_enabled = False  # Flag to enable/disable card counting
        self.init_gui()
        self.blackjack_game = Blackjack(players=["Player 1"])
        self.card_counter = Card_Counter(self.blackjack_game, total_decks=6, strategy_name='hi_lo')

    def enable_buttons(self):
        self.hitButton.config(state=tk.NORMAL)
        self.standButton.config(state=tk.NORMAL)
        self.doubleDownButton.config(state=tk.NORMAL)
        self.splitButton.config(state=tk.NORMAL)
        self.surrenderButton.config(state=tk.NORMAL)
        self.insuranceButton.config(state=tk.NORMAL)

    def start(self):
        self.actionButton.config(state=tk.DISABLED)
        self.play_blackjack_round()

    def play_blackjack_round(self):
        self.blackjack_game.play_round()

        dealer_card, player_cards = self.get_current_hands()
        self.update_count(dealer_card)
        for card_value in player_cards:
            self.update_count(card_value)

        self.display_current_hands(dealer_card, player_cards)
        self.display_count()

        bust_probability = self.card_counter.calculate_bust_probability(self.running_count)
        self.bustProbLabel.config(text=f"Bust Probability: {bust_probability}")

        if not self.blackjack_game.is_game_over():
            self.enable_buttons()
        else:
            self.actionButton.config(state=tk.NORMAL)

    def trigger_player_action(self, action):
        self.clicked_button = action
        self.disable_buttons()
        self.blackjack_game.player_action(action)

    def get_current_hands(self):
        dealer_hand = self.blackjack_game.dealer.current_hand
        player_cards = [player.current_hand for player in self.blackjack_game.players]
        return dealer_hand, player_cards
    
    def display_current_hands(self, dealer_card, player_cards):
        self.dealerLabel.config(text=f"Dealer's Hand: {dealer_card}")
        self.playerLabel.config(text=f"Player's Hand: {player_cards}")

    def display_count(self):
        self.countLabel.config(text=f"Running Count: {self.running_count}")
        if self.counting_enabled:
            self.valueLabel.config(text=f"Count: {self.card_counter.score}")
            self.scoreLabel.config(text=f"Number of Cards Shown: {self.card_counter.count}")

    def update_count(self, card_value):
        self.card_counter.update_count(card_value)
        self.running_count = self.card_counter.running_count

    def load_cards(self):
        self.cards = []
        ranks = [str(rank) for rank in range(2, 11)] + ['jack', 'queen', 'king', 'ace']
        suits = ['clubs', 'diamonds', 'hearts', 'spades']
        for rank in ranks:
            for suit in suits:
                img_path = os.path.join("classic-cards", f"{rank}_of_{suit}.png")
                img = Image.open(img_path)
                img = img.resize((100, 150))
                img = ImageTk.PhotoImage(img)
                self.cards.append(img)

    def init_gui(self):
        self.actionButton = Button(self, text="Start Blackjack Round", command=self.start)
        self.dealerLabel = Label(self, text="Dealer's Hand:")
        self.playerLabel = Label(self, text="Player's Hand:")
        self.countLabel = Label(self, text=f"Running Count: {self.running_count}")
        self.valueLabel = Label(self)
        self.scoreLabel = Label(self)
        self.bustProbLabel = Label(self) 

        self.actionButton.pack()
        self.dealerLabel.pack()
        self.playerLabel.pack()
        self.countLabel.pack()
        self.valueLabel.pack()
        self.scoreLabel.pack()
        self.bustProbLabel.pack()

        self.hitButton = Button(self, text="HIT", command=lambda: self.trigger_player_action("HIT"))
        self.hitButton.pack(side=tk.LEFT)

        self.standButton = Button(self, text="STAND", command=lambda: self.trigger_player_action("STAND"))
        self.standButton.pack(side=tk.LEFT)

        self.doubleDownButton = Button(self, text="DOUBLE DOWN", command=lambda: self.trigger_player_action("DOUBLE_DOWN"))
        self.doubleDownButton.pack(side=tk.LEFT)

        self.splitButton = Button(self, text="SPLIT", command=lambda: self.trigger_player_action("SPLIT"))
        self.splitButton.pack(side=tk.LEFT)

        self.surrenderButton = Button(self, text="SURRENDER", command=lambda: self.trigger_player_action("SURRENDER"))
        self.surrenderButton.pack(side=tk.LEFT)

        self.insuranceButton = Button(self, text="INSURANCE", command=lambda: self.trigger_player_action("INSURANCE"))
        self.insuranceButton.pack(side=tk.LEFT)

        self.toggleCountingButton = Button(self, text="Enable Card Counting", command=self.toggle_counting)
        self.toggleCountingButton.pack()

    def toggle_counting(self):
        if self.counting_enabled:
            self.counting_enabled = False
            self.toggleCountingButton.config(text="Enable Card Counting")
            self.valueLabel.config(text="")
            self.scoreLabel.config(text="")
        else:
            self.counting_enabled = True
            self.toggleCountingButton.config(text="Disable Card Counting")
            self.valueLabel.config(text="Count: 0")
            self.scoreLabel.config(text="Number of Cards Shown: 0")

    def disable_buttons(self):
        self.hitButton.config(state=tk.DISABLED)
        self.standButton.config(state=tk.DISABLED)
        self.doubleDownButton.config(state=tk.DISABLED)
        self.splitButton.config(state=tk.DISABLED)
        self.surrenderButton.config(state=tk.DISABLED)
        self.insuranceButton.config(state=tk.DISABLED)

if __name__ == "__main__":
    BlackjackSimulator().mainloop()
