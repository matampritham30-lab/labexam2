import sys
import time
import random
import re
import matplotlib.pyplot as plt


class LineNode:
    """A linked-list node containing one line number."""
    def __init__(self, line):
        self.line = line
        self.next = None


class Lines:
    """Keep unique line numbers in the order they are encountered."""
    def __init__(self, line):
        self.head = LineNode(line)
        self.tail = self.head

    def add(self, line):
        # Input is scanned from top to bottom, so duplicate line numbers
        # for a word can only be equal to the last stored line number.
        if self.tail.line != line:
            self.tail.next = LineNode(line)
            self.tail = self.tail.next


def get_words(filename):
    """Return (word, line_number) pairs using the project's separators."""
    words = []
    with open(filename, "r", encoding="utf-8") as file:
        for line_no, line in enumerate(file, 1):
            # Only blanks, tabs, line breaks, full stops, commas,
            # colons and semicolons are separators.
            for word in re.split(r"[ \t\r\n.,:;]+", line):
                if word:
                    words.append((word, line_no))
    return words


class TrieNode:
    def __init__(self):
        self.child = {}
        self.lines = None


def trie_insert(root, word, line):
    node = root
    for char in word:
        if char not in node.child:
            node.child[char] = TrieNode()
        node = node.child[char]
    if node.lines is None:
        node.lines = Lines(line)
    else:
        node.lines.add(line)


def trie_search(root, word):
    node = root
    for char in word:
        if char not in node.child:
            return None
        node = node.child[char]
    return node.lines


def trie_print(root, output):
    """Iterative depth-first traversal in ascending ASCII order."""
    stack = [(root, "")]
    while stack:
        node, word = stack.pop()
        if node.lines is not None:
            output.write(word + "\t")
            current = node.lines.head
            while current:
                output.write(str(current.line) + " ")
                current = current.next
            output.write("\n")
        for char in sorted(node.child, reverse=True):
            stack.append((node.child[char], word + char))


class BSTNode:
    def __init__(self, word, line):
        self.word = word
        self.lines = Lines(line)
        self.left = None
        self.right = None


def bst_insert(root, word, line):
    if root is None:
        return BSTNode(word, line)
    node = root
    while True:
        if word == node.word:
            node.lines.add(line)
            break
        elif word < node.word:
            if node.left is None:
                node.left = BSTNode(word, line)
                break
            node = node.left
        else:
            if node.right is None:
                node.right = BSTNode(word, line)
                break
            node = node.right
    return root


def bst_search(root, word):
    node = root
    while node is not None:
        if word == node.word:
            return node.lines
        if word < node.word:
            node = node.left
        else:
            node = node.right
    return None


def bst_print(root, output):
    """Iterative in-order traversal prints words in sorted order."""
    stack = []
    node = root
    while stack or node:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        output.write(node.word + "\t")
        current = node.lines.head
        while current:
            output.write(str(current.line) + " ")
            current = current.next
        output.write("\n")
        node = node.right


def dict_insert(index, word, line):
    if word in index:
        index[word].add(line)
    else:
        index[word] = Lines(line)


def dict_search(index, word):
    return index.get(word)


def dict_print(index, output):
    for word in sorted(index):
        output.write(word + "\t")
        current = index[word].head
        while current:
            output.write(str(current.line) + " ")
            current = current.next
        output.write("\n")


def write_index(output, heading, print_function, structure):
    output.write(heading + "\n")
    print_function(structure, output)


def build_structures(words):
    """Build all three indexes and return each structure with its functions."""
    trie = TrieNode()
    bst = None
    dictionary = {}
    for word, line in words:
        trie_insert(trie, word, line)
        bst = bst_insert(bst, word, line)
        dict_insert(dictionary, word, line)
    return [
        ("Trie", trie, trie_search, trie_print),
        ("BST", bst, bst_search, bst_print),
        ("Dictionary", dictionary, dict_search, dict_print),
    ]


def run_one(input_file, output_file):
    try:
        words = get_words(input_file)
    except (OSError, UnicodeError) as error:
        print("Could not read input file:", error)
        return 1

    unique_words = sorted({word for word, line in words})
    random.seed(1)
    # Exactly 100,000 queries; repeats are allowed by the specification.
    search_words = random.choices(unique_words, k=100000) if unique_words else []

    results = {}
    with open(output_file, "w", encoding="utf-8", newline="") as output:
        for name in ("Trie", "BST", "Dictionary"):
            # Construction timing is measured separately for each structure.
            start = time.perf_counter()
            if name == "Trie":
                structure = TrieNode()
                for word, line in words:
                    trie_insert(structure, word, line)
                search_function, print_function = trie_search, trie_print
            elif name == "BST":
                structure = None
                for word, line in words:
                    structure = bst_insert(structure, word, line)
                search_function, print_function = bst_search, bst_print
            else:
                structure = {}
                for word, line in words:
                    dict_insert(structure, word, line)
                search_function, print_function = dict_search, dict_print
            build_time = time.perf_counter() - start

            start = time.perf_counter()
            for word in search_words:
                search_function(structure, word)
            search_time = time.perf_counter() - start

            start = time.perf_counter()
            write_index(output, name.upper() + " INDEX", print_function, structure)
            output.write("\n")
            print_time = time.perf_counter() - start
            results[name] = (build_time, search_time, print_time)

    print("\nPerformance Comparison")
    print("----------------------")
    for name, timings in results.items():
        print(name)
        print(f"Construction: {timings[0]:.6f} seconds")
        print(f"Search:       {timings[1]:.6f} seconds")
        print(f"Printing:     {timings[2]:.6f} seconds")
    make_graph(results, "performance.png")
    print(f"\nIndex saved to {output_file}")
    print("Performance graph saved as performance.png")
    return 0


def make_graph(results, filename):
    names = list(results)
    positions = list(range(len(names)))
    plt.figure(figsize=(8, 5))
    for column, label in enumerate(("Construction", "Search", "Printing")):
        plt.plot(positions, [results[name][column] for name in names],
                 marker="o", label=label)
    plt.xticks(positions, names)
    plt.xlabel("Data Structure")
    plt.ylabel("Time in seconds")
    plt.title("Index Generation Performance")
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


def main():
    if len(sys.argv) != 3:
        print("Usage: python index.py input.txt output.txt")
        return 1
    return run_one(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    sys.exit(main())
