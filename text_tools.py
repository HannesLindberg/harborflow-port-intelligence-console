"""Regex sanitization, stable-sequence, and incident-index functions."""

import re


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



def normalize_text(text):
    text = text.lower()
    words = re.findall(r'[a-z0-9]+', text)
    return words



def build_index(incidents):
    """incidents: list of dicts with incident_id, title, report.
    Return (index, titles)."""
    index = {}
    titles = {}
    for incident in incidents:
        incident_id = incident["incident_id"]
        titles[incident_id] = incident["title"]
        words = normalize_text(incident["report"])
        for word in set(words):
            if word not in index:
                index[word] = []
            index[word].append(incident_id)
    return index, titles


