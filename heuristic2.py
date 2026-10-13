
from schnapsen.game import Bot, Move, PlayerPerspective
from schnapsen.game import SchnapsenTrickScorer
from schnapsen.deck import Card, Suit, Rank


class HeuristicTwo(Bot):
    """The suit order is [CLUBS, DIAMONDS, SPADES, HEARTS], from lower suit to higher suit."""


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
        """If the bot can play a HEARTS marriage"""
        
        if leader_move is not None:
            return False
        
        valid_moves = perspective.valid_moves()

        for move in valid_moves:
            if move.is_marriage() and move.suit == Suit.HEARTS:
                return True
            
        return False


    def condition2(self, perspective: PlayerPerspective, leader_move: Move | None) -> bool:
        """...otherwise, if the bot is certain that the opponent has the 🂽 (QUEEN_HEARTS) in their hand"""

        opponentcards = perspective.get_known_cards_of_opponent_hand()
    
        for card in opponentcards:
            if card.rank == Rank.QUEEN and card.suit == Suit.HEARTS:
                return True
            
        return False


    def condition3(self, perspective: PlayerPerspective, leader_move: Move | None) -> bool:
        """and if the bot has at least 1 cards and the sum of their points are higher than 16"""

        hand = perspective.get_hand()
        cards = hand.get_cards()

        if len(cards) < 1:
            return False
        
        points = 0
        for card in cards:
            points += SchnapsenTrickScorer.SCORES[card.rank]

        return points > 16        


    def action1(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """...then play the HEARTS marriage."""

        valid_moves = perspective.valid_moves()

        for move in valid_moves:
            if move.is_marriage() and move.suit == Suit.HEARTS:
                return move
            
    def action2(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """then play the valid regular move where the card has the highest suit according
        to the suit order above. If multiple cards have the highest suit,
        prioritize according to highest points."""
        
        valid_moves = perspective.valid_moves()

        regular_moves = []
        for m in valid_moves:
            if m.is_regular_move():
                regular_moves.append(m)

        if not regular_moves:
            return valid_moves[0]
        
        suitpriority = {
            Suit.CLUBS: 0,
            Suit.DIAMONDS: 1,
            Suit.SPADES: 2,
            Suit.HEARTS: 3
        }

        pointmap = SchnapsenTrickScorer.SCORES

        def sorting(move):
            card = move.card
            return(suitpriority[card.suit], pointmap[card.rank])
        
        bestmove = max(regular_moves, key=sorting)

        return bestmove

    def action3(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """...otherwise find the least frequent suit among the cards in valid regular moves.
        If multiple suits have the same least frequency, prioritize according
        to the suit order above. Among these cards, play the one with the
        highest points."""
        
        valid_moves = perspective.valid_moves()
        
        regular_moves = []
        for m in valid_moves:
            if m.is_regular_move():
                regular_moves.append(m)

        if not regular_moves:
            return valid_moves[0]
        
        suitcounts = {}

        for move in regular_moves:
            s = move.card.suit
            suitcounts[s] = suitcounts.get(s, 0) + 1

        suitpriority = {
            Suit.CLUBS: 0,
            Suit.DIAMONDS: 1,
            Suit.SPADES: 2,
            Suit.HEARTS: 3
        }

        pointmap = SchnapsenTrickScorer.SCORES

        def sorting(move):
            card = move.card
            freq = suitcounts[card.suit]
            return(-freq, suitpriority[card.suit], pointmap[card.rank])
        
        bestmove = max(regular_moves, key=sorting)

        return bestmove


    def action4(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """...otherwise take the cards in valid regular moves and order them by points (low to high); in this
             ordering, if two cards have the same points, sort these according to the suit order.
             Now, play the card in the middle of the sequence. If the number of cards is even, play
             the card right above the middle."""
        
        valid_moves = perspective.valid_moves()
        
        regular_moves = []
        for m in valid_moves:
            if m.is_regular_move():
                regular_moves.append(m)

        if not regular_moves:
            return valid_moves[0]
        
        suitpriority = {
            Suit.CLUBS: 0,
            Suit.DIAMONDS: 1,
            Suit.SPADES: 2,
            Suit.HEARTS: 3
        }

        pointmap = SchnapsenTrickScorer.SCORES

        def sorting(move):
            card = move.card
            return(pointmap[card.rank], suitpriority[card.suit])
        
        sortedmoves = sorted(regular_moves, key = sorting)

        midindex = len(sortedmoves) // 2

        return sortedmoves[midindex]