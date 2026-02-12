"""
Adversarial Search - Simplest Form (Minimax Algorithm)

This module implements the Minimax algorithm, which is the simplest and most
fundamental form of adversarial search used in two-player zero-sum games.

In adversarial search:
- Two players (MAX and MIN) take turns
- MAX tries to maximize the score
- MIN tries to minimize the score
- The algorithm explores all possible game states to find the optimal move
"""

import math


def minimax(state, is_maximizing, evaluate, get_moves, make_move, is_terminal):
    """
    Minimax algorithm - the simplest form of adversarial search.
    
    Args:
        state: Current game state
        is_maximizing: True if current player is maximizing, False otherwise
        evaluate: Function to evaluate a terminal state, returns a score
        get_moves: Function to get all possible moves from a state
        make_move: Function to apply a move to a state and return new state
        is_terminal: Function to check if state is terminal (game over)
    
    Returns:
        The best score achievable from this state
    """
    if is_terminal(state):
        return evaluate(state)
    
    moves = get_moves(state)
    if not moves:
        return evaluate(state)
    
    if is_maximizing:
        best_score = -math.inf
        for move in moves:
            new_state = make_move(state, move, is_maximizing)
            score = minimax(new_state, False, evaluate, get_moves, make_move, is_terminal)
            best_score = max(best_score, score)
        return best_score
    else:
        best_score = math.inf
        for move in moves:
            new_state = make_move(state, move, is_maximizing)
            score = minimax(new_state, True, evaluate, get_moves, make_move, is_terminal)
            best_score = min(best_score, score)
        return best_score


def find_best_move(state, is_maximizing, evaluate, get_moves, make_move, is_terminal):
    """
    Find the best move for the current player using minimax.
    
    Args:
        state: Current game state
        is_maximizing: True if current player is maximizing
        evaluate: Function to evaluate a terminal state
        get_moves: Function to get all possible moves
        make_move: Function to apply a move to a state
        is_terminal: Function to check if state is terminal
    
    Returns:
        The best move for the current player
    """
    moves = get_moves(state)
    best_move = None
    
    if is_maximizing:
        best_score = -math.inf
        for move in moves:
            new_state = make_move(state, move, is_maximizing)
            score = minimax(new_state, False, evaluate, get_moves, make_move, is_terminal)
            if score > best_score:
                best_score = score
                best_move = move
    else:
        best_score = math.inf
        for move in moves:
            new_state = make_move(state, move, is_maximizing)
            score = minimax(new_state, True, evaluate, get_moves, make_move, is_terminal)
            if score < best_score:
                best_score = score
                best_move = move
    
    return best_move


# =============================================================================
# Tic-Tac-Toe Example - Demonstrating Minimax
# =============================================================================

class TicTacToe:
    """
    Simple Tic-Tac-Toe game to demonstrate adversarial search.
    
    X is the maximizing player (tries to win with +1)
    O is the minimizing player (tries to win with -1)
    """
    
    def __init__(self):
        # Board represented as a list of 9 cells (3x3 grid)
        # Empty = ' ', X = 'X', O = 'O'
        self.board = [' '] * 9
    
    def copy(self):
        """Create a copy of the game state."""
        new_game = TicTacToe()
        new_game.board = self.board.copy()
        return new_game
    
    def get_moves(self):
        """Get all available moves (empty cells)."""
        return [i for i, cell in enumerate(self.board) if cell == ' ']
    
    def make_move(self, position, is_maximizing):
        """Make a move and return a new game state."""
        new_game = self.copy()
        new_game.board[position] = 'X' if is_maximizing else 'O'
        return new_game
    
    def check_winner(self):
        """Check if there's a winner. Returns 'X', 'O', or None."""
        # Winning combinations: rows, columns, diagonals
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]               # Diagonals
        ]
        
        for line in lines:
            a, b, c = line
            if self.board[a] == self.board[b] == self.board[c] != ' ':
                return self.board[a]
        return None
    
    def is_terminal(self):
        """Check if the game is over."""
        return self.check_winner() is not None or ' ' not in self.board
    
    def evaluate(self):
        """
        Evaluate the terminal state.
        Returns: +1 if X wins, -1 if O wins, 0 for draw
        """
        winner = self.check_winner()
        if winner == 'X':
            return 1
        elif winner == 'O':
            return -1
        return 0
    
    def display(self):
        """Display the board."""
        print()
        for i in range(3):
            row = self.board[i*3:(i+1)*3]
            print(f" {row[0]} | {row[1]} | {row[2]} ")
            if i < 2:
                print("-----------")
        print()
    
    def find_best_move(self, is_x_turn):
        """Find the best move using minimax."""
        return find_best_move(
            state=self,
            is_maximizing=is_x_turn,
            evaluate=lambda s: s.evaluate(),
            get_moves=lambda s: s.get_moves(),
            make_move=lambda s, m, is_max: s.make_move(m, is_max),
            is_terminal=lambda s: s.is_terminal()
        )


def play_game():
    """Play a game of Tic-Tac-Toe with AI vs AI using minimax."""
    game = TicTacToe()
    is_x_turn = True
    
    print("Tic-Tac-Toe: AI vs AI using Minimax Algorithm")
    print("X (maximizing) vs O (minimizing)")
    print("=" * 40)
    
    game.display()
    
    while not game.is_terminal():
        player = 'X' if is_x_turn else 'O'
        move = game.find_best_move(is_x_turn)
        
        print(f"{player} plays at position {move}")
        game = game.make_move(move, is_x_turn)
        game.display()
        
        is_x_turn = not is_x_turn
    
    winner = game.check_winner()
    if winner:
        print(f"Winner: {winner}")
    else:
        print("It's a draw!")
    
    return game


if __name__ == "__main__":
    play_game()
