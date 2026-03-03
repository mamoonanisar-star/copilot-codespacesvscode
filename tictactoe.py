"""
Tic-Tac-Toe Game Tree Analysis

Implements game tree generation, evaluation function, minimax algorithm,
and alpha-beta pruning for tic-tac-toe.

Evaluation function: Eval(s) = 3*X2(s) + X1(s) - (3*O2(s) + O1(s))
where Xn = number of lines with exactly n X's and no O's,
      On = number of lines with exactly n O's and no X's.

Utility: +1 if X3=1, -1 if O3=1, 0 for other terminal positions.
"""

# All 8 lines: 3 rows, 3 columns, 2 diagonals
LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
    (0, 4, 8), (2, 4, 6),              # diagonals
]

EMPTY = '.'
X = 'X'
O = 'O'

# Symmetry transformations for a 3x3 board (indices 0-8 mapped as 3x3 grid)
# Board positions:
# 0 1 2
# 3 4 5
# 6 7 8
SYMMETRY_TRANSFORMS = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8],  # identity
    [6, 3, 0, 7, 4, 1, 8, 5, 2],  # 90° clockwise
    [8, 7, 6, 5, 4, 3, 2, 1, 0],  # 180°
    [2, 5, 8, 1, 4, 7, 0, 3, 6],  # 270° clockwise
    [2, 1, 0, 5, 4, 3, 8, 7, 6],  # horizontal reflection
    [6, 7, 8, 3, 4, 5, 0, 1, 2],  # vertical reflection
    [0, 3, 6, 1, 4, 7, 2, 5, 8],  # main diagonal reflection
    [8, 5, 2, 7, 4, 1, 6, 3, 0],  # anti-diagonal reflection
]


def make_board():
    """Create an empty 3x3 board."""
    return [EMPTY] * 9


def apply_transform(board, transform):
    """Apply a symmetry transformation to a board."""
    return tuple(board[i] for i in transform)


def canonical_form(board):
    """Return the canonical (smallest) form of a board under all symmetries."""
    return min(apply_transform(board, t) for t in SYMMETRY_TRANSFORMS)


def count_xn_on(board):
    """
    Count Xn and On values for the board.

    Returns dict with keys 'X1', 'X2', 'X3', 'O1', 'O2', 'O3'.
    Xn = number of lines with exactly n X's and no O's.
    On = number of lines with exactly n O's and no X's.
    """
    counts = {'X1': 0, 'X2': 0, 'X3': 0, 'O1': 0, 'O2': 0, 'O3': 0}
    for line in LINES:
        cells = [board[i] for i in line]
        x_count = cells.count(X)
        o_count = cells.count(O)
        if x_count > 0 and o_count == 0:
            counts[f'X{x_count}'] += 1
        elif o_count > 0 and x_count == 0:
            counts[f'O{o_count}'] += 1
    return counts


def evaluate(board):
    """
    Compute the linear evaluation function:
    Eval(s) = 3*X2(s) + X1(s) - (3*O2(s) + O1(s))
    """
    c = count_xn_on(board)
    return 3 * c['X2'] + c['X1'] - (3 * c['O2'] + c['O1'])


def utility(board):
    """
    Terminal utility: +1 if X wins (X3=1), -1 if O wins (O3=1), 0 otherwise.
    Returns None if the position is not terminal.
    """
    c = count_xn_on(board)
    if c['X3'] >= 1:
        return 1
    if c['O3'] >= 1:
        return -1
    if all(cell != EMPTY for cell in board):
        return 0
    return None


def is_terminal(board):
    """Check if the board is in a terminal state."""
    return utility(board) is not None


def get_moves(board):
    """Return list of available moves (empty positions)."""
    return [i for i in range(9) if board[i] == EMPTY]


def make_move(board, pos, player):
    """Return a new board with the move applied."""
    new_board = list(board)
    new_board[pos] = player
    return new_board


def generate_successors_with_symmetry(board, player):
    """
    Generate unique successor boards considering symmetry.

    Returns list of (move, new_board) pairs, one per symmetry-equivalent class.
    """
    seen = set()
    successors = []
    for move in get_moves(board):
        new_board = make_move(board, move, player)
        canon = canonical_form(new_board)
        if canon not in seen:
            seen.add(canon)
            successors.append((move, new_board))
    return successors


def build_game_tree(board, player, depth, max_depth):
    """
    Build a game tree from the given board state down to max_depth.

    Returns a tree node dict with:
      - 'board': the board state
      - 'player': whose turn it is
      - 'eval': evaluation at leaf or backed-up minimax value
      - 'children': list of child nodes (each with 'move' key too)
      - 'depth': current depth
    """
    node = {
        'board': list(board),
        'player': player,
        'depth': depth,
        'children': [],
        'eval': evaluate(board),
    }

    if is_terminal(board) or depth >= max_depth:
        return node

    successors = generate_successors_with_symmetry(board, player)
    next_player = O if player == X else X

    for move, new_board in successors:
        child = build_game_tree(new_board, next_player, depth + 1, max_depth)
        child['move'] = move
        node['children'].append(child)

    return node


def minimax(node):
    """
    Apply minimax algorithm to assign backed-up values.

    X is the maximizer, O is the minimizer.
    Modifies node['minimax'] in place and returns the minimax value.
    """
    if not node['children']:
        node['minimax'] = node['eval']
        return node['minimax']

    child_values = [minimax(child) for child in node['children']]

    if node['player'] == X:
        node['minimax'] = max(child_values)
    else:
        node['minimax'] = min(child_values)

    return node['minimax']


