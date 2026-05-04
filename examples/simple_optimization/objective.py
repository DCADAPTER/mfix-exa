from __future__ import annotations

import argparse


def objective(x: float) -> float:
    # Convex toy objective. Global optimum at x=3.0 where f(x)=0.
    return (x - 3.0) ** 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--x", type=float, required=True)
    args = parser.parse_args()

    y = objective(args.x)
    print(f"x={args.x:.6f}")
    print(f"objective={y:.6f}")
