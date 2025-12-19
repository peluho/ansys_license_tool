import numpy as np
from prix_base import LICENSES

def compute_costs(licence_counts, mode: str, years: int = 8):
    initial, annual = [], []
    for name, qty in licence_counts.items():
        p = LICENSES[name]
        if mode == "purchase":
            initial.append(qty * p["paid-up"])
            annual.append(qty * p["TECS"])
        else:
            initial.append(0)
            annual.append(qty * p["lease"])
    total_i, total_a = sum(initial), sum(annual)
    return [total_i + total_a * yr for yr in range(years)]
