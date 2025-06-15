import numpy as np
from plotting import *

def get_signal_name(name):
    return {
         "Sin": sine_graph,
        "Cos": cos_graph,
        "Tan": tan_graph,
        "Cosec": cosec_graph,
        "Sec": sec_graph,
        "Cot": cot_graph,
        "Triangle": triangle_graph,
        "Square": square_graph
    }.get(name, None)
operation_map = {
    "A + B": lambda A, B: A + B,
    "A - B": lambda A, B: A - B,
    "A * B": lambda A, B: A * B,
    "A / B": lambda A, B: A / B,
    "sin(A)": lambda A, B: np.sin(A),
    "cos(B)": lambda A, B: np.cos(B),
    "sin(A) + 2*B": lambda A, B: np.sin(A) + 2 * B,
}
def compute_expression(t,inputA,inputB,operation,constants):
    signalA = get_signal_name(inputA)
    signalB = get_signal_name(inputB)

    A=signalA(t)
    B=signalB(t)

    operations=["+", "-", "*", "/", "sin", "cos", "A+B", "A*2", "sin(A) + 2*B"]
    if not operation in operations:
        print("Invalid operation")
    else:
        calculated_expression=operation_map.get(operation)