def alphabeta(node, alpha=float('-inf'), beta=float('inf')):
    """
    Apply alpha-beta pruning. Marks nodes that are evaluated vs pruned.

    Sets node['pruned'] = False for evaluated nodes, True for pruned.
    Returns the alpha-beta value.
    """
    node['pruned'] = False

    if not node['children']:
        node['ab_value'] = node['eval']
        return node['ab_value']

    if node['player'] == X:  # maximizer
        value = float('-inf')
        for child in node['children']:
            child_val = alphabeta(child, alpha, beta)
            value = max(value, child_val)
            alpha = max(alpha, value)
            if alpha >= beta:
                # Prune remaining children
                idx = node['children'].index(child)
                for pruned_child in node['children'][idx + 1:]:
                    _mark_pruned(pruned_child)
                break
        node['ab_value'] = value
    else:  # minimizer
        value = float('inf')
        for child in node['children']:
            child_val = alphabeta(child, alpha, beta)
            value = min(value, child_val)
            beta = min(beta, value)
            if alpha >= beta:
                idx = node['children'].index(child)
                for pruned_child in node['children'][idx + 1:]:
                    _mark_pruned(pruned_child)
                break
        node['ab_value'] = value

    return node['ab_value']


def _mark_pruned(node):
    """Mark a node and all its descendants as pruned."""
    node['pruned'] = True
    node['ab_value'] = None
    for child in node.get('children', []):
        _mark_pruned(child)


def order_children_for_pruning(node):
    """
    Reorder children for optimal alpha-beta pruning.

    For maximizer (X): sort children by eval descending (best first).
    For minimizer (O): sort children by eval ascending (best first).
    Recursively applies to all levels.
    """
    if not node['children']:
        return

    for child in node['children']:
        order_children_for_pruning(child)

    if node['player'] == X:
        node['children'].sort(key=lambda c: c.get('minimax', c.get('eval', 0)),
                              reverse=True)
    else:
        node['children'].sort(key=lambda c: c.get('minimax', c.get('eval', 0)))


def pos_label(pos):
    """Convert position index to row,col label."""
    return f"({pos // 3},{pos % 3})"


def board_to_str(board):
    """Pretty-print a board."""
    rows = []
    for r in range(3):
        rows.append(' '.join(board[r * 3:(r + 1) * 3]))
    return '\n'.join(rows)


def print_tree(node, indent=0):
    """Print the game tree with evaluations and minimax values."""
    prefix = '  ' * indent
    board = node['board']

    move_str = ""
    if 'move' in node:
        move_str = f" [move: {pos_label(node['move'])}]"

    pruned_str = ""
    if node.get('pruned'):
        pruned_str = " (PRUNED)"

    eval_str = f"eval={node.get('eval', '?')}"
    minimax_str = f"minimax={node.get('minimax', '?')}"
    ab_str = ""
    if 'ab_value' in node:
        ab_str = f" ab={node.get('ab_value', '?')}"

    print(f"{prefix}Depth {node['depth']}{move_str}{pruned_str}")
    for row in board_to_str(board).split('\n'):
        print(f"{prefix}  {row}")
    print(f"{prefix}  {eval_str}, {minimax_str}{ab_str}")
    print()

    for child in node['children']:
        print_tree(child, indent + 1)


def run_analysis():
    """Run the full game tree analysis and print results."""
    board = make_board()

    print("=" * 60)
    print("TIC-TAC-TOE GAME TREE ANALYSIS")
    print("=" * 60)
    print()
    print("Evaluation function: Eval(s) = 3*X2(s) + X1(s) - (3*O2(s) + O1(s))")
    print("Utility: +1 if X3=1, -1 if O3=1, 0 for other terminals")
    print()

    # (a) Build game tree to depth 2 with symmetry
    print("-" * 60)
    print("(a) Game tree from empty board to depth 2 (with symmetry)")
    print("-" * 60)
    tree = build_game_tree(board, X, 0, 2)

    # (b) & (c) Mark evaluations and compute minimax
    minimax(tree)

    print()
    print("(b) Evaluations at depth 2 and (c) minimax backed-up values:")
    print()
    print_tree(tree)

    # (c) Best starting move
    best_child = max(tree['children'], key=lambda c: c['minimax'])
    print("-" * 60)
    print(f"(c) Best starting move: {pos_label(best_child['move'])}")
    print(f"    Backed-up minimax value at root: {tree['minimax']}")
    print("-" * 60)
    print()

    # (d) Alpha-beta pruning with optimal ordering
    print("-" * 60)
    print("(d) Alpha-beta pruning (optimal node ordering)")
    print("-" * 60)
    # Rebuild tree for fresh alpha-beta analysis
    tree_ab = build_game_tree(board, X, 0, 2)
    minimax(tree_ab)  # Need minimax values for optimal ordering
    order_children_for_pruning(tree_ab)
    alphabeta(tree_ab)

    print()
    print("Nodes marked (PRUNED) would not be evaluated:")
    print()
    print_tree(tree_ab)

    # Collect pruned depth-2 nodes
    pruned_nodes = []
    for child in tree_ab['children']:
        for grandchild in child['children']:
            if grandchild.get('pruned'):
                pruned_nodes.append(grandchild)

    if pruned_nodes:
        print(f"Pruned depth-2 nodes ({len(pruned_nodes)}):")
        for pn in pruned_nodes:
            print(f"  Move: {pos_label(pn['move'])}")
            for row in board_to_str(pn['board']).split('\n'):
                print(f"    {row}")
            print()
    else:
        print("No depth-2 nodes pruned (tree is too shallow for pruning).")

    return tree, tree_ab


if __name__ == '__main__':
    run_analysis()
