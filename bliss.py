import random
from pathlib import Path
from random import Random
from schnapsen.game import Bot, Move, PlayerPerspective, RegularMove, GamePhase, GameState, SchnapsenGamePlayEngine
from schnapsen.game import SchnapsenTrickScorer
from schnapsen.deck import Card, Suit, Rank
from schnapsen.bots import RdeepBot, MLPlayingBot, MLDataBot, RandBot, BullyBot
from schnapsen.bots.heuristic1 import HeuristicOne
from schnapsen.bots.heuristic2 import HeuristicTwo
from typing import Optional


class BLiSS(Bot):
    '''The BLiSS system provides an easy structure to play Schnapsen as a multi-agent system.

    BLiSS can handle monolithic, two-agent, and four-agent configurations, and a total
    of four playing agents. It divides Schnapsen between phase one and phase two,
    and further into leading and following style gameplay.

    The four agents are defined as:
        A (Alpha) - Rdeep
        B (Bravo) - ML
        C (Charlie) - Heuristic Bot 1
        D (Delta) - Heuristic Bot 2

    Args:
        agent_order (str): A string determining the system configuration based on length.
            - Length 1: Monolithic system.
            - Length 2: Two-agent system (1st char: Phase 1, 2nd char: Phase 2).
            - Length 4: Four-agent system (Phase 1 Leader, Phase 1 Follower,
              Phase 2 Leader, Phase 2 Follower).

    Note:
        If the parameter string does not fit the defined format, the system will
        default to Rdeep.
    '''
    def __init__(self, agent_order: str, name: Optional[str] = None) -> None:
        """Initializes the BLiSS bot and its sub-agent components.

        Instantiates the four distinct bot types (Alpha, Bravo, Charlie, Delta) and
        calculates the number of active agents based on the input string length.

        Args:
            agent_order (str): The configuration string (e.g., 'AB', 'ABCD').
            name (Optional[str]): An optional name for the bot instance.
        """
        super().__init__(name)
        self.alpha = RdeepBot(num_samples=12, depth=5, rand=random.Random(), name="rdeep")
        self.bravo = MLPlayingBot(Path('rdeep_model'))
        self.charlie = HeuristicOne()
        self.delta = HeuristicTwo()
        self.nr_agents: int = len(agent_order) # The system determines the number of agents automatically based on the parameter string's length.
        self.agent_order: str = agent_order

    def pick_agent(self, initial: str, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """Delegates the move decision to a specific sub-agent based on a character code.

        Args:
            initial (str): The character code ('A', 'B', 'C', 'D') identifying the agent.
            perspective (PlayerPerspective): The current state of the game from the player's view.
            leader_move (Move | None): The move played by the leader, or None if this bot is leading.

        Returns:
            Move: The move selected by the specific sub-agent (Alpha, Bravo, Charlie, or Delta).
                  Defaults to Alpha (Rdeep) if the initial is unrecognized.
        """
        if initial == 'A':
            return self.alpha.get_move(perspective, leader_move)
        elif initial == 'B':
            return self.bravo.get_move(perspective, leader_move)
        elif initial == 'C':
            return self.charlie.get_move(perspective, leader_move)
        elif initial == 'D':
            return self.delta.get_move(perspective, leader_move)
        else:
            return self.alpha.get_move(perspective, leader_move)


    def get_move(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """Determines the next move by selecting the correct sub-agent for the current game state.

        The method checks the number of agents configured (monolithic, 2, or 4) and
        the current game phase/role (leading vs following) to decide which character
        from `agent_order` determines the strategy.

        Args:
            perspective (PlayerPerspective): The current state of the game.
            leader_move (Move | None): The move played by the opponent if they led,
                                       otherwise None.

        Returns:
            Move: The optimal move as decided by the currently active sub-agent.
        """
        # Monolithic System
        if self.nr_agents == 1:
            return self.pick_agent(self.agent_order[0], perspective, leader_move)
        
        # Two-Agent System (Split by Game Phase)
        elif self.nr_agents == 2:
            if perspective.get_phase() == GamePhase.ONE:
                return self.pick_agent(self.agent_order[0], perspective, leader_move)
            elif perspective.get_phase() == GamePhase.TWO:
                return self.pick_agent(self.agent_order[1], perspective, leader_move)
            
        # Four-Agent System (Split by Phase and Role)
        elif self.nr_agents == 4:
            if perspective.get_phase() == GamePhase.ONE:
                if leader_move is None:
                    return self.pick_agent(self.agent_order[0], perspective, leader_move)
                else: 
                    return self.pick_agent(self.agent_order[1], perspective, leader_move)
            elif perspective.get_phase() == GamePhase.TWO:
                if leader_move is None:
                    return self.pick_agent(self.agent_order[2], perspective, leader_move)
                else: 
                    return self.pick_agent(self.agent_order[3], perspective, leader_move)
                
        # Fallback
        else:
            return self.alpha.get_move(perspective, leader_move)

