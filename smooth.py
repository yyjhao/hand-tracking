from pykalman import KalmanFilter
import numpy as np


def smooth(lst_points_v):
    transition_matrices = [
        [
            1 if (i == j or (j - 1 == i and not (i % 2))) else 0 for j in range(len(lst_points_v[0]))
        ] for i in range(len(lst_points_v[0]))
    ]
    observation_matrices = [
        [
            1 if i == j else 0 for j in range(len(lst_points_v[0]))
        ] for i in range(len(lst_points_v[0]))
    ]
    kf = KalmanFilter(transition_matrices=transition_matrices, observation_matrices=observation_matrices)
    kf = kf.em(lst_points_v, n_iter=2)

    (filtered_state_means, filtered_state_covariances) = kf.filter(lst_points_v)
    (smoothed_state_means, smoothed_state_covariances) = kf.smooth(lst_points_v)

    return (filtered_state_means, smoothed_state_means)


def point_to_point_v(prev_point, point):
    for c1, c2 in zip(prev_point, point):
        yield c2
        yield c2 - c1


def to_points(nums):
    points = []
    point = []
    for n in nums:
        point.append(n)
        if len(point) == 3:
            points.append(point)
            point = []
    return points


def from_points_v(points_v):
    return [str(points_v[i]) for i in range(len(points_v)) if not (i % 2)]


def kal(fin):
    points_v = []
    with open(fin) as f:
        for line in f:
            points = to_points(float(num) for num in line.split(", "))
            prevp = 0
            curp = 0
            cur = []
            while curp < len(points):
                cur.extend(list(point_to_point_v(points[prevp], points[curp])))
                prevp = curp
                curp += 1
            points_v.append(cur)
    filtered, smoothed = smooth(points_v)
    with open("filtered", 'w') as fout:
        fout.write("\n".join(", ".join(from_points_v(list(f))) for f in filtered))

    with open("smoothed", 'w') as fout:
        fout.write("\n".join(", ".join(from_points_v(list(f))) for f in smoothed))

kal("bin/pllvtiptouch.txt")
