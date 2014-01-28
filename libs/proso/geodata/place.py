# -*- coding: utf-8 -*-

def empty_distance_matrix(places, place_type=None):
    dist = {}
    for i, row1 in places.iterrows():
        if place_type and place_type != row1['type']:
            continue
        dist[row1['id']] = {}
        for j, row2 in places.iterrows():
            if place_type and place_type != row2['type']:
                continue
            if row1['id'] == row2['id']:
                dist[row1['id']][row2['id']] = 0
            else:
                dist[row1['id']][row2['id']] = float('inf')
    return dist


def distance_matrix(places, placerelations, place_type=None):
    matrix = empty_distance_matrix(places, place_type)
    for i, row in placerelations.iterrows():
        if row['type'] != 3:
            continue
        for j in row['related_places']:
            try:
                matrix[row['place']][j] = 1
                matrix[j][row['place']] = 1
            except KeyError:
                pass
    return matrix
