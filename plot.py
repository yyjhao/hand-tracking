import matplotlib.pyplot as plt

f1 = "filtered"
f2 = "bin/pllvtiptouch.txt"


def transpose(mat):
    return [
        [mat[i][j] for i in range(len(mat))]
        for j in range(len(mat[0]))
    ]

def get_inds(filename, inds):
    with open(filename) as fin:
        return [
            (data, filename + str(ind)) for data, ind in zip(
                transpose([
                    [line.strip().split(", ")[ind] for ind in inds]
                    for line in fin
                ]), inds)
        ]

inds = [21, 22, 23]

for a, b in zip(get_inds(f1, inds), get_inds(f2, inds)):
    fig = plt.figure()

    ax = fig.add_subplot(1, 1, 0)
    ax.set_xlabel('Time')
    ax.set_ylabel('coordinate')
    ax.plot(a[0], label=a[1])
    ax.plot(b[0], label=b[1])
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels)

plt.show()
