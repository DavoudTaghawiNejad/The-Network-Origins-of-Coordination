python -m cProfile -s cumtime -o %1 main.py
python print_profile %1
