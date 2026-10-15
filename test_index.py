"""Small automated correctness checks for the data structures."""
import io
from index import (
    get_words, TrieNode, trie_insert, trie_search, trie_print,
    bst_insert, bst_search, bst_print, dict_insert, dict_search, dict_print
)


def line_numbers(lines):
    values = []
    node = lines.head if lines else None
    while node:
        values.append(node.line)
        node = node.next
    return values


def main():
    sample = [("apple", 1), ("apple", 1), ("banana", 1),
              ("apple", 2), ("zebra", 3)]
    trie = TrieNode()
    bst = None
    dictionary = {}
    for word, line in sample:
        trie_insert(trie, word, line)
        bst = bst_insert(bst, word, line)
        dict_insert(dictionary, word, line)

    for search in (trie_search(trie, "apple"),
                   bst_search(bst, "apple"),
                   dict_search(dictionary, "apple")):
        assert line_numbers(search) == [1, 2]
    assert trie_search(trie, "missing") is None
    assert bst_search(bst, "missing") is None
    assert dict_search(dictionary, "missing") is None

    for printer, structure in ((trie_print, trie), (bst_print, bst),
                               (dict_print, dictionary)):
        output = io.StringIO()
        printer(structure, output)
        lines = [line.split("\t", 1)[0] for line in output.getvalue().splitlines()]
        assert lines == sorted(lines), (printer.__name__, lines)

    print("All data-structure tests passed.")


if __name__ == "__main__":
    main()
