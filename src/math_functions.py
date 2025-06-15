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

def compute_expression(t,inputA,inputB,operation,constants):
    print("ji3")