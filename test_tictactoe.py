"""
Tests for the tic-tac-toe game tree analysis module.
"""

import unittest
from tictactoe import (
    LINES, EMPTY, X, O,
    make_board, make_move, count_xn_on, evaluate, utility,
    is_terminal, get_moves, canonical_form, apply_transform,
    generate_successors_with_symmetry, build_game_tree,
    minimax, alphabeta, order_children_for_pruning, _mark_pruned,
    SYMMETRY_TRANSFORMS,
)


class TestBoard(unittest.TestCase):
    def test_make_board(self):
        board = make_board()
        self.assertEqual(len(board), 9)
        self.assertTrue(all(c == EMPTY for c in board))

    def test_make_move(self):
        board = make_board()
        new_board = make_move(board, 0, X)
        self.assertEqual(new_board[0], X)
        self.assertEqual(board[0], EMPTY)  # original unchanged

    def test_get_moves_empty(self):
        board = make_board()
        self.assertEqual(get_moves(board), list(range(9)))

    def test_get_moves_partial(self):
        board = make_move(make_board(), 4, X)
        moves = get_moves(board)
        self.assertEqual(len(moves), 8)
        self.assertNotIn(4, moves)


class TestLines(unittest.TestCase):
    def test_line_count(self):
        self.assertEqual(len(LINES), 8)

    def test_all_positions_covered(self):
        positions = set()
        for line in LINES:
            for pos in line:
                positions.add(pos)
        self.assertEqual(positions, set(range(9)))


class TestCountXnOn(unittest.TestCase):
    def test_empty_board(self):
        board = make_board()
        c = count_xn_on(board)
        self.assertEqual(c['X1'], 0)
        self.assertEqual(c['X2'], 0)
        self.assertEqual(c['X3'], 0)
        self.assertEqual(c['O1'], 0)
        self.assertEqual(c['O2'], 0)
        self.assertEqual(c['O3'], 0)

    def test_x_in_center(self):
        """X in center: position 4 is in 4 lines (row1, col1, diag, anti-diag)."""
        board = make_move(make_board(), 4, X)
        c = count_xn_on(board)
        self.assertEqual(c['X1'], 4)
        self.assertEqual(c['X2'], 0)
        self.assertEqual(c['O1'], 0)

    def test_x_in_corner(self):
        """X in corner 0: in row0, col0, main-diag = 3 lines."""
        board = make_move(make_board(), 0, X)
        c = count_xn_on(board)
        self.assertEqual(c['X1'], 3)
        self.assertEqual(c['X2'], 0)

    def test_x_on_edge(self):
        """X on edge 1: in row0, col1 = 2 lines."""
        board = make_move(make_board(), 1, X)
        c = count_xn_on(board)
        self.assertEqual(c['X1'], 2)

    def test_x_center_o_corner(self):
        """X center, O corner(0): some lines blocked."""
        board = make_move(make_board(), 4, X)
        board = make_move(board, 0, O)
        c = count_xn_on(board)
        # X at 4 has lines: row1(3,4,5), col1(1,4,7), diag(0,4,8), anti(2,4,6)
        # O at 0 has lines: row0(0,1,2), col0(0,3,6), diag(0,4,8)
        # Diag has both X and O -> blocked for both
        # X1: row1, col1, anti-diag = 3
        self.assertEqual(c['X1'], 3)
        # O1: row0, col0 = 2
        self.assertEqual(c['O1'], 2)

    def test_x_wins(self):
        """X wins with top row."""
        board = make_board()
        for pos in [0, 1, 2]:
            board = make_move(board, pos, X)
        c = count_xn_on(board)
        self.assertEqual(c['X3'], 1)

    def test_o_wins(self):
        """O wins with left column."""
        board = make_board()
        for pos in [0, 3, 6]:
            board = make_move(board, pos, O)
        c = count_xn_on(board)
        self.assertEqual(c['O3'], 1)


class TestEvaluate(unittest.TestCase):
    def test_empty_board(self):
        self.assertEqual(evaluate(make_board()), 0)

    def test_x_center(self):
        board = make_move(make_board(), 4, X)
        # X1=4, X2=0, O1=0, O2=0 -> 3*0 + 4 - 0 = 4
        self.assertEqual(evaluate(board), 4)

    def test_x_corner(self):
        board = make_move(make_board(), 0, X)
        # X1=3 -> eval = 3
        self.assertEqual(evaluate(board), 3)

    def test_x_edge(self):
        board = make_move(make_board(), 1, X)
        # X1=2 -> eval = 2
        self.assertEqual(evaluate(board), 2)

    def test_x_center_o_corner(self):
        board = make_move(make_board(), 4, X)
        board = make_move(board, 0, O)
        c = count_xn_on(board)
        expected = 3 * c['X2'] + c['X1'] - (3 * c['O2'] + c['O1'])
        self.assertEqual(evaluate(board), expected)


