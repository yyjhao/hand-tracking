import re
import sys
from os import listdir, getcwd
from os.path import join
import cmp_points

def print_distance(distances):
    print max(distances), min(distances), sum(distances) / len(distances)

def cmp_file(output, truth):
    with open(output) as out, open(truth) as tru:
        dummy = tru.readline()
        lines = zip([
                [float(i) for i in re.split(',\s', line)]
                    for line in out
            ], [
                [float(i) for i in line.split(' ')]
                    for line in tru
            ])

    matches_counter = [{} for i in range(20)]
    for l1, l2 in lines:
        distance_pairs, matches = cmp_points.match(cmp_points.to_points(l1), cmp_points.to_points(l2))
        if not distance_pairs:
            print l1, l2
            continue
        distances = [i[0] for i in distance_pairs]
        for i, m in enumerate(matches):
            matches_counter[i][m] = matches_counter[i].get(m, 0) + 1
        # print_distance(distances)

    possible_matches = [
        max(((b, a) for a, b in d.items()))[1]
        for d in matches_counter
    ]
    print possible_matches

    total_distance = [0] * 20
    total_max = 0
    total_min = 0
    total_ave = 0
    for l1, l2 in lines:
        ps1 = cmp_points.to_points(l1)
        ps2 = cmp_points.to_points(l2)
        distances = [
            cmp_points.distance(ps1[i], ps2[j]) for i, j in enumerate(possible_matches)
        ]
        total_max += max(distances)
        total_min += min(distances)
        total_ave += sum(distances) / len(distances)
        for d in distances:
            total_distance[i] += d
        print_distance(distances)
    print [d / len(lines) for d  in total_distance]
    print total_max/len(lines), total_min/len(lines), total_ave/len(lines)


output_file = join(getcwd(), sys.argv[1])
truth_file = join(getcwd(), sys.argv[2])

cmp_file(output_file, truth_file)
