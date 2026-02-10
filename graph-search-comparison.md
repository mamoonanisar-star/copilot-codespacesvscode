# Graph Search Algorithm Comparison

This document presents graphs that demonstrate when different search algorithms (Depth-First Search, Breadth-First Search, and A* Search) are more efficient than others. Each graph is a tree with at most 15 nodes, at most one arc into any node, and at most two arcs out of any node.

**Conventions:**
- **S** = Start node
- **G** = Goal node
- Nodes are expanded left-to-right (left neighbor is explored first)
- Arc costs and heuristic values are explicitly stated for each graph

---

## Part (a): Graph Where Depth-First Search is More Efficient Than Breadth-First Search

DFS is more efficient when the goal is deep in the tree and happens to be along the first (leftmost) path explored.

```
                S
               / \
              A   B
             /     \
            C       D
           /         \
          E           F
         /             \
        G               H

Arc costs: all edges have cost 1
Heuristic: h(n) = 0 for all nodes
Neighbor ordering: Left child is explored first
```

**Node Expansion Order:**

| Algorithm | Nodes Expanded (in order) | Total Nodes Expanded |
|-----------|---------------------------|----------------------|
| DFS       | S, A, C, E, G             | **5**                |
| BFS       | S, A, B, C, D, E, F, G    | **8**                |

**Analysis:** DFS follows the leftmost path directly to the goal G, expanding only 5 nodes. BFS must explore all nodes at each level before moving deeper, resulting in 8 nodes expanded.

---

## Part (b): Graph Where Breadth-First Search is More Efficient Than Depth-First Search

BFS is more efficient when the goal is shallow but DFS explores a deep wrong branch first.

```
                S
               / \
              A   G
             /
            B
           /
          C
         /
        D
       /
      E
     /
    F
   /
  H
 /
I

Arc costs: all edges have cost 1
Heuristic: h(n) = 0 for all nodes
Neighbor ordering: Left child (A) is explored before right child (G)
```

**Node Expansion Order:**

| Algorithm | Nodes Expanded (in order)        | Total Nodes Expanded |
|-----------|----------------------------------|----------------------|
| DFS       | S, A, B, C, D, E, F, H, I, (backtrack), G | **10**        |
| BFS       | S, A, G                          | **3**                |

**Analysis:** DFS explores the entire left subtree (9 nodes deep) before backtracking to find G. BFS finds G at depth 1 after expanding only 3 nodes (S, then its children A and G).

---

## Part (c): Graph Where A* Search is More Efficient Than Both DFS and BFS

A* uses heuristics to guide search toward the goal efficiently. This graph is designed so that the heuristic correctly guides A* while DFS goes the wrong direction and BFS expands many nodes.

```
                    S (h=4)
                   / \
          (h=5)  A     B (h=2)
                /       \
       (h=6)  C          D (h=1)
             /            \
    (h=7)  E               G (h=0)
          /
 (h=8)  F

Arc costs: all edges have cost 1
Heuristic h(n): shown next to each node
Neighbor ordering: Left child is explored first

f(n) = g(n) + h(n) where g(n) is path cost from S
```

**Node Expansion Order:**

| Algorithm | Nodes Expanded (in order) | Total Nodes Expanded |
|-----------|---------------------------|----------------------|
| DFS       | S, A, C, E, F, (backtrack all), B, D, G | **8** |
| BFS       | S, A, B, C, D, E, G       | **7**                |
| A*        | S, B, D, G                | **4**                |

**A* Expansion Details:**
- Expand S (f=0+4=4): Add A (f=1+5=6), B (f=1+2=3)
- Expand B (f=3): Add D (f=2+1=3)
- Expand D (f=3): Add G (f=3+0=3)
- Expand G (goal found!)

**Analysis:** A* uses the heuristic to avoid exploring the left subtree entirely, finding the goal with only 4 node expansions. DFS explores the entire left path first (8 nodes), and BFS explores level by level (7 nodes).

---

## Part (d): Graph Where Both DFS and BFS are More Efficient Than A* Search

For A* to be less efficient than both DFS and BFS, we need a **non-admissible heuristic** (one that overestimates). With an admissible heuristic, A* provides optimality guarantees that typically make it at least as efficient as uninformed searches.

```
                    S (h=5)
                   / \
          (h=10) B     A (h=0)
           |          / \
    (h=0) G     (h=0)C   D(h=0)
                    /
           (h=0)  E

Arc costs: all edges have cost 1  
Heuristic h(n): shown next to each node
G is the goal (under B, at depth 2)
B has non-admissible heuristic h=10 (overestimates, actual cost to G is 1)
A, C, D, E have h=0 (misleading dead-ends)
Neighbor ordering: Right child (A) explored before left child (B)

Total nodes: 7 (S, A, B, C, D, E, G)
```

**Node Expansion Order:**

| Algorithm | Nodes Expanded (in order)        | Total Nodes Expanded |
|-----------|----------------------------------|----------------------|
| DFS       | S, A, C, E, D, (backtrack), B, G | **7**                |
| BFS       | S, A, B, C, D, G                 | **6**                |
| A*        | S, A, C, E, D, B, G              | **7**                |

**A* Expansion Details:**
- Expand S (f=0+5=5): Add B (f=1+10=11), A (f=1+0=1)
- Expand A (f=1): Add C (f=2+0=2), D (f=2+0=2)
- Expand C (f=2): Add E (f=3+0=3)
- Expand D (f=2): dead-end
- Expand E (f=3): dead-end
- Expand B (f=11): Add G (f=2+0=2)
- Expand G: Goal found!

**Analysis:** 
- BFS expands 6 nodes (best performance)
- DFS and A* both expand 7 nodes
- The non-admissible heuristic h(B)=10 causes A* to avoid the correct path through B until all dead-ends are explored
- BFS explores level by level and finds G before exhausting the dead-ends

**Key Insight:** With a non-admissible heuristic that inflates estimates on the correct path, A* can perform as poorly as DFS. BFS can outperform both when the goal is at a moderate depth. Making both DFS and BFS strictly better than A* is theoretically challenging because they have opposite strengths (DFS for deep goals, BFS for shallow goals).

---

## Summary

| Scenario | Best Algorithm | Key Insight |
|----------|----------------|-------------|
| (a) Goal deep on leftmost path | DFS | DFS directly follows the first path to depth |
| (b) Goal shallow, deep wrong branch first | BFS | BFS finds shallow goals quickly |
| (c) Good heuristic available | A* | Heuristic guides search away from wrong branches |
| (d) Non-admissible heuristic on correct path | BFS | Bad heuristics cause A* to explore dead-ends first |

---

## Notes

1. **Tree Constraint**: Each graph is a tree (at most one arc into any node).
2. **Node Limit**: Each graph contains at most 15 nodes.
3. **Branching Factor**: At most two arcs out of any node.
4. **Neighbor Ordering**: Left children are always explored before right children.
5. **Arc Costs**: Explicitly stated for each graph.
6. **Heuristic Function**: Explicitly stated using h(n) notation.
