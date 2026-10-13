'''
BLiSS vs. Rdeep Tournament Benchmark

This script executes 10 000 games per setup to evaluate the performance of BLiSS against a baseline bot - Rdeep. 
It iterates through different configurations, defined in an external file.
Results are printed in console real-time, as well as stored in external files.

Inputs:
    benchmark_setups.txt: A file containing a list of BLiSS configuration strings 
                          (e.g., "A", "AB", "ABCD"), one per line.

Outputs:
    benchmark_results.txt: Aggregate statistics (wins/scores) for each setup.
    benchmark_logs.txt:    Detailed log of every single game played, including 
                           unique IDs and point differentials.

'''

import os
import random
import pathlib
from typing import Optional
import click
from schnapsen.bots import MLDataBot, train_ML_model, MLPlayingBot, RandBot, BullyBot
from schnapsen.game import (Bot, GamePlayEngine, Move, PlayerPerspective,
                            SchnapsenGamePlayEngine, TrumpExchange)
from schnapsen.bots.rdeep import RdeepBot
from schnapsen.bots.bliss import BLiSS
from statistics import mean


# Initialize the game engine
engine = SchnapsenGamePlayEngine()

# Define the baseline opponent (Rdeep)
rdeep_bot = RdeepBot(num_samples=12, depth=5, rand=random.Random(), name="rdeep")

# Setup

# Read list of configurations to test from the input file
with open('benchmark_setups.txt', 'r') as f:
    setups = f.read().splitlines()

# Initialize the results file with a header
with open('benchmark_results.txt', 'w') as f:
    f.write("setup bliss_wins rdeep_wins bliss_score rdeep_score\n")

# Initialize detailed logs file with a header
with open('benchmark_logs.txt', 'w') as f:
    f.write("id setup bliss rdeep\n")

# Global counter for game ID
id = 1


# Tournament loop
for setup in setups:
    # Initiate BLiSS with the current configuration string (e.g. ABCD)
    bliss = BLiSS(setup, "bliss")

    # Initialize counters for the current configuration

    rdeep_wins = 0
    bliss_wins = 0
    rdeep_score = 0
    bliss_score = 0

    # Run 10 000 games
    for x in range(10000):
        # Playing one game. Returns: winner (Bot object), game_points (int)
        winner, game_points, x = engine.play_game(rdeep_bot, bliss, random.Random())

        # Check winner and update stats
        if str(winner) == "rdeep":
            rdeep_wins += 1
            rdeep_score += (game_points)

            # Log the win for Rdeep
            with open('benchmark_logs.txt', 'a') as f:
                f.write(f"{id} {setup} 0 {game_points}\n")
        else:
            bliss_wins += 1
            bliss_score += (game_points)

            # Log the win for BLiSS
            with open('benchmark_logs.txt', 'a') as f:
                f.write(f"{id} {setup} {game_points} 0\n")
        
        # Increment global game ID
        id += 1
            


    # Reporting

    # Print a summary to the console
    print(f"RDeep vs. BLiSS | {setup} | Wins: {rdeep_wins} / {bliss_wins} | Total score: {rdeep_score} / {bliss_score}")

    # Save the results to the results file
    with open('benchmark_results.txt', 'a') as f:
        f.write(f"{setup} {bliss_wins} {rdeep_wins} {bliss_score} {rdeep_score}\n")
