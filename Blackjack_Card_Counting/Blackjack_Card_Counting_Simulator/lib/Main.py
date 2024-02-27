import os
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import Button, Label, Entry
from tkinter import messagebox
import card_count
from blackjack import Blackjack
from card_count import Card_Counter

class Main(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Card Counting Trainer")
        self.geometry("600x300")

        self.load_cards()

        self.random = np.random.RandomState()
        self.actionButton = None
        self.cardPanel = None
        self.count = 0
        self.countLabel = None
        self.cpmField = None
        self.index = 0
        self.score = 0
        self.scoreLabel = None
        self.timer = None
        self.track = None
        self.valueLabel = None
        self.value = 0

        self.init_gui()
        self.running_count = 0  # Initialize running count
        self.blackjack_game = Blackjack(players=["Player 1"])
        self.card_counter = Card_Counter(self.blackjack_game,
                                         total_decks=6,
                                         strategy_name='hi_lo')

        

    def start(self):
        self.count = 0
        self.score = 0
        self.value = 0
        self.track = np.zeros(52, dtype=bool)
        self.actionButton.config(text="Next Card")
        self.show_next_card()

    def stop(self):
        pass

    def show_next_card(self):
        if self.count >= 52:
            self.actionButton.config(text="Start")
            messagebox.showinfo("Message", "All cards shown.")
            return
        self.index = self.random.randint(52) % 52
        while self.track[self.index]:
            self.index = self.random.randint(52) % 52

        self.value = self.get_card_value(self.index)
        self.update_count(self.value)  # Update running count based on card value

        self.valueLabel.config(text=f"Value: {self.value}")
        self.scoreLabel.config(text=f"Score: {self.score}")
        self.countLabel.config(text=f"Running Count: {self.running_count}")  # Update score label
        self.cardPanel.config(image=self.cards[self.index])

        self.track[self.index] = True

    def update_count(self, card_value):
        self.count += 1
        # Simple Hi-Lo card counting system
        if 2 <= card_value <= 6:
            self.running_count += 1
            self.score = 1
        elif 10 <= card_value <= 11:
            self.running_count -= 1
            self.score = -1
        else:
            self.score = 0
        # Neutral cards (7, 8, 9) are not counted

        self.card_counter.update_count(card_value)


    def load_cards(self):
        self.cards = []
        ranks = [str(rank) for rank in range(2, 11)] + ['jack', 'queen', 'king', 'ace']
        suits = ['clubs', 'diamonds', 'hearts', 'spades']

        for rank in ranks:
            for suit in suits:
                img_path = os.path.join("classic-cards", f"{rank}_of_{suit}.png")
                img = Image.open(img_path)
                img = img.resize((100, 150))  # Resize image
                img = ImageTk.PhotoImage(img)
                self.cards.append(img)

    def get_card_value(self, index):
        rank = index // 4 + 2
        suit = index // 13

        if rank >= 11:  # Face cards
            return 10
        elif rank == 1:  # Ace
            return 11
        else:
            return rank

    def init_gui(self):
        self.cpmField = Entry(self, width=5)
        self.cpmField.insert(0, "52")
        self.actionButton = Button(self, text="Start", command=self.start)
        self.countLabel = Label(self)
        self.valueLabel = Label(self)
        self.scoreLabel = Label(self)
        self.cardPanel = Label(self)

        self.cpmField.pack()
        self.actionButton.pack()
        self.valueLabel.pack()
        self.scoreLabel.pack()
        self.countLabel.pack()

        self.cardPanel.pack()

    def run_simulation(self, num_rounds):
        # Simulate the specified number of rounds
        for _ in range(num_rounds):
            # Play a round of Blackjack
            self.blackjack_game.play_round()

            # Update card counting metrics
            self.update_card_count()

            # Calculate bust probability and display or log the result
            bust_probability = self.calculate_bust_probability()
            print(f"Bust Probability: {bust_probability}")

