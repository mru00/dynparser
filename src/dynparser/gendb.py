
GEN_HERE = 0
GEN_INCLUDE = 1
GEN_STATIC_GLOBAL = 2
GEN_INITIALLY_MAIN = 3
GEN_MAIN_LOOP = 4

_positions = {}

def add_gen(pos, template):
    global _positions
    if pos not in _positions:
        _postions[pos] = []

    _positions[pos].append(template)

get_gen = lambda pos: _positions[pos]
