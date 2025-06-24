from plotting.plotting import *

# Signal name to function mapping
def get_signal_name(name):
    signal_map = {
        "Sin": sine_graph,
        "Cos": cos_graph,
        "Tan": tan_graph,
        "Cosec": cosec_graph,
        "Sec": sec_graph,
        "Cot": cot_graph,
        "Triangle": triangle_graph,
        "Square": square_graph
    }
    return signal_map.get(name, None)

# Operation mapping with optional constant support
operation_map = {
    "A + B": lambda A, B, c: A + B,
    "A - B": lambda A, B, c: A - B,
    "A * B": lambda A, B, c: A * B,
    "A / B": lambda A, B, c: np.divide(A, B, out=np.zeros_like(A), where=B != 0),
    "sin(A)": lambda A, B, c: np.sin(A),
    "cos(B)": lambda A, B, c: np.cos(B),
    "sin(A) + 2*B": lambda A, B, c: np.sin(A) + 2 * B,
    "A + k": lambda A, B, c: A + c,
    "B * k": lambda A, B, c: B * c,
    "A ^ 2": lambda A, B, c: A ** 2,
    "A + B + k": lambda A, B, c: A + B + c
}

# Expression computation function
def compute_expression(t, inputA, inputB, operation, constant=1.0):
    signalA = get_signal_name(inputA)
    signalB = get_signal_name(inputB)

    if signalA is None or signalB is None:
        print("Invalid signal name(s):", inputA, inputB)
        return None

    A = signalA(t)
    B = signalB(t)

    if operation not in operation_map:
        print(f"Invalid operation: {operation}")
        return None

    try:
        result = operation_map[operation](A, B, constant)
        return t, result
    except Exception as e:
        print(f"Error computing expression: {e}")
        return None
