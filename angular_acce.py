from pykalman import KalmanFilter
import math
import numpy as np

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

tweaked_joints = [
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
    (12, 16),
    (16, 17),
    (17, 18),
    (18, 19)
]

adj = [[] for i in range(20)]
for a, b in tweaked_joints:
    adj[a].append(b)


def smooth(lst_points_v):
    transition_matrices = [
        [
            1 if (i == j or (j - 1 == i and ((i - 2) % 3)) or (j - 2 == i and not (i % 3))) else 0 for j in range(len(lst_points_v[0]))
        ] for i in range(len(lst_points_v[0]))
    ]
    observation_matrices = [
        [
            1 if (i == j) else 0 for j in range(len(lst_points_v[0]))
        ] for i in range(len(lst_points_v[0]))
    ]

    # def covar(i, j, val):
    #     observation_covariance[i][j] = observation_covariance[j][i] = val
    # for i in range(len(lst_points_v[0]) / 2):
    #     covar(i * 2, i * 2 + 1, .1)

    # for i, j in joints:
    #     for k in range(6):
    #         if k % 2:
    #             covar(i * 6 + k, j + 6 + k, .2)

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

    # for k in range(9):
    #     covar(k, k, .3)

    kf = KalmanFilter(
        transition_matrices=transition_matrices,
        observation_matrices=observation_matrices,
        # observation_covariance=observation_covariance,
    )

    (filtered_state_means, filtered_state_covariances) = kf.filter(lst_points_v)
    (smoothed_state_means, smoothed_state_covariances) = kf.smooth(lst_points_v)

    return (filtered_state_means, smoothed_state_means)


def point_to_point_v(prev_point, point):
    for c1, c2 in zip(prev_point, point):
        yield c2
        yield c2 - c1


def p_minus(a, b):
    if isinstance(a, tuple):
        return tuple(p_minus(ia, ib) for ia, ib in zip(a, b))
    else:
        return a - b


def p_add(a, b):
    if isinstance(a, tuple):
        return tuple(p_add(ia, ib) for ia, ib in zip(a, b))
    else:
        return a + b


def cross_p(a, b):
    return (
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    )


def dot_p(a, b):
    return sum(ia * ib for ia, ib in zip(a, b))


def p_scalar(k, v):
    if isinstance(v, tuple):
        return tuple(p_scalar(k, vi) for vi in v)
    else:
        return k * v


def transpose(v):
    return tuple(
        tuple(v[j][i] for j in range(len(v[0])))
        for i in range(len(v))
    )


def p_mul(va, vb):
    tvb = transpose(vb)
    return tuple(
        tuple(dot_p(vai, vbj) for vbj in tvb)
        for vai in va
    )


identity = (
    (1, 0, 0),
    (0, 1, 0),
    (0, 0, 1)
)


def unit(v):
    l = math.sqrt(dot_p(v, v))
    return tuple(i / l for i in v)

def get_rotation(a, b):
    ''' as per http://math.stackexchange.com/questions/180418/calculate-rotation-matrix-to-align-vector-a-to-vector-b-in-3d '''
    pa = unit(a)
    pb = unit(b)
    pb = unit(p_add(pa, p_scalar(0.5, p_minus(pb, pa))))

    v = cross_p(pa, pb)
    s = math.sqrt(dot_p(v, v))
    if not s:
        return identity
    c = dot_p(pa, pb)
    vx = (
        (0, -v[2], v[1]),
        (v[2], 0, -v[0]),
        (-v[1], v[0], 0)
    )
    return p_add(p_add(identity, vx), p_scalar(float(1 - c) / s / s, p_mul(vx, vx)))



def new_p_with_rotation(rot, pa, pb, npa):
    vec = p_minus(pb, pa)
    new_vec = (dot_p(r, vec) for r in rot)
    return p_add(npa, new_vec)


def rotation_adv(prev, cur):
    def get_point(vec, ind):
        return (
            vec[ind * 6],
            vec[ind * 6 + 2],
            vec[ind * 6 + 4]
        )

    rotations = {}
    for a, b in tweaked_joints:
        ap = get_point(prev, a)
        bp = get_point(prev, b)
        cap = get_point(cur, a)
        cbp = get_point(cur, b)
        rotation = get_rotation(p_minus(bp, ap), p_minus(cbp, cap))
        rotations[(a, b)] = rotation

    new_pos = [() for i in range(20)]
    new_pos[0] = p_add(get_point(cur, 0), p_minus(get_point(cur, 0), get_point(prev, 0)))

    for u in adj[0]:
        new_pos[u] = p_add(get_point(cur, u), p_minus(get_point(cur, u), get_point(prev, u)))

    def populate_new_pos(u):
        for v in adj[u]:
            if not new_pos[v]:
                new_pos[v] = new_p_with_rotation(rotations[(u, v)], get_point(cur, u), get_point(cur, v), new_pos[u])
            populate_new_pos(v)

    populate_new_pos(0)

    for ind, p in enumerate(new_pos):
        cur[ind * 6 + 1], cur[ind * 6 + 3], cur[ind * 6 + 5] = p_minus(p, get_point(cur, ind))
        # cur[ind * 6 + 1], cur[ind * 6 + 3], cur[ind * 6 + 5] = 0, 0, 0
        # cur[ind * 6], cur[ind * 6 + 2], cur[ind * 6 + 4] = p



def to_rotation_vec(vec):
    for i in range(len(vec) - 1):
        rotation_adv(vec[i], vec[i + 1])

    return vec

def add_acce(vecs):
    cur = []
    for i in range(len(vecs[0]) / 2):
        cur.append(vecs[0][i * 2])
        cur.append(vecs[0][i * 2 + 1])
        cur.append(0)
    new_vecs = [cur]
    for i in range(len(vecs) - 1):
        new_cur = []
        for j in range(len(vecs[0]) / 2):
            new_cur.append(vecs[i + 1][j * 2])
            new_cur.append(vecs[i + 1][j * 2 + 1])
            new_cur.append(vecs[i + 1][j * 2 + 1] - vecs[i][j * 2 + 1])
        new_vecs.append(new_cur)
    return new_vecs



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
            cur = []
            while curp < len(points):
                cur.extend(list(point_to_point_v(points[prevp], points[curp])))
                prevp = curp
                curp += 1
            points_v.append(cur)
    filtered, smoothed = smooth(add_acce(to_rotation_vec(points_v)))
    with open("filtered", 'w') as fout:
        fout.write("\n".join(", ".join(from_points_v(list(f))) for f in filtered))

    with open("smoothed", 'w') as fout:
        fout.write("\n".join(", ".join(from_points_v(list(f))) for f in smoothed))

kal("bin/yjunstable.txt")