class TestUtility(unittest.TestCase):
    def test_empty_not_terminal(self):
        self.assertIsNone(utility(make_board()))

    def test_x_wins(self):
        board = make_board()
        for pos in [0, 1, 2]:
            board = make_move(board, pos, X)
        self.assertEqual(utility(board), 1)

    def test_o_wins(self):
        board = make_board()
        for pos in [0, 3, 6]:
            board = make_move(board, pos, O)
        self.assertEqual(utility(board), -1)

    def test_draw(self):
        # X O X
        # X X O
        # O X O
        board = [X, O, X, X, X, O, O, X, O]
        self.assertEqual(utility(board), 0)

    def test_not_terminal(self):
        board = make_move(make_board(), 4, X)
        self.assertIsNone(utility(board))
        self.assertFalse(is_terminal(board))


class TestSymmetry(unittest.TestCase):
    def test_transforms_count(self):
        self.assertEqual(len(SYMMETRY_TRANSFORMS), 8)

    def test_identity(self):
        board = make_move(make_board(), 0, X)
        transformed = apply_transform(board, SYMMETRY_TRANSFORMS[0])
        self.assertEqual(tuple(board), transformed)

    def test_corner_symmetry(self):
        """All 4 corners should be equivalent under symmetry."""
        boards = []
        for corner in [0, 2, 6, 8]:
            b = make_move(make_board(), corner, X)
            boards.append(canonical_form(b))
        self.assertTrue(all(b == boards[0] for b in boards))

    def test_edge_symmetry(self):
        """All 4 edges should be equivalent under symmetry."""
        boards = []
        for edge in [1, 3, 5, 7]:
            b = make_move(make_board(), edge, X)
            boards.append(canonical_form(b))
        self.assertTrue(all(b == boards[0] for b in boards))

    def test_center_unique(self):
        """Center is unique - not equivalent to corners or edges."""
        center = canonical_form(make_move(make_board(), 4, X))
        corner = canonical_form(make_move(make_board(), 0, X))
        edge = canonical_form(make_move(make_board(), 1, X))
        self.assertNotEqual(center, corner)
        self.assertNotEqual(center, edge)
        self.assertNotEqual(corner, edge)


class TestSuccessorsWithSymmetry(unittest.TestCase):
    def test_depth1_three_unique(self):
        """From empty board, X has 3 unique moves: center, corner, edge."""
        board = make_board()
        successors = generate_successors_with_symmetry(board, X)
        self.assertEqual(len(successors), 3)

    def test_successors_cover_categories(self):
        """Verify the 3 unique moves are center, a corner, and an edge."""
        board = make_board()
        successors = generate_successors_with_symmetry(board, X)
        move_positions = [s[0] for s in successors]
        # Should have one from {4}, one from {0,2,6,8}, one from {1,3,5,7}
        has_center = 4 in move_positions
        has_corner = any(m in {0, 2, 6, 8} for m in move_positions)
        has_edge = any(m in {1, 3, 5, 7} for m in move_positions)
        self.assertTrue(has_center)
        self.assertTrue(has_corner)
        self.assertTrue(has_edge)


class TestGameTree(unittest.TestCase):
    def test_tree_depth0(self):
        tree = build_game_tree(make_board(), X, 0, 0)
        self.assertEqual(tree['depth'], 0)
        self.assertEqual(tree['eval'], 0)
        self.assertEqual(tree['children'], [])

    def test_tree_depth1(self):
        tree = build_game_tree(make_board(), X, 0, 1)
        self.assertEqual(tree['depth'], 0)
        self.assertEqual(len(tree['children']), 3)  # 3 unique moves
        for child in tree['children']:
            self.assertEqual(child['depth'], 1)
            self.assertIn('eval', child)

    def test_tree_depth2(self):
        tree = build_game_tree(make_board(), X, 0, 2)
        self.assertEqual(tree['depth'], 0)
        self.assertEqual(len(tree['children']), 3)
        for child in tree['children']:
            self.assertTrue(len(child['children']) > 0)
            for grandchild in child['children']:
                self.assertEqual(grandchild['depth'], 2)
                self.assertIn('eval', grandchild)


