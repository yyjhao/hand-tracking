from pykalman import KalmanFilter
import math
import numpy as np
import random

transition_matrices = [1]
observation_matrices = [1]

kf = KalmanFilter(
    transition_matrices=transition_matrices,
    observation_matrices=observation_matrices,
    # observation_covariance=observation_covariance,
)
# kf = kf.em(lst_points_v, n_iter=10)

points = [1, 2, 3, 4, 5, 5, 6, 7, 8, 9, 9, 9, 10, 11, 2]

(filtered_state_means, filtered_state_covariances) = kf.filter(points)

for i in zip(filtered_state_means, points):
    print i
