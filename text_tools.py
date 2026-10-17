"""Regex sanitization, stable-sequence, and incident-index functions."""

def longest_stable_sequence(events):
    start = 0
    last_seen = {}
    best_start = 0
    best_length = 0

    for i, event in enumerate(events):
        if event in last_seen and last_seen[event] >= start:
            start = last_seen[event] + 1

        last_seen[event] = i 

        length = i - start + 1
        if length > best_length:
            best_start = start
            best_length =  length

    return events[best_start:best_start + best_length]

