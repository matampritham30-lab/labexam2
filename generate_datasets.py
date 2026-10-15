"""Generate the six large synthetic input files required by the project.

Each generated file has more than 1,000,000 word occurrences and exactly
the requested number of distinct words. Run: python generate_datasets.py
"""
import os
import random

DATASETS = [
    ("input1.txt", 1_000),
    ("input2.txt", 5_000),
    ("input3.txt", 10_000),
    ("input4.txt", 50_000),
    ("input5.txt", 100_000),
    ("input6.txt", 500_000),
]
TOTAL_WORDS = 1_100_000
WORDS_PER_LINE = 100
OUTPUT_DIR = "datasets"


def make_word(number):
    # Prefix and fixed-width digits make each token unique and ASCII-sortable.
    return f"word{number:06d}"


def generate_file(path, distinct_count):
    unique = [make_word(i) for i in range(distinct_count)]
    rng = random.Random(1000 + distinct_count)
    # Include every distinct word at least once, then add repeats until
    # the file contains TOTAL_WORDS occurrences.
    tokens = unique[:]
    tokens.extend(rng.choices(unique, k=TOTAL_WORDS - len(tokens)))
    rng.shuffle(tokens)
    with open(path, "w", encoding="ascii", newline="\n") as output:
        for start in range(0, len(tokens), WORDS_PER_LINE):
            output.write(" ".join(tokens[start:start + WORDS_PER_LINE]) + "\n")
    print(f"Created {path}: {len(tokens):,} words, {distinct_count:,} distinct words")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for filename, count in DATASETS:
        generate_file(os.path.join(OUTPUT_DIR, filename), count)
    print("\nAll six datasets are ready in the datasets folder.")


if __name__ == "__main__":
    main()
