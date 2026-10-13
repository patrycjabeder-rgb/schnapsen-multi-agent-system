
from schnapsen.game import Bot, Move, PlayerPerspective
from schnapsen.deck import Card, Suit, Rank


class HeuristicOne(Bot):
    """The suit order is [SPADES, DIAMONDS, CLUBS, HEARTS], from lower suit to higher suit."""


    def get_move(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """
        The condition-action structure of the Bot.
        """
        if self.condition1(perspective, leader_move):
            return self.action1(perspective, leader_move)
        elif self.condition2(perspective, leader_move):
            if self.condition3(perspective, leader_move):
                return self.action2(perspective, leader_move)
            else:
                return self.action3(perspective, leader_move)
        else:
            return self.action4(perspective, leader_move)

    def condition1(self, perspective: PlayerPerspective, leader_move: Move | None) -> bool:
        """If the bot can play a trump exchange"""
        if leader_move is not None:
            return False
        trump_card = perspective.get_trump_card()
        trump_suit = perspective.get_trump_suit()
        my_cards = perspective.get_hand().get_cards()
        have_jack_trump = False

        if trump_card is None:
            return False
        for card in my_cards:
            if card.suit == trump_suit and card.rank == Rank.JACK:
                have_jack_trump = True
        if have_jack_trump:
            return True
        else:
            return False

    def condition2(self, perspective: PlayerPerspective, leader_move: Move | None) -> bool:
        """...Otherwise, if the bot is certain that the opponent has the 🃝 (QUEEN_CLUBS) in their hand"""
    
        queen_clubs = Card.QUEEN_CLUBS
        known_opponent_cards = perspective.get_known_cards_of_opponent_hand()
        if known_opponent_cards.__contains__(queen_clubs):
            return True
        else:
            return False

    def condition3(self, perspective: PlayerPerspective, leader_move: Move | None) -> bool:
        """If the bot has more HEARTS than DIAMONDS or equal the number in their hand"""
        
        my_hand = perspective.get_hand()
        hearts_in_hand = my_hand.filter_suit(Suit.HEARTS)
        diamonds_in_hand = my_hand.filter_suit(Suit.DIAMONDS)
        if len(hearts_in_hand) >= len(diamonds_in_hand):
            return True
        else:
            return False


    def action1(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """...then play a trump exchange."""
        valid_moves = perspective.valid_moves()
        for move in valid_moves:
            if move.is_trump_exchange():
                return move

    def assign_point_score(self, rank: Rank) -> int:
        """A function to assign point scores to ranks, which makes sorting cards easier"""
        if rank == Rank.NINE:
            return 0
        if rank == Rank.JACK:
            return 2
        if rank == Rank.QUEEN:
            return 3
        if rank == Rank.KING:
            return 4
        if rank == Rank.TEN:
            return 10
        if rank == Rank.ACE:
            return 11
        return 0

    def action2(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """...then play the valid regular move where the card has the lowest suit according
        to the suit order above. If multiple cards have the lowest suit,
        prioritize according to lowest points."""
        
        valid_moves = perspective.valid_moves()
        #filter only regular moves
        valid_regular_moves = []
        for moves in valid_moves:
            if moves.is_regular_move():
                valid_regular_moves.append(moves)
        #dividing moves into separate lists according to suit
        spades_moves = []
        diamonds_moves = []
        clubs_moves = []
        hearts_moves = []
        for move in valid_regular_moves:
            if move._cards()[0].suit == Suit.SPADES:
                spades_moves.append(move)
            elif move._cards()[0].suit == Suit.DIAMONDS:
                diamonds_moves.append(move)
            elif move._cards()[0].suit == Suit.CLUBS:
                clubs_moves.append(move)
            elif move._cards()[0].suit == Suit.HEARTS:
                hearts_moves.append(move)
        #picking the suit to play, according to the suit order, only if it has at least one move
        if len(spades_moves) > 0:
            if len(spades_moves) == 1:
                return spades_moves[0]
            else:
                #finding the lowest point move among spades moves
                lowest_point_move = spades_moves[0]
                for i in range(len(spades_moves)):
                    point_score = self.assign_point_score(spades_moves[i]._cards()[0].rank)
                    if point_score < self.assign_point_score(lowest_point_move._cards()[0].rank):
                        lowest_point_move = spades_moves[i]
                return lowest_point_move
        elif len(diamonds_moves) > 0:
            if len(diamonds_moves) == 1:
                return diamonds_moves[0]
            else:
                #finding the lowest point move among diamonds moves
                lowest_point_move = diamonds_moves[0]
                for i in range(len(diamonds_moves)):
                    point_score = self.assign_point_score(diamonds_moves[i]._cards()[0].rank)
                    if point_score < self.assign_point_score(lowest_point_move._cards()[0].rank):
                        lowest_point_move = diamonds_moves[i]
                return lowest_point_move
        elif len(clubs_moves) > 0:
            if len(clubs_moves) == 1:
                return clubs_moves[0]
            else:
                #finding the lowest point move among clubs moves
                lowest_point_move = clubs_moves[0]
                for i in range(len(clubs_moves)):
                    point_score = self.assign_point_score(clubs_moves[i]._cards()[0].rank)
                    if point_score < self.assign_point_score(lowest_point_move._cards()[0].rank):
                        lowest_point_move = clubs_moves[i]
                return lowest_point_move
        elif len(hearts_moves) > 0:
            if len(hearts_moves) == 1:
                return hearts_moves[0]
            else:
                #finding the lowest point move among hearts moves
                lowest_point_move = hearts_moves[0]
                for i in range(len(hearts_moves)):
                    point_score = self.assign_point_score(hearts_moves[i]._cards()[0].rank)
                    if point_score < self.assign_point_score(lowest_point_move._cards()[0].rank):
                        lowest_point_move = hearts_moves[i]
                return lowest_point_move
        

    def action3(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """...otherwise find the least frequent suit among the cards in valid regular moves.
        If multiple suits have the same least frequency, prioritize according
        to the suit order above. Among these cards, play the one with the
        lowest points."""
        
        valid_moves = perspective.valid_moves()
        #filter only regular moves
        valid_regular_moves = []
        for move in valid_moves:
            if move.is_regular_move():
                valid_regular_moves.append(move)
        #dividing moves into separate lists according to suit
        spades_moves = []
        diamonds_moves = []
        clubs_moves = []
        hearts_moves = []
        for move in valid_regular_moves:
            if move._cards()[0].suit == Suit.SPADES:
                spades_moves.append(move)
            elif move._cards()[0].suit == Suit.DIAMONDS:
                diamonds_moves.append(move)
            elif move._cards()[0].suit == Suit.CLUBS:
                clubs_moves.append(move)
            elif move._cards()[0].suit == Suit.HEARTS:
                hearts_moves.append(move)
        
        #finding the least frequent suit(s)
        suit_frequencies = [len(spades_moves), len(diamonds_moves), len(clubs_moves), len(hearts_moves)]
        suit_frequencies.sort()
        #removing zero frequencies
        while suit_frequencies[0] == 0:
            suit_frequencies.pop(0)
        
        
        lowest_frequencies = []
        #picking all suits that have the lowest frequency (frequencies equal to the first (smallest) element in sorted list)
        for freq in suit_frequencies:
            if freq == suit_frequencies[0]:
                lowest_frequencies.append(freq)
    
        #picking a target suit, among those with lowest frequency, according to suit order
        if len(hearts_moves) in lowest_frequencies:
            target_moves = hearts_moves
        elif len(clubs_moves) in lowest_frequencies:
            target_moves = clubs_moves
        elif len(diamonds_moves) in lowest_frequencies:
            target_moves = diamonds_moves
        else:
            target_moves = spades_moves
    
        #finding the lowest point move among target moves
        lowest_point_move = target_moves[0]
        for i in range(len(target_moves)):
            point_score = self.assign_point_score(target_moves[i]._cards()[0].rank)
            if point_score < self.assign_point_score(lowest_point_move._cards()[0].rank):
                lowest_point_move = target_moves[i]
        return lowest_point_move

    def action4(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        
        """...otherwise take the cards in valid regular moves and order them by points (low to high); in this
             ordering, if two cards have the same points, sort these according to the suit order.
             Now, play the card in the middle of the sequence. If the number of cards is even, play
             the card right above the middle."""
        valid_moves = perspective.valid_moves()
        #filter only regular moves
        valid_regular_moves = []
        for move in valid_moves:
            if move.is_regular_move():
                valid_regular_moves.append(move)
        #dividing moves into separate lists according to the rank
        nines_moves = []
        jacks_moves = []
        queens_moves = []
        kings_moves = []
        tens_moves = []
        aces_moves = []
        for move in valid_regular_moves:
            #sort according to rank order
            if move._cards()[0].rank == Rank.NINE:
                nines_moves.append(move)
            elif move._cards()[0].rank == Rank.JACK:
                jacks_moves.append(move)
            elif move._cards()[0].rank == Rank.QUEEN:
                queens_moves.append(move)
            elif move._cards()[0].rank == Rank.KING:
                kings_moves.append(move)
            elif move._cards()[0].rank == Rank.TEN:
                tens_moves.append(move)
            elif move._cards()[0].rank == Rank.ACE:
                aces_moves.append(move)
        #ordering moves by rank
        ordered_moves_by_rank = [nines_moves, jacks_moves, queens_moves, kings_moves, tens_moves, aces_moves]
        for i in range (len(ordered_moves_by_rank)):
            #if there are multiple moves with the same rank, sorting according to suit order
            if len(ordered_moves_by_rank[i]) > 1:
                spades = []
                diamonds = []
                clubs = []
                hearts = []
                for move in ordered_moves_by_rank[i]:
                    if move._cards()[0].suit == Suit.SPADES:
                        spades.append(move)
                    elif move._cards()[0].suit == Suit.DIAMONDS:
                        diamonds.append(move)
                    elif move._cards()[0].suit == Suit.CLUBS:
                        clubs.append(move)
                    elif move._cards()[0].suit == Suit.HEARTS:
                        hearts.append(move)
                sorted_list = spades + diamonds + clubs + hearts
                #replacing the unsorted list of a rank with the sorted one according to suit order
                ordered_moves_by_rank[i] = sorted_list
        #combining all ordered lists into one final ordered list
        final_ordered_moves = []
        for list in ordered_moves_by_rank:
            for move in list:
                final_ordered_moves.append(move)
        #finding the middle index
        middle_index = len(final_ordered_moves) // 2
    
        return final_ordered_moves[middle_index]
        


