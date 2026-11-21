"""Same data stored by rows and by columns, using only the Python standard library.
Run:  python3 demo.py
The page shows the numbers from one run (N = 200,000). Text columns and zlib are a crude stand-in for Parquet."""
import random
import time
import zlib


def run(n=200_000, seed=7):
    random.seed(seed)
    regions, channels = ["North", "South", "East", "West"], ["web", "app", "store"]
    rows = [(i, random.choice(regions), random.choice(channels), random.randint(1, 500), round(random.uniform(5, 900), 2)) for i in range(n)]
    row_bytes = "\n".join(",".join(map(str, r)) for r in rows).encode()          # row layout: one line per row
    col_bytes = ["\n".join(map(str, c)).encode() for c in zip(*rows)]            # column layout: one block per column
    names = ["id", "region", "channel", "qty", "amount"]
    out = {"raw_row": len(row_bytes), "raw_col": sum(map(len, col_bytes))}
    out["zlib_row"] = len(zlib.compress(row_bytes, 6))
    out["zlib_col_each"] = {nm: len(zlib.compress(b, 6)) for nm, b in zip(names, col_bytes)}
    out["zlib_col"] = sum(out["zlib_col_each"].values())
    # query: SUM(amount) GROUP BY region
    t = time.perf_counter()
    tot = {}
    for line in row_bytes.decode().split("\n"):
        f = line.split(",")
        tot[f[1]] = tot.get(f[1], 0) + float(f[4])
    out["t_row"] = time.perf_counter() - t
    t = time.perf_counter()
    tot2 = {}
    for r, a in zip(col_bytes[1].decode().split("\n"), col_bytes[4].decode().split("\n")):
        tot2[r] = tot2.get(r, 0) + float(a)
    out["t_col"] = time.perf_counter() - t
    out["same_answer"] = all(abs(tot[k] - tot2[k]) < 1e-6 for k in tot)
    out["bytes_read_row"] = len(row_bytes)
    out["bytes_read_col"] = len(col_bytes[1]) + len(col_bytes[4])
    return out


if __name__ == "__main__":
    print(run())
