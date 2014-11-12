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
            1 if (i == j or (j - 1 == i and not (i % 2))) else 0 for j in range(len(lst_points_v[0]))
        ] for i in range(len(lst_points_v[0]))
    ]
    observation_matrices = [
        [
            1 if (i == j) else 0 for j in range(len(lst_points_v[0]))
        ] for i in range(len(lst_points_v[0]))
    ]

    observation_covariance = [
        [
            3 if (i == j) else 0 for j in range(len(lst_points_v[0]))
        ] for i in range(len(lst_points_v[0]))
    ]

    for i in range(len(lst_points_v[0])):
        if i % 2:
            observation_matrices[i][i] = 30

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
        observation_covariance=observation_covariance,
    )
    # kf = kf.em(lst_points_v, n_iter=10)

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
    # pb = unit(p_add(pa, p_scalar(1, p_minus(pb, pa))))

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


def get_point(vec, ind):
    return (
        vec[ind * 6],
        vec[ind * 6 + 2],
        vec[ind * 6 + 4]
    )


def rotation_adv(prev, cur):

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

    # for u in adj[0]:
    #     new_pos[u] = p_add(get_point(cur, u), p_minus(get_point(cur, u), get_point(prev, u)))

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


def magnitude(p):
    return math.sqrt(dot_p(p, p))


def max_distance(points):
    return max(magnitude(p_minus(p1, p2)) for p1 in points for p2 in points) / (len(points) * (len(points) - 1))


def squeez_matric(frame):
    return max_distance([get_point(frame, ind) for ind in adj[0][1:]])


def fix_squeez(cur, prev):
    for i in range(len(cur)):
        cur[i] = prev[i]
    for i in range(len(cur) / 2):
        cur[i * 2] += cur[i * 2 + 1]


def correct_squeez(points_v):
    max_dist = 0
    prev = points_v[0]
    for frame in points_v[1:]:
        d = squeez_matric(frame)
        print d
        if d > max_dist:
            max_dist = d
        if d < max_dist / 2:
            fix_squeez(frame, prev)
        prev = frame

def correct_frame(cur, prev):
    for i in range(len(cur)):
        cur[i] = prev[i]
    # for i in range(len(cur) / 2)
    #     cur[i * 2] += cur[i * 2 + 1] * 0.1

def correct_velocity(cur, prev):
    for i in range(len(cur) / 2):
        cur[i * 2 + 1] = cur[i * 2] - prev[i * 2]

def correct_points(points_v):
    prev = points_v[0]
    max_dist = 0
    last_correct = None
    for frame in points_v[1:]:
        total = 0
        for a, b in [(1, 16), (4, 12), (16, 1), (12, 4)]:
            dist = 0
            for j in range(0, 6, 2):
                dist += (frame[a * 6 + j] - prev[b * 6 + j]) ** 2
            total += math.sqrt(dist)
        matric = max_distance([p_scalar(0.5, p_add(get_point(frame, p), get_point(prev, p))) for p in [1, 4, 12, 16]])
        max_dist = max(matric, max_dist)
        if matric < max_dist / 2:
            if last_correct:
                correct_frame(prev, last_correct)
                correct_velocity(frame, prev)
                last_correct = None
            else:
                last_correct = [i for i in frame]
                correct_frame(frame, prev)
        else:
            last_correct = None
        correct_velocity(frame, prev)
        prev = frame


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
    correct_points(points_v)
    filtered, smoothed = smooth(to_rotation_vec(points_v))
    correct_squeez(filtered) 
    with open("filtered", 'w') as fout:
        fout.write("\n".join(", ".join(from_points_v(list(f))) for f in filtered))

    with open("smoothed", 'w') as fout:
        fout.write("\n".join(", ".join(from_points_v(list(f))) for f in smoothed))

kal("bin/yjunstable.txt")
