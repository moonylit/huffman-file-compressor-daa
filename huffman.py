#!/usr/bin/env python3
"""
Huffman File Compression and Analysis Engine
Design and Analysis of Algorithms (DAA) Project

Core Paradigms:
- Greedy Strategy (Optimal Prefix-Free Codes)
- Priority Queues via Min-Heap (O(k log k) Tree Assembly)
- Variable-Length Encoding

Author: DAA Project Engineering Team
"""

import sys
import os
import heapq
from collections import Counter
from typing import Optional, Dict, List


class HuffmanNode:
    """
    Node representation in the Huffman Binary Tree.
    Implements comparison operators for Min-Heap priority queue ordering.
    """
    __slots__ = ('char', 'freq', 'left', 'right', 'seq')

    def __init__(
        self,
        char: Optional[str],
        freq: int,
        left: Optional['HuffmanNode'] = None,
        right: Optional['HuffmanNode'] = None,
        seq: int = 0
    ):
        self.char = char          # Character for leaf node, None for internal node
        self.freq = freq          # Frequency count
        self.left = left          # Left child (represents bit '0')
        self.right = right        # Right child (represents bit '1')
        self.seq = seq            # Monotonic sequence counter for deterministic heap tie-breaking

    def is_leaf(self) -> bool:
        """Returns True if the node is a leaf with no children."""
        return self.left is None and self.right is None

    def __lt__(self, other: 'HuffmanNode') -> bool:
        """
        Priority queue ordering.
        Primary key: Frequency (Min-Heap property)
        Secondary key: Sequence index for deterministic stability
        """
        if self.freq != other.freq:
            return self.freq < other.freq
        return self.seq < other.seq

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HuffmanNode):
            return False
        return self.freq == other.freq and self.char == other.char


