"""Modul hitungan SAW (Simple Additive Weighting), murni tanpa database dan tanpa web.

Input:
- matrix: list baris, tiap baris list nilai C1..C5 untuk satu paket.
- weights: list bobot, total harus 1,00.
- types: list 'Cost' atau 'Benefit' per kriteria.

Output: dict dengan matriks ternormalisasi, nilai Vi, ranking, dan urutan paket.
Ranking 1 = Vi tertinggi. Tidak ada nilai yang diubah diam-diam di modul ini.
"""

import math


def normalize(matrix, types):
    if not matrix:
        return []
    n_col = len(matrix[0])
    maxs = [max(row[j] for row in matrix) for j in range(n_col)]
    mins = [min(row[j] for row in matrix) for j in range(n_col)]
    out = []
    for row in matrix:
        norm = []
        for j, x in enumerate(row):
            if types[j] == "Cost":
                norm.append(mins[j] / x if x != 0 else 0.0)
            else:
                norm.append(x / maxs[j] if maxs[j] != 0 else 0.0)
        out.append(norm)
    return out


def calculate(matrix, weights, types):
    normalized = normalize(matrix, types)
    values = []
    for norm in normalized:
        values.append(sum(n * w for n, w in zip(norm, weights)))
    # Ranking kompetisi, sama dengan fungsi RANK di Excel: nilai yang sama
    # mendapat peringkat yang sama, dan peringkat berikutnya dilewati.
    # Urutan tampil tetap deterministik: nilai tertinggi dulu, lalu nomor urut paket.
    order = sorted(range(len(values)), key=lambda i: (-values[i], i))
    ranks = [1 + sum(1 for v in values if v > values[i]) for i in range(len(values))]
    return {
        "normalized": normalized,
        "values": values,
        "ranks": ranks,
        "order": order,
    }
