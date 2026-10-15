"""Benchmark all six project datasets, create index outputs and combined plots."""
import csv
import os
import random
import time
import matplotlib.pyplot as plt

from index import (
    get_words, TrieNode, trie_insert, trie_search, trie_print,
    bst_insert, bst_search, bst_print, dict_insert, dict_search, dict_print,
    write_index,
)

DATASETS = [
    ("input1.txt", 1_000),
    ("input2.txt", 5_000),
    ("input3.txt", 10_000),
    ("input4.txt", 50_000),
    ("input5.txt", 100_000),
    ("input6.txt", 500_000),
]
DATA_DIR = "datasets"
OUTPUT_DIR = "outputs"
SEARCH_COUNT = 100_000


def benchmark_structure(name, words, search_words):
    start = time.perf_counter()
    if name == "Trie":
        structure = TrieNode()
        for word, line in words:
            trie_insert(structure, word, line)
        search_fn, print_fn = trie_search, trie_print
    elif name == "BST":
        structure = None
        for word, line in words:
            structure = bst_insert(structure, word, line)
        search_fn, print_fn = bst_search, bst_print
    else:
        structure = {}
        for word, line in words:
            dict_insert(structure, word, line)
        search_fn, print_fn = dict_search, dict_print
    construction = time.perf_counter() - start

    start = time.perf_counter()
    for word in search_words:
        search_fn(structure, word)
    searching = time.perf_counter() - start
    return structure, print_fn, (construction, searching)


def save_graph(rows, action_index, title, filename):
    plt.figure(figsize=(10, 6))
    for name in ("Trie", "BST", "Dictionary"):
        subset = [row for row in rows if row["structure"] == name]
        plt.plot([row["distinct_words"] for row in subset],
                 [row[("construction", "search", "printing")[action_index]] for row in subset],
                 marker="o", label=name)
    plt.xscale("log")
    plt.xlabel("Number of distinct words (log scale)")
    plt.ylabel("Time in seconds")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    rows = []
    for filename, expected_distinct in DATASETS:
        path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(path):
            print(f"Missing {path}. Run python generate_datasets.py first.")
            return 1
        print(f"\nReading {path} ...")
        words = get_words(path)
        unique_words = sorted({word for word, line in words})
        if len(words) <= 1_000_000:
            print(f"WARNING: {filename} has only {len(words):,} words.")
        if len(unique_words) != expected_distinct:
            print(f"WARNING: expected {expected_distinct:,} distinct words, found {len(unique_words):,}.")
        random.seed(1)
        queries = random.choices(unique_words, k=SEARCH_COUNT) if unique_words else []
        output_path = os.path.join(OUTPUT_DIR, filename.replace(".txt", "_indexes.txt"))
        with open(output_path, "w", encoding="utf-8", newline="") as output:
            for name in ("Trie", "BST", "Dictionary"):
                print(f"  Benchmarking {name} ...")
                structure, print_fn, (construction, searching) = benchmark_structure(name, words, queries)
                start = time.perf_counter()
                write_index(output, name.upper() + " INDEX", print_fn, structure)
                output.write("\n")
                printing = time.perf_counter() - start
                rows.append({
                    "dataset": filename,
                    "distinct_words": expected_distinct,
                    "total_words": len(words),
                    "structure": name,
                    "construction": construction,
                    "search": searching,
                    "printing": printing,
                })
                del structure
        print(f"  Index output: {output_path}")

    csv_path = os.path.join(OUTPUT_DIR, "benchmark_results.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        fields = ["dataset", "distinct_words", "total_words", "structure",
                  "construction", "search", "printing"]
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    save_graph(rows, 0, "Construction Time vs Distinct Words", os.path.join(OUTPUT_DIR, "construction.png"))
    save_graph(rows, 1, "Search Time (100,000 queries) vs Distinct Words", os.path.join(OUTPUT_DIR, "search.png"))
    save_graph(rows, 2, "Printing Time vs Distinct Words", os.path.join(OUTPUT_DIR, "printing.png"))
    print("\nFinished. Results and graphs are in the outputs folder.")
    print("Note: runtimes depend on your computer; BST can be slow on sorted/adversarial data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
