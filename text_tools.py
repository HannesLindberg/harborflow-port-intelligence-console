"""Regex sanitization, stable-sequence, and incident-index functions."""

import re


    #for task 7
def longest_stable_sequence(events):
    #Finds the longest run of consecutive events with no repeated code, using a sliding window.
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


#for task 9
def normalize_text(text):
    #owercases the text and extracts words with re.findall(r'[a-z0-9]+', ...).
    text = text.lower()
    words = re.findall(r'[a-z0-9]+', text)
    return words


#for task 9
def build_index(incidents):
    #builds an inverted index (word → sorted incident IDs, no duplicates) and a titles lookup (ID → title).
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



#for task 9
def search_incidents(query, index, titles):
#scores each incident by the number of distinct query words it contains.
# Results are sorted by score (descending) and then by ID.
    scores = {}
    words = set(normalize_text(query))
    for word in words:
        if word in index:
            for incident_id in index[word]:
                scores[incident_id] = scores.get(incident_id, 0) + 1
    pairs = list(scores.items())
    pairs.sort(key=lambda pair: (-pair[1], pair[0]))
    results = []
    for incident_id, score, in pairs:
        results.append((incident_id, score, titles[incident_id]))
    return results


