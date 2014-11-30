import matplotlib.pyplot as plt

# plot coordinates from f1 and f2 as specified by inds

f1 = "filtered"
f2 = "bin/pllvtiptouch.txt"

inds = [0, 1, 2]

f_label = ["filtered", "unfiltered"]
ind_label = ["x", "y", "z"]


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

for ind, (a, b) in enumerate(zip(get_inds(f1, inds), get_inds(f2, inds))):
    fig = plt.figure()

    ax = fig.add_subplot(1, 1, 0)
    ax.set_xlabel('Time')
    ax.set_ylabel('coordinate')
    ax.plot(a[0], label=" ".join([f_label[0], ind_label[ind]]))
    ax.plot(b[0], label=" ".join([f_label[1], ind_label[ind]]))
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels)

    # save the image
    fig.savefig(a[1] + '.png')

# show the image
# plt.show()
