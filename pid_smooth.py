import argparse

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

def main(input_file, output_file):
	outputs = []
	prev_smoothed = []
	cumulative_error = []
	smoothed_output = []
	prev_error = []
	error = []
	with open(input_file) as f:
		for line in f:
			target = [float(num) for num in line.split(", ")]
			prev_smoothed = smoothed_output if smoothed_output else target
			prev_error = error
			error = get_error(prev = prev_smoothed, curr = target)
			error_derivative = differentiate(prev = prev_error, curr = error)
			cumulative_error = accumulate(prev = cumulative_error, curr = error)

			smoothed_output = pid_output(prev = prev_smoothed, p = error, i = cumulative_error, d = error_derivative)
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
