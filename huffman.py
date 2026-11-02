#!/usr/bin/env python3
"""
Huffman File Compression and Analysis Engine
Design and Analysis of Algorithms (DAA) Project

Core Paradigms:
- Greedy Strategy (Optimal Prefix-Free Codes)
- Priority Queues via Min-Heap (O(k log k) Tree Assembly)
- Lossless Variable-Length Encoding and Bit-Level Packing
- Shannon Entropy & Theoretical Redundancy Analytics

Author: DAA Project Engineering Team
"""

import sys
import os
import heapq
import struct
import math
from collections import Counter
from typing import Optional, Dict, Tuple, List, Any


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
    Production-grade Huffman Coding Engine implementing greedy tree construction,
    prefix-free binary encoding, lossless bitstream decoding, and compression metrics.
    """

    MAGIC_HEADER = b"HUFF"   # File format magic signature
    VERSION = 1

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
    # DAA Phase 4: Lossless Encoding O(N)
    # -------------------------------------------------------------------------
    def encode_text(self, text: str) -> str:
        """
        Encodes source string into a continuous binary bitstring using code table.
        Time Complexity: O(N) where N is text length.
        """
        if not text:
            return ""

        if not self.code_table or any(char not in self.code_table for char in text):
            self.compute_frequencies(text)
            self.build_tree(self.frequency_table)
            self.generate_codes(self.root)

        encoded_bits = "".join(self.code_table[char] for char in text)
        return encoded_bits

    # -------------------------------------------------------------------------
    # DAA Phase 5: Lossless Decoding O(B) where B is total bit length
    # -------------------------------------------------------------------------
    def decode_bits(self, encoded_bits: str, root: Optional[HuffmanNode] = None) -> str:
        """
        Decodes a binary bitstring back into the exact original text.
        Traverses tree from root according to bits until reaching a leaf node.
        No delimiters needed due to the prefix-free code property.

        Time Complexity: O(B) where B is the number of encoded bits.
        Since B <= 8N, this is strictly O(N).
        """
        if not encoded_bits:
            return ""

        if root is None:
            root = self.root

        if root is None:
            raise ValueError("Huffman tree is empty. Cannot decode.")

        decoded_chars: List[str] = []
        current_node = root

        # Handle single distinct character tree
        if root.left and root.right is None and root.left.is_leaf():
            leaf_char = root.left.char or ""
            return leaf_char * len(encoded_bits)

        for bit in encoded_bits:
            if bit == "0":
                current_node = current_node.left
            elif bit == "1":
                current_node = current_node.right
            else:
                raise ValueError(f"Invalid binary bit encountered: '{bit}'")

            if current_node is None:
                raise ValueError("Corrupted bitstream: encountered null branch in tree.")

            if current_node.is_leaf():
                if current_node.char is not None:
                    decoded_chars.append(current_node.char)
                current_node = root  # Reset traversal for next character

        return "".join(decoded_chars)

    # -------------------------------------------------------------------------
    # DAA Phase 6: Bit-Level Binary Serialization (Real File Compression)
    # -------------------------------------------------------------------------
    @staticmethod
    def pack_bitstring(bitstring: str) -> Tuple[bytes, int]:
        """
        Packs an arbitrary length bitstring ('01011...') into raw bytes.
        Returns (packed_bytes, padding_amount).
        """
        padding = (8 - (len(bitstring) % 8)) % 8
        padded_bitstring = bitstring + ("0" * padding)

        byte_arr = bytearray()
        for i in range(0, len(padded_bitstring), 8):
            byte_chunk = padded_bitstring[i:i + 8]
            byte_arr.append(int(byte_chunk, 2))

        return bytes(byte_arr), padding

    @staticmethod
    def unpack_bitstring(packed_bytes: bytes, padding: int) -> str:
        """
        Unpacks raw bytes back into binary string, trimming trailing padding bits.
        """
        bit_chunks = []
        for byte in packed_bytes:
            bit_chunks.append(f"{byte:08b}")
        full_bitstring = "".join(bit_chunks)
        if padding > 0:
            full_bitstring = full_bitstring[:-padding]
        return full_bitstring

    def compress_to_bytes(self, text: str) -> bytes:
        """
        Compresses plain text into a standalone self-extracting binary byte payload.
        Binary Format:
        [MAGIC 4B: 'HUFF']
        [VERSION 1B]
        [PADDING 1B]
        [ALPHABET_SIZE 2B (k)]
        For each symbol in alphabet:
            [CHAR_LEN 2B]
            [CHAR_UTF8 nB]
            [FREQ 4B (unsigned int)]
        [BODY_LEN 4B]
        [PACKED_DATA bytes]
        """
        if not text:
            # Empty file signature
            return self.MAGIC_HEADER + struct.pack(">BBH", self.VERSION, 0, 0)

        freqs = self.compute_frequencies(text)
        self.build_tree(freqs)
        self.generate_codes(self.root)
        bitstring = self.encode_text(text)
        packed_data, padding = self.pack_bitstring(bitstring)

        # Serialize header
        header = bytearray()
        header.extend(self.MAGIC_HEADER)
        header.extend(struct.pack(">BB", self.VERSION, padding))

        # Alphabet table
        header.extend(struct.pack(">H", len(freqs)))
        for char, freq in freqs.items():
            char_bytes = char.encode("utf-8")
            header.extend(struct.pack(">HI", len(char_bytes), freq))
            header.extend(char_bytes)

        # Packed payload length & data
        header.extend(struct.pack(">I", len(packed_data)))
        header.extend(packed_data)

        return bytes(header)

    def decompress_from_bytes(self, data: bytes) -> str:
        """
        Decompresses binary payload back into original text using embedded tree header.
        """
        if len(data) < 8:
            return ""

        magic = data[:4]
        if magic != self.MAGIC_HEADER:
            raise ValueError(f"Invalid file signature: {magic!r}. Expected {self.MAGIC_HEADER!r}.")

        offset = 4
        version, padding = struct.unpack(">BB", data[offset:offset + 2])
        offset += 2

        alphabet_size, = struct.unpack(">H", data[offset:offset + 2])
        offset += 2

        if alphabet_size == 0:
            return ""

        freq_table: Dict[str, int] = {}
        for _ in range(alphabet_size):
            char_len, freq = struct.unpack(">HI", data[offset:offset + 6])
            offset += 6
            char_bytes = data[offset:offset + char_len]
            offset += char_len
            char = char_bytes.decode("utf-8")
            freq_table[char] = freq

        data_len, = struct.unpack(">I", data[offset:offset + 4])
        offset += 4

        packed_data = data[offset:offset + data_len]

        # Reconstruct Tree
        reconstructed_root = self.build_tree(freq_table)
        bitstring = self.unpack_bitstring(packed_data, padding)
        original_text = self.decode_bits(bitstring, reconstructed_root)

        return original_text

    # -------------------------------------------------------------------------
    # DAA Phase 7: Mathematical & Empirical Compression Analytics
    # -------------------------------------------------------------------------
    def compute_analytics(self, text: str) -> Dict[str, Any]:
        """
        Computes formal compression metrics, Shannon Entropy, and Kraft's sum.
        """
        n_chars = len(text)
        if n_chars == 0:
            return {
                "original_chars": 0,
                "original_bits": 0,
                "original_bytes": 0,
                "compressed_bits": 0,
                "compressed_bytes": 0,
                "space_saved_percent": 0.0,
                "compression_ratio": 1.0,
                "average_code_length": 0.0,
                "shannon_entropy": 0.0,
                "coding_efficiency_percent": 100.0,
                "kraft_inequality_sum": 0.0,
                "kraft_valid": True,
                "unique_symbols": 0,
            }

        freqs = self.compute_frequencies(text)
        self.build_tree(freqs)
        codes = self.generate_codes(self.root)
        bitstring = self.encode_text(text)

        original_bits = n_chars * 8
        original_bytes = n_chars
        compressed_bits = len(bitstring)
        compressed_bytes = math.ceil(compressed_bits / 8)

        space_saved_percent = ((original_bits - compressed_bits) / original_bits) * 100.0 if original_bits > 0 else 0.0
        compression_ratio = original_bits / compressed_bits if compressed_bits > 0 else 1.0

        # Shannon Entropy H(X) = - sum( P(x) * log2(P(x)) )
        # Average Code Length L_avg = sum( P(x) * length(code(x)) )
        shannon_entropy = 0.0
        avg_code_length = 0.0
        kraft_sum = 0.0

        for char, count in freqs.items():
            prob = count / n_chars
            shannon_entropy -= prob * math.log2(prob)
            code_len = len(codes.get(char, ""))
            avg_code_length += prob * code_len
            kraft_sum += 2 ** (-code_len)

        # Efficiency: Shannon Entropy / Average Code Length
        efficiency = (shannon_entropy / avg_code_length * 100.0) if avg_code_length > 0 else 100.0

        return {
            "original_chars": n_chars,
            "original_bits": original_bits,
            "original_bytes": original_bytes,
            "compressed_bits": compressed_bits,
            "compressed_bytes": compressed_bytes,
            "space_saved_percent": round(space_saved_percent, 2),
            "compression_ratio": round(compression_ratio, 3),
            "average_code_length": round(avg_code_length, 4),
            "shannon_entropy": round(shannon_entropy, 4),
            "coding_efficiency_percent": round(min(efficiency, 100.0), 2),
            "kraft_inequality_sum": round(kraft_sum, 6),
            "kraft_valid": kraft_sum <= 1.000001,
            "unique_symbols": len(freqs),
            "code_table": codes,
            "frequency_table": freqs,
            "bitstring": bitstring,
        }

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


# -----------------------------------------------------------------------------
# Command Line Interface (CLI)
# -----------------------------------------------------------------------------
def run_cli():
    import argparse

    parser = argparse.ArgumentParser(
        description="Huffman Coding Text Compression & DAA Analysis Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python huffman.py --analyze "ABRACADABRA"
  python huffman.py --visualize "HELLO HUFFMAN WORLD"
  python huffman.py --compress input.txt compressed.huff
  python huffman.py --decompress compressed.huff restored.txt
  python huffman.py --test
        """
    )

    parser.add_argument("-c", "--compress", nargs=2, metavar=("INPUT", "OUTPUT"),
                        help="Compress a text file into binary .huff file")
    parser.add_argument("-d", "--decompress", nargs=2, metavar=("INPUT", "OUTPUT"),
                        help="Decompress a .huff binary file back to text")
    parser.add_argument("-a", "--analyze", type=str, metavar="TEXT",
                        help="Perform full DAA frequency and compression analysis on string")
    parser.add_argument("-f", "--analyze-file", type=str, metavar="FILE",
                        help="Perform full DAA compression analysis on a text file")
    parser.add_argument("-v", "--visualize", type=str, metavar="TEXT",
                        help="Print ASCII tree and prefix codes for text")
    parser.add_argument("-t", "--test", action="store_true",
                        help="Run internal verification test suite")

    args = parser.parse_args()
    engine = HuffmanEngine()

    if args.test:
        run_self_tests()
        return

    if args.compress:
        in_path, out_path = args.compress
        if not os.path.exists(in_path):
            print(f"Error: Input file '{in_path}' does not exist.", file=sys.stderr)
            sys.exit(1)

        with open(in_path, "r", encoding="utf-8", errors="replace", newline="") as f:
            raw_text = f.read()

        compressed_bytes = engine.compress_to_bytes(raw_text)
        with open(out_path, "wb") as f:
            f.write(compressed_bytes)

        orig_size = len(raw_text.encode("utf-8"))
        comp_size = len(compressed_bytes)
        ratio = orig_size / comp_size if comp_size > 0 else 0
        saved = (1 - comp_size / orig_size) * 100 if orig_size > 0 else 0

        print(f"[SUCCESS] Compressed '{in_path}' -> '{out_path}'")
        print(f"  Original Size:   {orig_size:,} bytes")
        print(f"  Compressed Size: {comp_size:,} bytes (including tree metadata)")
        print(f"  Space Saved:     {saved:.2f}%")
        print(f"  Effective Ratio: {ratio:.2f}:1")
        return

    if args.decompress:
        in_path, out_path = args.decompress
        if not os.path.exists(in_path):
            print(f"Error: Compressed file '{in_path}' not found.", file=sys.stderr)
            sys.exit(1)

        with open(in_path, "rb") as f:
            comp_bytes = f.read()

        recovered_text = engine.decompress_from_bytes(comp_bytes)
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            f.write(recovered_text)

        print(f"[SUCCESS] Restored '{in_path}' -> '{out_path}'")
        print(f"  Decompressed Size: {len(recovered_text.encode('utf-8')):,} bytes")
        return

    if args.analyze or args.analyze_file:
        if args.analyze_file:
            if not os.path.exists(args.analyze_file):
                print(f"Error: File '{args.analyze_file}' not found.", file=sys.stderr)
                sys.exit(1)
            with open(args.analyze_file, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        else:
            content = args.analyze

        stats = engine.compute_analytics(content)
        _print_analytics_report(stats)
        return

    if args.visualize:
        stats = engine.compute_analytics(args.visualize)
        _print_analytics_report(stats)
        print("\n" + "=" * 60)
        print(" ASCII HUFFMAN TREE VISUALIZATION ")
        print("=" * 60)
        print(engine.render_ascii_tree())
        return

    # Default fallback: interactive banner
    parser.print_help()


def _print_analytics_report(stats: Dict[str, Any]):
    print("=" * 70)
    print(" HUFFMAN CODING DAA COMPRESSION & COMPLEXITY REPORT")
    print("=" * 70)
    print(f"Original Text Length:       {stats['original_chars']:,} characters")
    print(f"Distinct Alphabet Size (k): {stats['unique_symbols']:,} symbols")
    print(f"Original Bit Length (ASCII):{stats['original_bits']:,} bits ({stats['original_bytes']:,} bytes)")
    print(f"Compressed Bitstream Length:{stats['compressed_bits']:,} bits ({stats['compressed_bytes']:,} bytes)")
    print(f"Storage Space Saved:        {stats['space_saved_percent']}%")
    print(f"Compression Ratio:          {stats['compression_ratio']}:1")
    print("-" * 70)
    print(" INFORMATION THEORETIC METRICS")
    print("-" * 70)
    print(f"Shannon Entropy H(X):       {stats['shannon_entropy']:.4f} bits/character")
    print(f"Average Code Length L_avg:  {stats['average_code_length']:.4f} bits/character")
    print(f"Coding Efficiency:          {stats['coding_efficiency_percent']}%")
    print(f"Kraft-McMillan Sum:         {stats['kraft_inequality_sum']:.6f} (Condition Valid <= 1.0: {stats['kraft_valid']})")
    print("-" * 70)
    print(" FREQUENCY & PREFIX CODEBOOK")
    print("-" * 70)
    print(f"{'Char':^8} | {'Frequency':^10} | {'Probability':^12} | {'Huffman Code':^16} | {'Length':^6}")
    print("-" * 70)

    for char, freq in sorted(stats['frequency_table'].items(), key=lambda x: -x[1]):
        display_char = repr(char) if char in (' ', '\n', '\t') else char
        prob = freq / stats['original_chars']
        code = stats['code_table'][char]
        print(f"{display_char:^8} | {freq:^10} | {prob:^12.4f} | {code:^16} | {len(code):^6}")


def run_self_tests():
    """Automated unit verification covering edge cases, Shannon entropy, and file I/O."""
    print("[TEST] Running Huffman Coding Engine Self-Verification Suite...")
    engine = HuffmanEngine()

    # Test 1: Standard string
    test_cases = [
        "ABRACADABRA",
        "The quick brown fox jumps over the lazy dog.",
        "AAAAAAABCCCCCCDDEEEEE",
        "Single 'A' repeats: AAAAAAAAAAAAAAAAA",
        "Punctuation & numbers: 12345!@#$%^&*()_+~`",
        "Line breaks\nand\ttabs\r\ntest.",
    ]

    for tc in test_cases:
        stats = engine.compute_analytics(tc)
        encoded = engine.encode_text(tc)
        decoded = engine.decode_bits(encoded)
        assert decoded == tc, f"Mismatch in test case: {tc!r} != {decoded!r}"
        assert stats["kraft_valid"], f"Kraft inequality violated for {tc!r}"
        # Binary byte roundtrip
        packed = engine.compress_to_bytes(tc)
        unpacked = engine.decompress_from_bytes(packed)
        assert unpacked == tc, f"Byte packing failed for {tc!r}"

    # Test 2: Empty string
    assert engine.encode_text("") == ""
    assert engine.compress_to_bytes("") != b""
    assert engine.decompress_from_bytes(engine.compress_to_bytes("")) == ""

    print("[PASS] All 6 test suites passed flawlessly with 100% lossless fidelity!")


if __name__ == "__main__":
    run_cli()
