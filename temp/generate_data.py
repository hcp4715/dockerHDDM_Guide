import numpy as np

def generate_data(seed=7, n=100):
    gen = np.random.default_rng(seed)
    age = gen.integers(1, 20, size=n)
    rt_comp = 1 * np.exp(-2 * age) + .1 + np.random.normal(size=n)
    rt_incomp = .5 * np.exp(-2 * age) + .5 + np.random.normal(size=n)
    return age, rt_comp, rt_incomp
