import argparse
import math

kp = 0.7
ki = 0.0
kd = -0.2

# Currently building derivative with (t, t-1). Consider (t, t-1, t-2) instead

def get_error(prev, curr):
    return [curr[i] - prev[i] for i in xrange(len(curr))]

def differentiate(prev, curr):
    if not prev:
        return [0 for x in xrange(len(curr))]
    return [curr[i] - prev[i] for i in xrange(len(curr))]

def accumulate(prev, curr):
    if not prev:
        return curr
    else:
        return [prev[i] + curr[i] for i in xrange(len(curr))]

def pid_output(prev, p, i, d):
    return [prev[x] + (kp * p[x]) + (ki * i[x]) + (kd * d[x]) for x in xrange(len(prev))]



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

def magnitude(p):
    return math.sqrt(dot_p(p, p))


def max_distance(points):
    return max(magnitude(p_minus(p1, p2)) for p1 in points for p2 in points) / (len(points) * (len(points) - 1))


def squeez_matric(frame):
    return max_distance([get_point(frame, ind) for ind in [4, 8, 12, 16]])


def get_point(vec, ind):
    return (
        vec[ind * 3],
        vec[ind * 3 + 1],
        vec[ind * 3 + 2]
    )


def correct_output(cur, prev):  
    for i in range(len(cur)):
        cur[i] = prev[i]



def main(input_file, output_file):
    outputs = []
    prev_smoothed = []
    cumulative_error = []
    smoothed_output = []
    prev_error = []
    error = []

    max_dist = 0
    max_input_dist = 0

    prev_target = []

    with open(input_file) as f:
        for line in f:
            target = [float(num) for num in line.split(", ")]

            if prev_target:
                input_d = squeez_matric([(a + b) / 2 for a, b in zip(prev_target, target)])
                max_input_dist = max(max_input_dist, input_d)
                if input_d < max_input_dist / 2:
                    correct_output(target, prev_target)

            prev_smoothed = smoothed_output if smoothed_output else target
            prev_error = error
            error = get_error(prev = prev_smoothed, curr = target)
            error_derivative = differentiate(prev = prev_error, curr = error)
            cumulative_error = accumulate(prev = cumulative_error, curr = error)

            smoothed_output = pid_output(prev = prev_smoothed, p = error, i = cumulative_error, d = error_derivative)

            prev_target = target

            d = squeez_matric(smoothed_output)
            max_dist = max(d, max_dist)
            if d < max_dist / 2:
                correct_output(smoothed_output, prev_smoothed)
            
            outputs.append(smoothed_output)

    with open(output_file, "w") as fout:
        fout.write("\n".join(", ".join(map(str, output)) for output in outputs))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help="file containing input positions to be smoothed")
    parser.add_argument('-o', '--output-file', help="smoothed file name (default is <input>_smoothed)")
    args = parser.parse_args()

    if args.output_file:
        output_file = args.output_file
    else:
        if args.input[-4:] == ".txt":
            output_file = args.input[:-4] + "_smoothed"
        else:
            output_file = args.input + "_smoothed"

    main(input_file = args.input, output_file = output_file)
