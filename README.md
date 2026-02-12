# Adversarial Search - Simplest Form

This repository contains an implementation of the **Minimax algorithm**, which is the simplest and most fundamental form of adversarial search.

## What is Adversarial Search?

Adversarial search is a search technique used in competitive environments where two or more agents have conflicting goals. The most common application is in two-player zero-sum games where one player's gain is the other's loss.

## Minimax Algorithm

The Minimax algorithm is the foundation of adversarial search:

- **MAX player**: Tries to maximize the score
- **MIN player**: Tries to minimize the score
- The algorithm explores all possible game states to find the optimal move
- Assumes both players play optimally

### How it Works

1. Generate the complete game tree from the current state
2. Apply the evaluation function to terminal states
3. Propagate values up the tree:
   - MAX nodes take the maximum value of children
   - MIN nodes take the minimum value of children
4. Choose the move that leads to the best outcome

## Example: Tic-Tac-Toe

The implementation includes a complete Tic-Tac-Toe game demonstrating the minimax algorithm:

```python
python adversarial_search.py
```

When two optimal players (using minimax) play against each other, Tic-Tac-Toe always ends in a draw - proving the algorithm works correctly.

## Usage

```python
from adversarial_search import minimax, find_best_move, TicTacToe

# Create a game
game = TicTacToe()

# Find the best move for X (maximizing player)
best_move = game.find_best_move(is_x_turn=True)
```

## Files

- `adversarial_search.py` - Contains the minimax algorithm and Tic-Tac-Toe example
