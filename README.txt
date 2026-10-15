INDEX GENERATION PROJECT — FINAL PACKAGE

Files:
- index.py: single-input implementation of Trie, BST, and dictionary indexes.
- generate_datasets.py: creates six large synthetic datasets with the required distinct-word counts.
- benchmark_all.py: benchmarks all six datasets, writes indexes, a CSV timing report, and three graphs.
- design.txt: brief design explanation.
- test_cases.txt: test plan and expected behavior.
- test_input.txt: small example input.

Setup:
    python -m pip install matplotlib

Create datasets:
    python generate_datasets.py

Run the full benchmark:
    python benchmark_all.py

Run one file:
    python index.py test_input.txt test_output.txt


Important:
The six large datasets are generated locally rather than included in this ZIP, keeping the submission package small. Run the generator before benchmarking. Six large files can require significant disk space and memory. Benchmark timings are machine-dependent. For your report, run the benchmark on your own computer and use the measured results; do not invent or manually estimate timings.
