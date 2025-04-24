"""
fuzzy.py - Simple fuzzy matching for autocomplete (subsequence and Levenshtein distance)
"""


def levenshtein(s1, s2):
    """Compute Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def fuzzy_score(query, candidate):
    """Return a score (higher is better) for how well candidate matches query."""
    query = query.lower()
    candidate = candidate.lower()
    # Exact match is best
    if query == candidate:
        return 100
    # Substring match is very good
    if query in candidate:
        return 90
    # Levenshtein distance (normalized)
    dist = levenshtein(query, candidate)
    maxlen = max(len(query), len(candidate))
    if maxlen == 0:
        return 0
    # Score: 100 for perfect, 0 for totally different
    return int(100 * (1 - dist / maxlen))


def fuzzy_top_matches(query, candidates, limit=10, min_score=60):
    """
    Return up to 'limit' candidates sorted by fuzzy_score descending.
    Only include those with score >= min_score.
    """
    scored = [(cand, fuzzy_score(query, cand)) for cand in candidates]
    scored = [x for x in scored if x[1] >= min_score]
    scored.sort(key=lambda x: -x[1])
    return [x[0] for x in scored[:limit]]
