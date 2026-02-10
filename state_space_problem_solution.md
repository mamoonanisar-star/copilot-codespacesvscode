# State Space Problem Solution: Agent with Cookie Shops

## Problem Description

An agent navigates a grid where:
- It can move up, down, left, or right (one step at a time)
- It can only move to white cells (not black cells or outside boundaries)
- Cookie shops are located at cells marked with Ci
- The agent starts at cell "S" without cookies
- The agent must reach cell "G" with cookies
- The cost of a path is the number of steps taken

---

## (a) State Space Abstraction

### State Representation

A state in this problem can be modeled as a tuple:

**State = (position, has_cookies)**

Where:
- **position**: The current cell (x, y) coordinates of the agent on the grid
- **has_cookies**: A boolean value indicating whether the agent has collected cookies (True/False)

### Components of the State Space Problem

1. **Initial State**: (S, False)
   - The agent starts at position S without any cookies

2. **Goal State**: (G, True)
   - The agent is at position G and has cookies

3. **Actions**: {UP, DOWN, LEFT, RIGHT}
   - Each action moves the agent one cell in the corresponding direction
   - An action is only valid if it leads to a white cell within the grid boundary

4. **Transition Model**:
   - Moving to a regular white cell: (pos, has_cookies) → (new_pos, has_cookies)
   - Moving to a cookie shop Ci: (pos, has_cookies) → (new_pos, True)
   - Moving to the goal G: (pos, has_cookies) → (G, has_cookies)

5. **Path Cost**: Each step costs 1, so the total path cost equals the number of steps

---

## (b) Number of States

### Calculation

Let's define:
- **W** = number of white cells in the grid (including S, G, and all cookie shops Ci)

Since each position can be combined with two possible cookie states (has_cookies = True or False):

**Total States = 2 × W**

### Breakdown

- For each white cell, the agent can be there **with** cookies: W states
- For each white cell, the agent can be there **without** cookies: W states
- Total: **2W states**

### Note

If the grid has dimensions m × n with B black cells, then:
- W = m × n - B (total cells minus black cells)
- Total States = 2 × (m × n - B)

---

## (c) Admissible Heuristic

### Definition

An admissible heuristic **never overestimates** the cost to reach the goal. It provides an optimistic estimate of the remaining cost.

### Proposed Heuristic

**h(state) = h((pos, has_cookies))**

**Case 1: Agent already has cookies (has_cookies = True)**
```
h((pos, True)) = Manhattan_distance(pos, G)
```

This is simply the Manhattan distance from the current position to the goal G.

**Case 2: Agent does not have cookies yet (has_cookies = False)**
```
h((pos, False)) = min over all cookie shops Ci of [Manhattan_distance(pos, Ci) + Manhattan_distance(Ci, G)]
```

This is the minimum of: (distance to any cookie shop + distance from that shop to G)

### Mathematical Definition

```
h(pos, has_cookies) = 
    if has_cookies:
        |pos.x - G.x| + |pos.y - G.y|
    else:
        min{|pos.x - Ci.x| + |pos.y - Ci.y| + |Ci.x - G.x| + |Ci.y - G.y|} for all cookie shops Ci
```

### Why This Heuristic is Admissible

1. **Manhattan distance is a lower bound**: Since the agent can only move in four cardinal directions (no diagonal moves), the Manhattan distance represents the shortest possible path between two points on a grid, assuming no obstacles.

2. **Ignoring obstacles**: The heuristic does not account for black cells (obstacles), which means the actual path may be longer. This ensures we never overestimate.

3. **For the "no cookies" case**: The agent must visit at least one cookie shop before reaching G. The minimum over all cookie shops of (distance to shop + distance from shop to G) is the shortest possible path that satisfies this requirement, ignoring obstacles.

4. **Optimistic estimate**: Since obstacles can only increase the actual path length, this heuristic will always be less than or equal to the true cost.

### Example

If the agent is at position (2, 3) without cookies, G is at (5, 5), and there are cookie shops at C1=(3, 4) and C2=(4, 3):

- Path through C1: |2-3| + |3-4| + |3-5| + |4-5| = 1 + 1 + 2 + 1 = 5
- Path through C2: |2-4| + |3-3| + |4-5| + |3-5| = 2 + 0 + 1 + 2 = 5

h((2,3), False) = min(5, 5) = 5

---

## Summary Table

| Component | Description |
|-----------|-------------|
| **State** | (position, has_cookies) tuple |
| **Number of States** | 2W where W = number of white cells |
| **Admissible Heuristic** | Manhattan distance to G if has cookies; otherwise min(Manhattan to any cookie shop + Manhattan from shop to G) |
