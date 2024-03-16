import os
import time
from io import BytesIO
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from players import Player
from tkinter import Button, Label, messagebox
from blackjack import Deck
from blackjack import Blackjack
from card_count import Card_Counter
from strategy import BasicStrategy
from bj_io import InputOutput
from BlackjackInterface import BlackjackInterface
from SimulatorInterface import SimulatorInterface
from BlackjackSimulatorConfig import BlackjackSimulatorConfig


class BlackjackSimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Blackjack Simulator with Card Counting")
        self.geometry("1000x750")

        self.dealer_hand_imgs = []
        self.player_hand_imgs = []
        
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
        self.clearRoundButton = None
        
        self.bust_bj_messageLabel = tk.Label(self, text='')
        self.message_label = tk.Label(self, text="")
        
        self.counting_enabled = False  # Flag to enable/disable card counting
        
        self.simulator_interface = SimulatorInterface()

        self.blackjack_game = Blackjack(players=[Player('MATH 111A class',1)])
        self.card_counter = self.blackjack_game.card_counter
        self.blackjack_interface = BlackjackInterface(blackjack_game=self.blackjack_game,
                                                     card_counter=self.card_counter,
                                                     deck=self.blackjack_game.deck_obj)
        self.blackjack_game.blackjack_interface = self.blackjack_interface
        self.blackjack_game.simulator_interface = self.simulator_interface
                
        self.input_output = InputOutput(self, self.card_counter, self.blackjack_game.simulator_interface)
        self.config = BlackjackSimulatorConfig(self.blackjack_game.players[0])
         # Initialization part of BlackjackSimulator
        self.basic_strategy = BasicStrategy()
        
        self.init_gui()
        
        
    def init_gui(self):
        self.actionButton = Button(self, text="Start Blackjack Round", command=self.start)

        self.dealerLabel = Label(self, text="")
        self.playerLabel = Label(self, text="")
        self.runningCountLabel = Label(self, text=f"Running Count: {self.running_count}")
        self.scoreLabel = Label(self)
        self.countLabel = Label(self)
        self.bustProbLabel = Label(self) 
        self.ruleset_label = Label(self)
        self.suggestion_bet_label = Label(self)
        self.suggestion_label = Label(self)
        self.valueLabel = Label(self)

        self.actionButton.pack()
        self.dealerLabel.pack()
        self.playerLabel.pack(anchor='e')
        self.runningCountLabel.pack()
        self.countLabel.pack()
        self.scoreLabel.pack()
        self.bustProbLabel.pack(anchor='sw')
        self.ruleset_label.pack(side=tk.BOTTOM,anchor="se",padx=20,pady=20)
        self.suggestion_bet_label.pack(anchor = 'sw')
        self.suggestion_label.pack(anchor='sw')
        self.valueLabel.pack(anchor='sw')
        
        self.hitButton = Button(self, text="HIT", command=lambda: self.trigger_player_action("HIT"))
        self.hitButton.pack(side=tk.LEFT, anchor='sw')

        self.standButton = Button(self, text="STAND", command=lambda: self.trigger_player_action("STAND"))
        self.standButton.pack(side=tk.LEFT,anchor='sw')

        self.doubleDownButton = Button(self, text="DOUBLE DOWN", command=lambda: self.trigger_player_action("DOUBLE_DOWN"))
        self.doubleDownButton.pack(side=tk.LEFT,anchor='sw')

        self.splitButton = Button(self, text="SPLIT", command=lambda: self.trigger_player_action("SPLIT"))
        self.splitButton.pack(side=tk.LEFT,anchor='sw')

        self.surrenderButton = Button(self, text="SURRENDER", command=lambda: self.trigger_player_action("SURRENDER"))
        self.surrenderButton.pack(side=tk.LEFT,anchor='sw')

        self.insuranceButton = Button(self, text="INSURANCE", command=lambda: self.trigger_player_action("INSURANCE"))
        self.insuranceButton.pack(side=tk.LEFT,anchor='sw')

        #self.toggleCountingButton = Button(self, text="Enable Card Counting", command=self.toggle_counting)
        #self.toggleCountingButton.pack(anchor='ne',padx=26)

        self.card_image_label_player1 = tk.Label(self, text="")
        self.card_image_label_player1.pack(anchor='e')
        
        self.action_message_label = tk.Label(self, text="")
        self.action_message_label.pack() 

        self.message_label.pack(side=tk.RIGHT,pady=26, ipadx=21, expand = 3)         
        self.bust_bj_messageLabel.pack(side=tk.RIGHT,pady=20, ipadx=21, expand = 3)         

        self.bet_input = tk.Entry(self)
        self.bet_input.pack(side=tk.RIGHT,anchor ='se', padx=37)
        print(f'Bankroll: {self.blackjack_game.players[0].bankroll}')
        self.betLabel = tk.Label(self, text=f"Current Bankroll: {self.blackjack_game.players[0].bankroll}\n\nBet Amount: ")
        self.betLabel.pack(side=tk.RIGHT,anchor ='se', padx=37)
        
        self.clearRoundButton = Button(self, text="Clear Round", command=self.clear_round)
        self.clearRoundButton.pack(side=tk.RIGHT,padx=26)

    def enable_buttons(self):
        self.hitButton.config(state=tk.NORMAL)
        self.standButton.config(state=tk.NORMAL)
        self.doubleDownButton.config(state=tk.NORMAL)
        self.splitButton.config(state=tk.NORMAL)
        self.surrenderButton.config(state=tk.NORMAL)
        self.insuranceButton.config(state=tk.NORMAL)

        if self.blackjack_game.is_game_over():
            self.actionButton.config(state=tk.DISABLED)
        else:
            self.actionButton.config(state=tk.NORMAL)

    def display_ruleset(self, ruleset_str):
        self.ruleset_label.config(text=ruleset_str)
        
        
    def start(self):
        self.blackjack_game.deck_obj.shuffle()
        self.actionButton.config(state=tk.DISABLED)
        self.blackjack_game = self.blackjack_game.initialize_game()
        self.update_gui(hit=False)
        
        config = BlackjackSimulatorConfig(self.blackjack_game.players[0])
        args, blackjack, ruleset_str = config.parse()
        self.display_ruleset(ruleset_str)

        bet_amount = self.bet_input.get()
        try:
            bet_amount = int(bet_amount)  # Convert to integer
        except ValueError:
            #messagebox.showerror("Invalid Input", "Please enter a valid bet amount.")
            return
        # Now you can use bet_amount as the bet for the game
        # For example:
        self.blackjack_game.players[0].place_bet(bet_amount)
        
        self.betLabel.config(self, text=f"Current Bankroll: {self.blackjack_game.players[0].bankroll}\n\nBet Amount: ")
        
        self.config.create_blackjack(args)
        
    def play_blackjack_round(self):
        self.blackjack_game.play_round()
        # Update the GUI after each round
        self.update_gui()

    def update_gui(self,hit=False,dealer=False):
        dealer_hand = self.blackjack_game.dealer.current_hand
        player_hand = self.blackjack_game.players[0].current_hand
        # Update dealer's hand
        if dealer & hit:
            self.dealer_card_imgs = [self.blackjack_game.deck_obj.pils[card] for card in dealer_hand]
            self.display_dealer_cards(self.dealer_card_imgs,dealer_hand,hit=True)
        # Update player's hands
        elif hit:
            for i, player in enumerate(self.blackjack_game.players):
                player_card_imgs = [self.blackjack_game.deck_obj.pils[card] for card in player_hand[-1]]
                self.display_player_cards(player_card_imgs, player_hand,hit=True)
        else:
            dealer_card_imgs = [self.blackjack_game.deck_obj.pils[card] for card in dealer_hand]
            self.display_dealer_cards(dealer_card_imgs,dealer_hand)
            
            for i, player in enumerate(self.blackjack_game.players):
                player_card_imgs = [self.blackjack_game.deck_obj.pils[card] for card in player_hand]
                self.display_player_cards(player_card_imgs, player_hand)

          # Update counts and other relevant information
        self.runningCountLabel.config(text=f"Running Count: {self.blackjack_interface.card_counter.running_count}")
               
        self.display_count()
        if not dealer:
            self.display_probabilities(self.blackjack_game.players[0])

        # Enable/disable buttons based on the game state
        self.enable_buttons()


    def display_dealer_cards(self, card_imgs, dealer_card, hit=False):
        if not self.dealer_hand_imgs or len(dealer_card) == 2:
            self.dealer_hand_img = Image.new('RGB', (200, 150), (255, 255, 255))
            x_offset = 0
            new_dealer_hand_img = self.dealer_hand_img  
        else:
            total_width = self.dealer_hand_img.width + (100)
            new_dealer_hand_img = Image.new('RGB', (total_width, 150), (255, 255, 255))
            new_dealer_hand_img.paste(self.dealer_hand_img, (0, 0))
            x_offset = self.dealer_hand_img.width
            
        self.dealer_hand_img = new_dealer_hand_img

        if not hit:
            for card_img in card_imgs:
                self.dealer_hand_img.paste(card_img, (x_offset, 0, x_offset+100, 150))
                x_offset += 100  
        else:
            self.dealer_hand_img.paste(card_imgs[-1], (x_offset, 0, x_offset+100, 150))

                
        dealer_hand_tk = ImageTk.PhotoImage(self.dealer_hand_img)

        self.dealerLabel.config(image=dealer_hand_tk)
        self.dealerLabel.image = dealer_hand_tk  # Keep a reference
        
        self.update()
        self.after(1000)


    def display_player_cards(self, card_imgs, player_hand, hit=False):
        if not self.player_hand_imgs or len(player_hand) == 2:
            self.player_hand_img = Image.new('RGB', (200, 150), (255, 255, 255))
            x_offset = 0
            new_player_hand_img = self.player_hand_img  
        else:
            total_width = self.player_hand_img.width + (100)
            new_player_hand_img = Image.new('RGB', (total_width, 150), (255, 255, 255))
            new_player_hand_img.paste(self.player_hand_img, (0, 0))
            # Start pasting from the end of the current hand image
            x_offset = self.player_hand_img.width
        
        self.player_hand_img = new_player_hand_img

        # Paste each new card image onto the base image
        if not hit:
            for card_img in card_imgs:
                self.player_hand_img.paste(card_img, (x_offset, 0, x_offset+100, 150))
                x_offset += 100  # Update the offset for the next card
        else:
            self.player_hand_img.paste(card_imgs[-1], (x_offset, 0, x_offset+100, 150))
            

        # Convert the image for use in Tkinter
        player_hand_tk = ImageTk.PhotoImage(self.player_hand_img)

        # Update the label for player cards
        self.playerLabel.config(image=player_hand_tk)
        self.playerLabel.image = player_hand_tk  # Keep a reference

        self.update()
        self.after(1000)

    def trigger_player_action(self, action):
        self.clicked_button = action
        self.disable_buttons()
        self.blackjack_interface.player_action(action)

        # HIT
        if action == "HIT":
            new_card_index = self.blackjack_game.player_play(self.blackjack_game.players[0], 0)
            end = False
            if not end:
                self.hitButton.config(state=tk.NORMAL)
                self.standButton.config(state=tk.NORMAL)
                if not (self.blackjack_game.players[0].blackjack or
                        self.blackjack_game.players[0].busted):
                    self.update_suggested_move()
                    end = self.update_gui_after_hit(new_card_index)
                else:
                    self.end_round()
                    end=True
        # STAND
        elif action == "STAND": #1
            self.disable_buttons()
            dealer_action, new_card_index = self.blackjack_game.dealer_play()
            if dealer_action == "HIT":
                end = self.update_gui_after_hit(new_card_index,dealer=True)
                while not (dealer_action == 'STAND' or self.blackjack_game.dealer.blackjack or self.blackjack_game.dealer.busted):
                    dealer_action, new_card_index = self.blackjack_game.dealer_play()
                    end = self.update_gui_after_hit(new_card_index,dealer=True)             
            self.end_round()
                    
        elif action == "DOUBLE_DOWN": #2
            self.input_output.double_down(self.blackjack_interface.last_card_drawn, self.blackjack_interface.deck, self.blackjack_interface.current_player)
        elif action == "SPLIT": #3
            #self.handle_split()
            self.input_output.split(self.blackjack_interface.current_player)
        elif action == "SURRENDER":
            #self.handle_surrender()
            self.input_output.surrender(self.blackjack_interface.current_player)
        elif action == "INSURANCE":
            #self.handle_insurance()
            self.input_output.insurance(self.blackjack_interface.current_player)
            
          
    def get_current_hands(self):
        dealer_hand = self.blackjack_interface.blackjack_game.dealer.current_hand
        player_cards = [player.current_hand for player in self.blackjack_interface.blackjack_game.players]
        return dealer_hand, player_cards
    
    def display_count(self):
        running_count = self.blackjack_interface.card_counter.running_count
        true_count = self.blackjack_interface.card_counter.true_count   
        cards_shown = self.blackjack_interface.card_counter.cards_shown

        # Update the GUI components
        self.runningCountLabel.config(text=f"Running Count: {running_count}")
         
        self.scoreLabel.config(text=f"Number of Cards Shown: {self.blackjack_interface.card_counter.cards_shown}")
            #self.countLabel.config(text=f"Count: {self.card_counter.count}")
            #self.scoreLabel.config(text=f"Score: {self.card_counter.score}")
            #self.valueLabel.config(text=f"True Count: {true_count}")
            
    def display_probabilities(self, player):
        self.valueLabel.config(text=f"True Count: {self.blackjack_interface.card_counter.true_count}")
        self.bustProbLabel.config(text=f"Bust Probability: {self.blackjack_game.calculate_bust_probability(player)}")
        player = self.blackjack_game.players[0]
        if not player.busted or player.blackjack:
            self.update_suggested_move()
        elif player.blackjack:
            self.display_message('Blackjack!')
            self.disable_buttons()
            self.end_round()
        elif player.busted:
            self.display_message('Busted! :(')
            self.disable_buttons()
            self.end_round()
        
    def update_suggested_move(self):
        dealer = self.blackjack_game.dealer
        player = self.blackjack_game.players[0] 
        
        numeric_hand_values = [value for value in player.hand_values if isinstance(value, int)]

        if min(numeric_hand_values, default=0) > 21:
            self.display_message("You busted!")
            self.end_round()
        else:
            suggested_move = self.basic_strategy.get_move(player, dealer)
            move_dict = {'H': 'Hit', 'S': 'Stand', 'D': 'Double Down', 'P': 'Split'}
            self.suggestion_label.config(text=f"Suggested Move: {move_dict.get(suggested_move, 'Unknown')}")
            self.update()  
    
    def update_player_hand_and_count(self, new_card_index, dealer=False):
        new_card_img = self.blackjack_game.deck_obj.get_pils_image(new_card_index)
        if dealer:
            self.dealer_hand_imgs.append(new_card_img)
            self.display_dealer_cards(self.dealer_hand_imgs, self.blackjack_game.dealer.current_hand, hit=True)
            print('dealer')

        else:
            self.player_hand_imgs.append(new_card_img)
            self.display_player_cards(self.player_hand_imgs, self.blackjack_game.players[0].current_hand, hit=True)
            print('player')
        self.update_count(new_card_index)
    
    def update_count(self, card_ind):
        self.countLabel.config(text=f"Count: {self.blackjack_interface.card_counter.count}", anchor='ne')
        self.runningCountLabel.config(text=f"Running Count: {self.blackjack_interface.card_counter.running_count}")
        self.display_probabilities(self.blackjack_game.players[0])
        self.scoreLabel.config(text=f"Number of cards shown: {self.blackjack_interface.card_counter.cards_shown}")
        self.update_idletasks()
    
    def toggle_counting(self):
        if self.counting_enabled:
            self.counting_enabled = False
            self.toggleCountingButton.config(text="Enable Card Counting")

        else:
            self.counting_enabled = True
            self.toggleCountingButton.config(text="Disable Card Counting")
            
            self.countLabel.config(text=f'Count: {self.blackjack_interface.card_counter.count}')
            self.runningCountLabel.config(text=f"Running Count: {self.blackjack_interface.card_counter.running_count}")
            self.scoreLabel.config(text=f"Number of Cards Shown: {self.blackjack_interface.card_counter.cards_shown}", anchor='ne')
            
            
    def hit(self, new_card_ind, deck_obj, player):    
        self.hitButton.config(state=tk.DISABLED)  # Disable hit button
        card_img = self.blackjack_game.cards[new_card_ind]
        self.blackjack_game.update_hand_values(player)
        self.update_gui()
        self.blackjack_interface.update_count(new_card)
        self.display_count()
        
        if player.busted:
            self.display_message(f"You busted!")
    
    def update_gui_after_hit(self, new_card_index, dealer=False):
        if dealer:
            if new_card_index == None:
                self.display_message(f"Dealer stands.")
                time.sleep(2)
                return True
                #self.end_round()
            else:
                self.update_player_hand_and_count(new_card_index,dealer=True)
            
            if self.blackjack_game.dealer.busted:
                self.display_message(f"{player.name} busted!", bust_bj=True)
                time.sleep(2)
                self.end_round()
                return True
            elif self.blackjack_game.dealer.blackjack:
                self.display_message(f"{player.name} got Blackjack!", bust_bj=True)
                time.sleep(2)
                self.end_round()
                return True
            else:
                return False
        else:
            self.update_player_hand_and_count(new_card_index)
            player= self.blackjack_game.players[0]
            if player.busted:
                self.display_msg(f"{player.name} busted!", bust_bj=True)
                time.sleep(2)
                self.end_round()  # Ends the round if the player is busted.
                return True
            elif player.blackjack:
                self.display_message(f"Player got Blackjack!", bust_bj=True)
                time.sleep(2)
                self.end_round()
                return True
            else:
                # Re-enable buttons except HIT if not busted.
                self.hitButton.config(state=tk.NORMAL)
        return False

    def stand(self, player):
        self.standButton.config(state=tk.DISABLED)  # Disable stand button
        self.input_output.stand(player)

    def double_down(self, new_card, deck_obj, player):
        self.doubleDownButton.config(state=tk.DISABLED)  # Disable double down button
        self.input_output.double_down(new_card, deck_obj, player)

    def split(self, player):
        self.splitButton.config(state=tk.DISABLED)  # Disable split button
        self.input_output.split(player)

    def surrender(self, player):
        self.surrenderButton.config(state=tk.DISABLED)  # Disable surrender button
        self.input_output.surrender(player)

    def insurance(self, player):
        self.insuranceButton.config(state=tk.DISABLED)  # Disable insurance button
        self.input_output.insurance(player)
            
    def disable_buttons(self):
        self.hitButton.config(state=tk.DISABLED)
        self.standButton.config(state=tk.DISABLED)
        self.doubleDownButton.config(state=tk.DISABLED)
        self.splitButton.config(state=tk.DISABLED)
        self.surrenderButton.config(state=tk.DISABLED)
        self.insuranceButton.config(state=tk.DISABLED)

    def display_message(self, msg, bust_bj = False):
        if bust_bj:
            self.bust_bj_messageLabel(text=msg)
        else:
            self.message_label.config(text=msg) 

    def end_round(self):
        time.sleep(1)
        
        winner = self.blackjack_game.end_round()
        if winner == 'tie':
            self.display_message("Tie! Settling bets...")
        elif winner == 'Player':
            self.display_message(f"{winner} wins! $$$")
        else:
            self.display_message(f"{winner} wins... ):")
        
        self.clearRoundButton.config(state=tk.NORMAL)

    def clear_round(self):
        self.update_bet_display()
        
        suggested_bet = self.blackjack_interface.card_counter.get_suggested_bet()
        self.suggestion_label.config(text=f"Suggested Bet: {suggested_bet}")
        
        # Clear dealer and player labels
        self.dealerLabel.image = None
        self.dealerLabel.config(image=None)
        self.playerLabel.image = None
        self.playerLabel.config(image=None)

        # Clear message label
        #self.message_label.config(text="")

        # Reset player hand images list
        self.player_hand_imgs = []
        self.dealer_hand_imgs = []

        # Enable action button and other buttons
        self.actionButton.config(state=tk.NORMAL)
        self.disable_buttons()
        
        self.update()

    def update_bet_display(self):
        self.betLabel.config(text=f"Current Bankroll: {self.blackjack_game.players[0].bankroll}\n\nBet Amount: {self.blackjack_game.players[0].bet}")

    '''def play_blackjack_round(self):
        dealer_card, player_cards, bust_probability = self.blackjack_interface.run_simulation_round()

        self.dealer_card_imgs = [self.blackjack_game.deck_obj.get_card_image(card) for card in dealer_card]
        self.display_dealer_cards(self.dealer_card_imgs,dealer_card)

        for i, player_card in enumerate(player_cards):
            self.player_card_imgs = [self.blackjack_game.deck_obj.get_card_image(card) for card in player_card]
            self.display_player_cards(self.player_card_imgs, i,start=True)
                
        self.update_suggested_move()
        
        bust_probability = self.blackjack_interface.calculate_bust_probability()
        self.bustProbLabel.config(text=f"Bust Probability: {bust_probability}")

        if not self.blackjack_interface.blackjack_game.is_game_over():
            self.enable_buttons()
        else:
            self.actionButton.config(state=tk.NORMAL)
    
        self.input_output.start_hand(self.blackjack_interface.hand_number)'''
        
if __name__ == "__main__":
    BlackjackSimulator().mainloop()
