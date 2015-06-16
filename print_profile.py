import pstats
import sys

# cumulative tottime time

p = pstats.Stats(sys.argv[1])
p.strip_dirs().sort_stats('time').print_stats(30)
