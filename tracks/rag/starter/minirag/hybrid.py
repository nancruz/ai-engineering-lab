"""Reciprocal rank fusion: merge rankings from different retrievers. (Lab 6.)

BM25 scores and cosine similarities live on different scales, so adding them is
meaningless. RRF uses only positions:

    rrf(d) = sum over rankings r that contain d of  1 / (c + rank_r(d))      (rank starts at 1)

c (60 by default) dampens the advantage of the very top positions.
"""


def rrf(rankings, c=60):
    """Fuse ranked lists of ids. Returns [(id, score), ...] best first, ties by id.

    Within one ranking, only the first occurrence of an id counts.
    """
    if c < 0:
        raise ValueError("c must be >= 0")
    # TODO (Lab 6): Accumulate 1 / (c + rank) per id across rankings (skip repeated ids within
    #       a ranking), then sort by (-score, id).
    raise NotImplementedError("Lab 6: write rrf() in minirag/hybrid.py")
