# 🎓 DAA Viva Quick-Fire Cheatsheet: Huffman Coding

**Course:** Design and Analysis of Algorithms (DAA)  
**Topic:** Text File Compression & Variable-Length Prefix Codes  
**Exam Prep:** 8 High-Scoring Faculty Viva Questions & Crisp Technical Answers  

---

### Q1: Break down the exact time complexity of the Huffman algorithm. Why is it expressed as $O(N + k \log k)$?
**Crisp Faculty Answer:**
* Let $N$ be the total length of the input text and $k$ be the number of unique characters in the alphabet ($k = |\Sigma|$).
* **Step 1 (Frequency Tally):** Scanning the text of length $N$ to count frequencies takes $\mathbf{O(N)}$ time using a hash map or direct array lookup.
* **Step 2 (Heap Initialization):** Inserting all $k$ unique characters into a binary Min-Heap takes $\mathbf{O(k)}$ time using Floyd’s linear-time `heapify` (bottom-up sift-down).
* **Step 3 (Greedy Tree Merging):** A tree with $k$ leaves requires exactly $k-1$ internal node merges. Each merge performs two `extract-min` operations ($2 \times O(\log k)$) and one `insert` operation ($O(\log k)$). Total cost: $(k-1) \times 3 \log k = \mathbf{O(k \log k)}$.
* **Step 4 (Codebook Traversal):** A Depth-First Search (DFS) over the binary tree of $2k-1$ nodes takes $\mathbf{O(k)}$ time.
* **Step 5 (Bitstream Encoding / Decoding):** Looking up and writing bits for $N$ characters takes $\mathbf{O(N)}$ time; decoding walks $B$ bits where $B \le 8N$, which is strictly $\mathbf{O(N)}$.
* **Sum Total:** $\mathbf{O(N + k \log k)}$ time and $\mathbf{O(N + k)}$ space.
* *Viva Punchline:* For ASCII or byte streams, $k \le 256$ is a small constant, meaning $k \log k \le 2048$ operations; thus, the real-world execution runtime is strictly **linear in text size $O(N)$**.

---

### Q2: Why is a Priority Queue (Min-Heap) strictly preferred over an unsorted array or a balanced Binary Search Tree (AVL/Red-Black)?
**Crisp Faculty Answer:**
* **Unsorted Array:** Finding the two minimum-frequency nodes requires scanning all remaining elements, taking $O(k)$ per step. Over $k-1$ iterations, total time is $\sum_{i=1}^{k} O(i) = \mathbf{O(k^2)}$.
* **Sorted Array:** Initial sorting takes $O(k \log k)$. However, inserting the merged parent back into the array takes $O(k)$ due to linear element shifting, yielding $(k-1) \times O(k) = \mathbf{O(k^2)}$.
* **Balanced BST (AVL / Red-Black Tree):** Finding the minimum and re-inserting takes $O(\log k)$ per step, matching the Min-Heap’s $O(k \log k)$ total time. However, a balanced BST requires 3 pointers per node (left, right, parent), balancing flags/height values, and rotational rebalancing overhead.
* **Binary Min-Heap:** A binary heap stores elements in a compact continuous array with zero pointer overhead, exhibits superior cache locality, supports $O(k)$ initialization via `heapify`, and achieves optimal $O(\log k)$ extract-min and insert operations.

---

### Q3: What happens to the Huffman tree structure and depth if character frequencies follow the Fibonacci sequence ($1, 1, 2, 3, 5, 8, \dots$)?
**Crisp Faculty Answer:**
* If symbol frequencies follow Fibonacci numbers, the algorithm produces the **maximally skewed (degenerate) tree**, which is the theoretical worst-case tree structure.
* **Mathematical Intuition:**
  - Let frequencies be $F_1, F_2, F_3, \dots, F_k$.
  - At Step 1: Pop $F_1 = 1$ and $F_2 = 1$. The merged parent is $1 + 1 = 2 = F_3$.
  - At Step 2: The minimum elements are now the new parent ($2$) and the next Fibonacci symbol $F_3 = 2$. Merged parent = $2 + 2 = 4 \approx F_4$.
  - By the Fibonacci recurrence $F_n = F_{n-1} + F_{n-2}$, at every subsequent step the newly merged subtree sum combined with the next leaf always forms the smallest pair.
* **Consequences:**
  - The resulting tree degenerates into a **linear linked chain (caterpillar tree)**.
  - Tree depth reaches the theoretical maximum: $\mathbf{\text{Depth} = k - 1}$.
  - The longest codeword reaches $\mathbf{k - 1}$ bits.
  - Codeword lengths are $1, 2, 3, \dots, k-1$ bits.

---

