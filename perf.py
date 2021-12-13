import pstats
p = pstats.Stats('profile.txt')
p.strip_dirs().sort_stats('tottime').print_stats(25)

p.sort_stats('ncalls').print_callers('<listcomp>')