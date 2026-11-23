"""Modul hitungan TOPSIS, murni tanpa database dan tanpa web.

Langkah, sama persis dengan Excel Langkah 3:
1. Normalisasi vektor: nilai / akar jumlah kuadrat kolom.
2. Matriks terbobot: normalisasi x bobot.
3. Solusi ideal positif: Benefit = maksimum, Cost = minimum.
   Solusi ideal negatif: sebaliknya.
4. Jarak D+ ke ideal positif dan D- ke ideal negatif (Euclidean).
5. Ci = D- / (D+ + D-). Ranking 1 = Ci tertinggi.
"""

import math


def normalize(matrix):
    if not matrix:
        return []
    n_col = len(matrix[0])
    den = [math.sqrt(sum(row[j] ** 2 for row in matrix)) for j in range(n_col)]
    out = []
    for row in matrix:
        out.append([x / den[j] if den[j] != 0 else 0.0 for j, x in enumerate(row)])
    return out


def calculate(matrix, weights, types):
    normalized = normalize(matrix)
    weighted = [[x * weights[j] for j, x in enumerate(row)] for row in normalized]
    n_col = len(matrix[0])
    ideal_pos = []
    ideal_neg = []
    for j in range(n_col):
        col = [row[j] for row in weighted]
        if types[j] == "Cost":
            ideal_pos.append(min(col))
            ideal_neg.append(max(col))
        else:
            ideal_pos.append(max(col))
            ideal_neg.append(min(col))
    distances_pos = []
    distances_neg = []
    values = []
    for row in weighted:
        dp = math.sqrt(sum((x - a) ** 2 for x, a in zip(row, ideal_pos)))
        dn = math.sqrt(sum((x - a) ** 2 for x, a in zip(row, ideal_neg)))
        distances_pos.append(dp)
        distances_neg.append(dn)
        values.append(dn / (dp + dn) if (dp + dn) != 0 else 0.0)
    # Ranking kompetisi, sama dengan fungsi RANK di Excel: nilai yang sama
    # mendapat peringkat yang sama, dan peringkat berikutnya dilewati.
    order = sorted(range(len(values)), key=lambda i: (-values[i], i))
    ranks = [1 + sum(1 for v in values if v > values[i]) for i in range(len(values))]
    return {
        "normalized": normalized,
        "weighted": weighted,
        "ideal_pos": ideal_pos,
        "ideal_neg": ideal_neg,
        "distances_pos": distances_pos,
        "distances_neg": distances_neg,
        "values": values,
        "ranks": ranks,
        "order": order,
    }
