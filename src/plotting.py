import math

def sine_graph(t):
    return math.sin(2 * math.pi * t)

def cos_graph(t):
    return math.cos(2 * math.pi * t)

def tan_graph(t):
    return math.tan(2 * math.pi * t)

def cosec_graph(t):
    return 1 / math.sin(2 * math.pi * t)

def sec_graph(t):
    return 1 / math.cos(2 * math.pi * t)

def cot_graph(t):
    return 1 / math.tan(2 * math.pi * t)

def triangle_graph(t):

    return 2 * abs(2 * (t % 1) - 1) - 1

def square_graph(t):

    return 1 if (t % 1) < 0.5 else -1