class HuffmanEngine:
    """
    Core Huffman Coding Engine implementing greedy tree construction,
    prefix-free binary encoding, and ASCII tree visualization.
    """

    def __init__(self):
        self.root: Optional[HuffmanNode] = None
        self.code_table: Dict[str, str] = {}
        self.reverse_code_table: Dict[str, str] = {}
        self.frequency_table: Dict[str, int] = {}
        self._seq_counter: int = 0

    # -------------------------------------------------------------------------
    # DAA Phase 1: Frequency Analysis O(N)
    # -------------------------------------------------------------------------
    def compute_frequencies(self, text: str) -> Dict[str, int]:
        """
        Scans input string of length N and counts occurrences of each character.
        Time Complexity: O(N) where N is text length.
        Space Complexity: O(k) where k is number of unique characters (|Sigma|).
        """
        self.frequency_table = dict(Counter(text))
        return self.frequency_table

    # -------------------------------------------------------------------------
    # DAA Phase 2: Greedy Tree Construction via Min-Heap O(k log k)
    # -------------------------------------------------------------------------
    def build_tree(self, frequency_table: Dict[str, int]) -> Optional[HuffmanNode]:
        """
        Constructs the optimal prefix tree using a Greedy Min-Heap approach.

        Greedy Choice Property:
        At every step, merge the two subtrees with the lowest frequencies.
        This local optimum leads to the globally optimal prefix-free tree.

        Time Complexity:
        - Heapify k leaf nodes: O(k)
        - (k - 1) iterations of 2 pop + 1 push operations:
          Each pop/push is O(log k). Total = O(k log k).
        Space Complexity: O(k) auxiliary memory.
        """
        self.frequency_table = frequency_table
        if not frequency_table:
            self.root = None
            return None

        heap: List[HuffmanNode] = []
        self._seq_counter = 0

        # Step 1: Initialize min-heap with leaf nodes for all distinct characters
        for char, freq in frequency_table.items():
            self._seq_counter += 1
            node = HuffmanNode(char=char, freq=freq, seq=self._seq_counter)
            heap.append(node)

        heapq.heapify(heap)

        # Edge case: Single distinct character in input (e.g. "AAAAA")
        if len(heap) == 1:
            leaf = heapq.heappop(heap)
            self._seq_counter += 1
            self.root = HuffmanNode(
                char=None,
                freq=leaf.freq,
                left=leaf,
                right=None,
                seq=self._seq_counter
            )
            return self.root

        # Step 2: Greedily extract two minimum nodes and merge into parent node
        while len(heap) > 1:
            left_child = heapq.heappop(heap)    # Lowest frequency
            right_child = heapq.heappop(heap)   # Second lowest frequency

            self._seq_counter += 1
            merged_parent = HuffmanNode(
                char=None,
                freq=left_child.freq + right_child.freq,
                left=left_child,
                right=right_child,
                seq=self._seq_counter
            )
            heapq.heappush(heap, merged_parent)

        self.root = heap[0] if heap else None
        return self.root

    # -------------------------------------------------------------------------
    # DAA Phase 3: Variable-Length Prefix Code Generation O(k)
    # -------------------------------------------------------------------------
    def generate_codes(self, root: Optional[HuffmanNode] = None) -> Dict[str, str]:
        """
        Traverses Huffman tree via DFS to assign variable-length binary prefix codes.
        Left edge = '0', Right edge = '1'.

        Prefix-Free Property:
        Every character resides exclusively at a LEAF node.
        Therefore, no assigned code can be a prefix of any other code.
        Time Complexity: O(k) where k is alphabet size.
        """
        if root is None:
            root = self.root

        self.code_table = {}
        self.reverse_code_table = {}

        if root is None:
            return self.code_table

        # Handle single-unique-symbol edge case
        if root.left and root.right is None and root.left.is_leaf():
            char = root.left.char
            if char is not None:
                self.code_table[char] = "0"
                self.reverse_code_table["0"] = char
            return self.code_table

        def _dfs(node: Optional[HuffmanNode], current_code: str):
            if node is None:
                return

            if node.is_leaf() and node.char is not None:
                # Leaf node: assign prefix code
                self.code_table[node.char] = current_code if current_code else "0"
                self.reverse_code_table[self.code_table[node.char]] = node.char
                return

            if node.left:
                _dfs(node.left, current_code + "0")
            if node.right:
                _dfs(node.right, current_code + "1")

        _dfs(root, "")
        return self.code_table

    # -------------------------------------------------------------------------
    # DAA Phase 4: Variable-Length Encoding O(N)
    # -------------------------------------------------------------------------
    def encode_text(self, text: str) -> str:
        """
        Encodes source string into a continuous binary bitstring using code table.
        Time Complexity: O(N) where N is text length.
        """
        if not text:
            return ""

        if not self.code_table:
            self.compute_frequencies(text)
            self.build_tree(self.frequency_table)
            self.generate_codes(self.root)

        encoded_bits = "".join(self.code_table[char] for char in text)
        return encoded_bits

    # -------------------------------------------------------------------------
    # Visual ASCII Tree Generator
    # -------------------------------------------------------------------------
    def render_ascii_tree(self, root: Optional[HuffmanNode] = None) -> str:
        """
        Generates an ASCII hierarchical tree diagram for terminal inspection.
        Uses pure ASCII symbols for 100% compatibility across all OS consoles.
        """
        if root is None:
            root = self.root
        if root is None:
            return "<Empty Tree>"

        lines: List[str] = []

        def _format_char(c: Optional[str]) -> str:
            if c is None:
                return ""
            special = {"\n": "\\n", "\t": "\\t", " ": "' '", "\r": "\\r"}
            return special.get(c, repr(c))

        def _build_lines(node: Optional[HuffmanNode], prefix: str = "", is_left: bool = True, is_root: bool = True):
            if node is None:
                return

            if is_root:
                label = f"[{node.freq}] (ROOT)"
                lines.append(label)
            else:
                branch = "+-- (0) " if is_left else "\\-- (1) "
                if node.is_leaf():
                    label = f"{branch}Leaf {_format_char(node.char)} [freq={node.freq}]"
                else:
                    label = f"{branch}Node [{node.freq}]"
                lines.append(prefix + label)

            new_prefix = prefix + ("|   " if is_left and not is_root else "    ")
            children = []
            if node.left:
                children.append((node.left, True))
            if node.right:
                children.append((node.right, False))

            for i, (child, left_flag) in enumerate(children):
                _build_lines(child, prefix + ("    " if is_root else ("|   " if is_left else "    ")), left_flag, False)

        _build_lines(root)
        return "\n".join(lines)


def run_cli():
    import argparse

    parser = argparse.ArgumentParser(
        description="Huffman Coding Engine (DAA Core Implementation)",
    )
    parser.add_argument("-a", "--analyze", type=str, metavar="TEXT", help="Analyze string frequencies and codes")
    parser.add_argument("-v", "--visualize", type=str, metavar="TEXT", help="Print ASCII tree and prefix codes")
    args = parser.parse_args()

    engine = HuffmanEngine()
    target_text = args.visualize or args.analyze or "ABRACADABRA"

    freqs = engine.compute_frequencies(target_text)
    engine.build_tree(freqs)
    codes = engine.generate_codes()
    bits = engine.encode_text(target_text)

    print("=" * 60)
    print(" HUFFMAN CODING CORE ENGINE")
    print("=" * 60)
    print(f"Input text: {target_text!r} ({len(target_text)} chars)")
    print(f"Distinct symbols: {len(freqs)}")
    print(f"Encoded bit length: {len(bits)} bits (vs {len(target_text)*8} ASCII bits)")
    print("-" * 60)
    print("PREFIX CODEBOOK:")
    for char, freq in sorted(freqs.items(), key=lambda x: -x[1]):
        print(f"  {char!r:>6}: freq={freq:<4} -> code={codes[char]}")
    print("-" * 60)
    print("ASCII TREE:")
    print(engine.render_ascii_tree())


if __name__ == "__main__":
    run_cli()
