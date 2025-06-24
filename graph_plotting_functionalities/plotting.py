import numpy as np

safe_val=1e-5 #very small value to approx zero

def safe_div(num,denom):
    return np.divide(num, denom, out=np.full_like(num, np.nan,dtype=float), where=np.abs(denom) > safe_val)

def sine_graph(t):
    return np.sin(2 * np.pi * t)

def cos_graph(t):
    return np.cos(2 * np.pi * t)

def tan_graph(t):
    return safe_div(np.sin(2 * np.pi * t), np.cos(2 * np.pi * t))

def cosec_graph(t):
    return safe_div(1, np.sin(2 * np.pi * t))

def sec_graph(t):
    return safe_div(1, np.cos(2 * np.pi * t))

def cot_graph(t):
    return safe_div(np.cos(2 * np.pi * t), np.sin(2 * np.pi * t))

def triangle_graph(t):
    return 2 * np.abs(2 * (t % 1) - 1) - 1

def square_graph(t):
    return np.where((t % 1) < 0.5, 1, -1)