### Q4: Why can Huffman coding cause negative compression (file expansion) on tiny files? How does tree header overhead factor into this?
**Crisp Faculty Answer:**
* Huffman coding is a **two-component transmission system**: the compressed file must store both the **compressed bitstream** AND the **decoding metadata** (either the character frequency table or the serialized tree topology) so that the decompressor can reconstruct the codebook.
* **The Header Overhead:** Storing $k$ unique characters with their frequency counts requires approximately $k \times (1 \text{ to } 4) \text{ bytes} \approx 50 \text{ to } 300 \text{ bytes}$.
* **The Threshold Effect:**
  - If the input file is only 50 bytes, saving 30% of ASCII bits yields a 15-byte saving.
  - However, prepending a 100-byte header results in a 135-byte compressed file—an expansion of **+170%**!
* **Asymptotic Amortization:**
  - Header overhead is strictly $O(k)$ (independent of $N$).
  - Compressed data size is $O(N)$.
  - As file length $N \gg k$ (e.g., files $> 5 \text{ KB}$), the fixed header overhead becomes negligible ($< 0.1\%$).

---

### Q5: Explain the Kraft-McMillan Inequality and why prefix-free codes do not require delimiter characters.
**Crisp Faculty Answer:**
* **Kraft-McMillan Inequality:** For any uniquely decodable binary prefix code with codeword lengths $l_1, l_2, \dots, l_k$:
  $$\sum_{i=1}^{k} 2^{-l_i} \le 1$$
* **Why Delimiters are Obsolete:**
  - In a standard code like Morse code, 'E' is `.` and 'I' is `..`. Without an audible pause (delimiter), the stream `..` could be interpreted as 'EE' or 'I'.
  - In a Huffman prefix tree, every valid symbol is located **strictly at a leaf node**. No character sits at an internal node.
  - Therefore, no codeword can be the prefix of another ($c_i \neq \text{prefix}(c_j)$).
  - The decoder reads bit-by-bit from the root. The instant a leaf node is reached, that symbol is uniquely and unequivocally identified. The decoder outputs the character and immediately resets to the root for the next bit without needing any separator tokens.

---

### Q6: How does Huffman Coding relate to Shannon’s Source Coding Theorem? What is Coding Redundancy?
**Crisp Faculty Answer:**
* **Shannon's Source Coding Theorem (1948)** proves that the absolute theoretical limit of lossless compression for an information source $X$ is governed by its **Shannon Entropy**:
  $$H(X) = -\sum_{i=1}^{k} P(x_i) \log_2 P(x_i) \quad (\text{measured in bits/character})$$
* **Huffman's Optimality:**
  - David Huffman proved that his code achieves the lowest average length $L_{\text{avg}} = \sum P(x_i) l_i$ among all symbol-by-symbol prefix codes.
  - Expected length is bounded within 1 bit of entropy:
    $$H(X) \le L_{\text{avg}} < H(X) + 1$$
* **Coding Redundancy ($R$):**
  $$R = L_{\text{avg}} - H(X) \ge 0$$
  Redundancy occurs because Huffman assigns an integral number of bits (at least 1 bit) to each character, whereas the true information content $-\log_2 P(x_i)$ may be fractional.

---

### Q7: What is the fundamental difference between Static Huffman Coding and Adaptive (Dynamic) Huffman Coding?
**Crisp Faculty Answer:**
* **Static Huffman Coding (Our Implementation):**
  - Requires **two passes** over the data: Pass 1 counts global frequencies to build the tree; Pass 2 encodes the text.
  - The tree structure remains static throughout the entire stream.
  - Must transmit the frequency table / tree header to the decoder.
* **Adaptive Huffman Coding (FGK / Vitter Algorithm):**
  - Operates in a **single pass** ($O(1)$ latency, ideal for real-time network streams).
  - Starts with an empty tree containing a special `NYT` (Not-Yet-Transmitted) escape token.
  - Dynamically updates tree weights and executes tree rotations (sibling property maintenance) after encoding/decoding each character.
  - **No header required:** The decoder updates its own identical tree synchronously from the incoming bitstream.

---

### Q8: How does Canonical Huffman Coding eliminate the need to transmit the tree structure in production formats like GZIP/PNG?
**Crisp Faculty Answer:**
* In standard Huffman coding, different tie-breaking choices produce different tree topologies, requiring the entire tree or frequency table to be transmitted.
* **Canonical Huffman Solution:**
  - Enforces two deterministic mathematical rules:
    1. Codewords of the same bit length are assigned in consecutive lexicographical order.
    2. Shorter codewords lexicographically precede longer codewords: $C(l+1) = (C(l) + 1) \ll 1$.
* **The Enormous Advantage:**
  - The encoder only needs to transmit a list of **bit lengths** for each alphabet symbol (e.g., `'A': 1, 'B': 3, 'C': 3`).
  - Both encoder and decoder compute the exact same binary codewords algebraically without ever storing or transmitting tree pointers.
  - This is the standard used in **DEFLATE (GZIP / ZIP)**, **PNG**, and **JPEG**.
