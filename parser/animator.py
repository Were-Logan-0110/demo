import matplotlib.pyplot as plt
import numpy as np


def visualizeVectors(*vectors):
    plt.style.use("dark_background")
    fig, ax = plt.subplots()

    # Setting up the axis limits and grid
    allX = [v[0] for v in vectors]
    allY = [v[1] for v in vectors]
    maxX = max(allX) if allX else 1
    minX = min(allX) if allX else -1
    maxY = max(allY) if allY else 1
    minY = min(allY) if allY else -1

    ax.set_xlim(minX - 2, maxX + 2)
    ax.set_ylim(minY - 2, maxY + 2)
    ax.set_aspect("equal")
    ax.grid(True, which="both", color="gray", linestyle="--", linewidth=0.5)

    ax.axhline(y=0, color="white", linewidth=1)
    ax.axvline(x=0, color="white", linewidth=1)

    for vector in vectors:
        originalPoint = [0, 0]
        scaledPoint = vector
        ax.plot(
            scaledPoint[0],
            scaledPoint[1],
            "o",
            label=f"Vector ({scaledPoint[0]}, {scaledPoint[1]})",
        )
        ax.plot(
            [originalPoint[0], scaledPoint[0]],
            [originalPoint[1], scaledPoint[1]],
            linestyle="-",
            linewidth=2,
        )

    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.legend(loc="upper right")

    plt.show()