class TestMinimax(unittest.TestCase):
    def test_minimax_depth2(self):
        tree = build_game_tree(make_board(), X, 0, 2)
        val = minimax(tree)
        self.assertIn('minimax', tree)
        self.assertEqual(tree['minimax'], val)

        # Root is maximizer (X), so root minimax = max of children's minimax
        child_vals = [c['minimax'] for c in tree['children']]
        self.assertEqual(val, max(child_vals))

    def test_minimax_depth1_children(self):
        """Depth-1 children are minimizer (O), so minimax = min of children's eval."""
        tree = build_game_tree(make_board(), X, 0, 2)
        minimax(tree)
        for child in tree['children']:
            if child['children']:
                child_evals = [gc['eval'] for gc in child['children']]
                self.assertEqual(child['minimax'], min(child_evals))

    def test_minimax_leaf(self):
        tree = build_game_tree(make_board(), X, 0, 0)
        val = minimax(tree)
        self.assertEqual(val, 0)  # empty board eval = 0


class TestAlphaBeta(unittest.TestCase):
    def test_ab_same_as_minimax(self):
        """Alpha-beta should return the same value as minimax."""
        tree_mm = build_game_tree(make_board(), X, 0, 2)
        mm_val = minimax(tree_mm)

        tree_ab = build_game_tree(make_board(), X, 0, 2)
        minimax(tree_ab)
        order_children_for_pruning(tree_ab)
        ab_val = alphabeta(tree_ab)

        self.assertEqual(mm_val, ab_val)

    def test_ab_marks_pruned(self):
        """Alpha-beta should mark some nodes as pruned or not."""
        tree = build_game_tree(make_board(), X, 0, 2)
        minimax(tree)
        order_children_for_pruning(tree)
        alphabeta(tree)

        # All nodes should have 'pruned' attribute set
        def check_pruned_attr(node):
            self.assertIn('pruned', node)
            for child in node.get('children', []):
                check_pruned_attr(child)

        check_pruned_attr(tree)

    def test_mark_pruned(self):
        """Test that _mark_pruned correctly marks a subtree."""
        node = {
            'children': [
                {'children': [], 'eval': 1},
                {'children': [], 'eval': 2},
            ],
            'eval': 0,
        }
        _mark_pruned(node)
        self.assertTrue(node['pruned'])
        self.assertIsNone(node['ab_value'])
        for child in node['children']:
            self.assertTrue(child['pruned'])


class TestEvalSpecificPositions(unittest.TestCase):
    """Test evaluation of specific depth-2 positions."""

    def test_x_center_o_corner(self):
        board = make_move(make_board(), 4, X)
        board = make_move(board, 0, O)
        val = evaluate(board)
        # X at 4: row1, col1, anti-diag unblocked (3 lines with X1)
        # O at 0: row0, col0 unblocked (2 lines with O1)
        # diag is blocked
        # Eval = 3*0 + 3 - (3*0 + 2) = 1
        self.assertEqual(val, 1)

    def test_x_center_o_edge(self):
        board = make_move(make_board(), 4, X)
        board = make_move(board, 1, O)
        val = evaluate(board)
        # X at 4: row1(3,4,5), anti-diag(2,4,6) unblocked = 2 X1 lines
        #   col1(1,4,7) blocked, diag(0,4,8) unblocked = +1 X1
        # Wait, let me recalculate:
        # X at 4, lines: row1(3,4,5), col1(1,4,7), diag(0,4,8), anti(2,4,6)
        # O at 1, lines: row0(0,1,2), col1(1,4,7)
        # col1 has both X and O -> blocked
        # X unblocked: row1, diag, anti-diag -> X1=3
        # O unblocked: row0 -> O1=1
        # Eval = 0 + 3 - (0 + 1) = 2
        self.assertEqual(val, 2)

    def test_x_center_o_center_impossible(self):
        """Can't place O on center if X is already there."""
        board = make_move(make_board(), 4, X)
        self.assertEqual(board[4], X)
        # Just verify the position is taken
        self.assertNotIn(4, get_moves(board))

    def test_x_corner_o_center(self):
        board = make_move(make_board(), 0, X)
        board = make_move(board, 4, O)
        val = evaluate(board)
        # X at 0: row0(0,1,2), col0(0,3,6), diag(0,4,8)
        # O at 4: row1(3,4,5), col1(1,4,7), diag(0,4,8), anti(2,4,6)
        # diag has both -> blocked
        # X unblocked: row0, col0 -> X1=2
        # O unblocked: row1, col1, anti-diag -> O1=3
        # Eval = 0 + 2 - (0 + 3) = -1
        self.assertEqual(val, -1)

    def test_x_corner_o_opposite_corner(self):
        board = make_move(make_board(), 0, X)
        board = make_move(board, 8, O)
        val = evaluate(board)
        # X at 0: row0, col0, diag(0,4,8)
        # O at 8: row2, col2, diag(0,4,8)
        # diag blocked
        # X unblocked: row0, col0 -> X1=2
        # O unblocked: row2, col2 -> O1=2
        # Eval = 0 + 2 - (0 + 2) = 0
        self.assertEqual(val, 0)


if __name__ == '__main__':
    unittest.main()
