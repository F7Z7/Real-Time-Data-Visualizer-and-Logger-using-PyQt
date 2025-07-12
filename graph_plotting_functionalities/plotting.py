import numpy as np

safe_val = 1e-5  # very small value to approx zero


def safe_div(num, denom):
    return np.divide(num, denom, out=np.full_like(num, np.nan, dtype=float), where=np.abs(denom) > safe_val)


def random_mixed_signal(t, duration_secs=3600):
    t = np.atleast_1d(t)
    # 1 Hz base sine wave
    base = np.sin(2 * np.pi * 1 * t)

    # Add high-frequency noise
    noise = 0.2 * np.random.randn(len(t))

    # Create random spikes
    spikes = np.zeros_like(t)
    spike_indices = np.random.choice(len(t), size=int(len(t) * 0.002), replace=False)
    spikes[spike_indices] = np.random.uniform(2, 5, size=spike_indices.shape[0]) * np.random.choice([-1, 1], size=
    spike_indices.shape[0])

    return base + noise + spikes


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


Signal_list = {
    "random_mixed": random_mixed_signal,
    "sine": sine_graph,
    "cos": cos_graph,
    "tan": tan_graph,
    "cosec": cosec_graph,
    "sec": sec_graph,
    "cot": cot_graph,
    "triangle": triangle_graph,
    "square": square_graph
}
