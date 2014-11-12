from pykalman import KalmanFilter
import numpy as np


def smooth(lst_points_v):
    transition_matrices = [
        [
            1 if (i == j or (j - 1 == i and ((i - 2) % 3))) else 0 for j in range(len(lst_points_v[0]))
        ] for i in range(len(lst_points_v[0]))
    ]
    observation_matrices = [
        [
            1 if (i == j) else 0 for j in range(len(lst_points_v[0]))
        ] for i in range(len(lst_points_v[0]))
    ]

    initial_state_covariance = [
        [
            1 if (i == j) else 0 for j in range(len(lst_points_v[0]))
        ] for i in range(len(lst_points_v[0]))
    ]

    def covar(i, j, val):
        initial_state_covariance[i][j] = initial_state_covariance[j][i] = val
    for i in range(len(lst_points_v[0]) / 3):
        covar(i * 3, i * 3 + 1, .1)
        covar(i * 3 + 2, i * 3 + 1, .1)

    # for i in range(len(lst_points_v[0]) / 9):
    #     for j in range(9):
    #         for k in range(9):
    #             if j == k:
    #                 continue
    #             covar(i * 9 + k, i * 9 + j, 3)

    joints = [
        (0, 1),
        (1, 2),
        (2, 3),
        (0, 4),
        (4, 5),
        (5, 6),
        (6, 7),
        (0, 8),
        (8, 9),
        (9, 10),
        (10, 11),
        (0, 12),
        (12, 13),
        (13, 14),
        (14, 15),
        (0, 16),
        (16, 17),
        (17, 18),
        (18, 19)
    ]

    for i, j in joints:
        for k in range(9):
            if k % 3:
                covar(i * 9 + k, j + 9 + k, .2)

    # tips = [
    #     3,
    #     7,
    #     11,
    #     15,
    #     19,
    # ]

    # for t in tips:
    #     for k in range(9):
    #         covar(t * 9 + k, t * 9 + k, .3)

    for k in range(9):
        covar(k, k, .3)

    kf = KalmanFilter(
        transition_matrices=transition_matrices,
        observation_matrices=observation_matrices,
        observation_covariance=initial_state_covariance,
    )
    kf = kf.em(lst_points_v, n_iter=4)

    (filtered_state_means, filtered_state_covariances) = kf.filter(lst_points_v)
    (smoothed_state_means, smoothed_state_covariances) = kf.smooth(lst_points_v)

    return (filtered_state_means, smoothed_state_means)


def point_to_point_v(ppv_point, prev_point, point):
    for cp, (c1, c2) in zip(ppv_point, zip(prev_point, point)):
        yield c2
        yield c2 - c1
        yield (c2 - c1) - (c1 - cp)




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
    return [str(points_v[i]) for i in range(len(points_v)) if not (i % 3)]


def kal(fin):
    points_v = []
    with open(fin) as f:
        for line in f:
            points = to_points(float(num) for num in line.split(", "))
            prevp = 0
            curp = 0
            ppp = 0
            cur = []
            while curp < len(points):
                cur.extend(list(point_to_point_v(points[ppp], points[prevp], points[curp])))
                ppp = prevp
                prevp = curp
                curp += 1
            points_v.append(cur)
    filtered, smoothed = smooth(points_v)
    with open("filtered", 'w') as fout:
        fout.write("\n".join(", ".join(from_points_v(list(f))) for f in filtered))

    with open("smoothed", 'w') as fout:
        fout.write("\n".join(", ".join(from_points_v(list(f))) for f in smoothed))

kal("bin/yjunstable.txt")
