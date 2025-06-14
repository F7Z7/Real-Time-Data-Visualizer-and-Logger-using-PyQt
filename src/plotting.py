import math

safe_val=1e-5 #very small value to approx zero

def safe_div(num,denom):
    if abs(denom) > safe_val:
        return num/denom
    else:
        return float('nan')
def sine_graph(t):
    return math.sin(2 * math.pi * t)

def cos_graph(t):
    return math.cos(2 * math.pi * t)

def tan_graph(t):
    return safe_div(math.sin(2 * math.pi * t), math.cos(2 * math.pi * t))

def cosec_graph(t):
    return safe_div(1, math.sin(2 * math.pi * t))

def sec_graph(t):
    return safe_div(1, math.cos(2 * math.pi * t))

def cot_graph(t):
    return safe_div(math.cos(2 * math.pi * t), math.sin(2 * math.pi * t))

def triangle_graph(t):

    return 2 * abs(2 * (t % 1) - 1) - 1

def square_graph(t):

    return 1 if (t % 1) < 0.5 else -1
