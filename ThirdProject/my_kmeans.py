import numpy as np
import random
import sys
import matplotlib.pyplot as plt
import time
from scipy.cluster.vq import kmeans2, kmeans

def calcDistance(center, point):
    return np.sqrt(np.power(center[0] - point[0], 2) + np.power(center[1] - point[1], 2))


def assignPointsToNearestCluster(centers, data):
    # create index array to tag cluster to each data point
    index = np.zeros(len(data[0, :]))
    # assign points to clusters/centers
    for i in range(len(data[0, :])):
        min_dist = sys.float_info.max
        cluster = -1
        for j in range(len(centers[:, 0])):
            distFromCenterToPoint = calcDistance(centers[j, :], data[:, i])
            if distFromCenterToPoint < min_dist:
                min_dist = distFromCenterToPoint
                cluster = j

        index[i] = cluster

        # SOME POSSIBILITY TO SPEED UP
        # tree = scipy.spatial.KDTree( centers )
        # index = np.zeros( len(data[0,:]) )

        # # assign points to clusters/centers
        # for i in range( len(data[0,:]) ):
        # [ distance , location] = tree.query( data[:,i] )
        # index[i] = location
        # return index

    return index


def calculateObjectiveFunction(centers, data, index, j, i, original_size, new_center0, new_center1):
    #error = 0.0
    #for i in range(len(data[0, :])):
    #    for j in range(len(centers[:, 0])):
    #        if index[i] == j:
    #            error += calcDistance(centers[j, :], data[:, i])
    new_center = [new_center0, new_center1]
    return calcDistance(new_center, data[:, i]) + original_size * calcDistance(centers[j, :], new_center)



def calcMeanOfCenter(centers, index, i):
    centers[i, 0] = 0.0
    centers[i, 1] = 0.0

    # calculate new position of centroid i
    num_of_points_in_cluster = sum(index == i)  # sum number of points assigned to a center

    for j in range(len(index)):  # loop over all indexes of points
        if index[j] == i:  # if point is assigned to center add it
            centers[i, 0] = centers[i, 0] + data[0, j]
            centers[i, 1] = centers[i, 1] + data[1, j]

    if num_of_points_in_cluster != 0:
        centers[i, 0] /= float(num_of_points_in_cluster)
        centers[i, 1] /= float(num_of_points_in_cluster)

    return centers


def determineWinnerCentroid(centers, x):
    min_dist = sys.float_info.max
    center_index = -1
    for i in range(len(centers[:, 0])):
        distFromCenterToPoint = calcDistance(centers[i, :], x)
        if (distFromCenterToPoint < min_dist):
            min_dist = distFromCenterToPoint
            center_index = i

    return center_index


def LIoyds_Built_in(data, k):

    data_transposed = np.transpose(data)
    centers , distortion_factor = kmeans( data_transposed , k)
    index = assignPointsToNearestCluster(centers, data)

    return index, centers

def LIoyds(data, k):
    min_val_X, min_val_Y, max_val_X, max_val_Y = min(data[0, :]), min(data[1, :]), max(data[0, :]), max(data[1, :])

    # initialize centers
    centers = np.zeros((k, 2), np.float64)
    for i in range(k):
        centers[i, 0] = random.uniform(min_val_X, max_val_X)
        centers[i, 1] = random.uniform(min_val_Y, max_val_Y)

    index = np.zeros(len(data[0, :]))
    index_previous = np.zeros(len(data[0, :]))

    # loop until there is no change in assignment to clusters
    count = 0
    while True:
        count+=1
        index = assignPointsToNearestCluster(centers, data)

        # if assignment to centers did not change then stop algorithm
        if np.array_equal(index, index_previous):
            break

        # compute centers for all centroids
        for l in range(k):
            centers = calcMeanOfCenter(centers, index, l)

        index_previous = np.copy(index)
    #print count
    return index, centers


def Hartigan(data, k):
    # initialize centers
    centers = np.zeros((k, 2), np.float64)
    n = len(data[0, :])

    # randomly assign points to clusters
    index = np.zeros(n)
    for i in range(n):
        index[i] = random.randint(0, k-1)

    # compute mean of centers, we only need to compute before iteration once
    for i in range(0, k):
        centers = calcMeanOfCenter(centers, index, i)

    converged = False
    # loop until there is no change in assignment to clusters
    count = 0
    while converged is False:
        count+=1
        converged = True
        for j in range(n):
            init_center = index[j]  # get center i of point j
            original_size = sum(index == init_center)
            index[j] = -1  # remove point j from center
            centers[init_center, 0] = (centers[init_center, 0] * original_size - data[0, j]) / (original_size-1)
            centers[init_center, 1] = (centers[init_center, 1] * original_size - data[1, j]) / (original_size-1)
            min_error = sys.float_info.max
            proper_cluster = -1

            for i in range(k):
                original_size = sum(index == i)
                index[j] = i  # assign point j to cluster i
                new_center0 = (centers[i, 0] * original_size + data[0, j]) / (original_size+1)
                new_center1 = (centers[i, 1] * original_size + data[1, j]) / (original_size+1)
                objFunResult = calculateObjectiveFunction(centers, data, index, i, j, original_size, new_center0, new_center1)
                if min_error > objFunResult:
                    min_error = objFunResult
                    proper_cluster = i

            if proper_cluster != init_center:  # if no change in assignment to centers
                converged = False  # converged

            size = sum(index == proper_cluster)
            index[j] = proper_cluster  # assign point to cluster for which objective function is the lowest
            centers[proper_cluster, 0] = (centers[proper_cluster, 0] * size + data[0, j]) / (size+1)
            centers[proper_cluster, 1] = (centers[proper_cluster, 1] * size + data[1, j]) / (size+1)
    #print count
    return index, centers

def MacQueen(data , k):
    min_val_X = min(data[0, :])
    min_val_Y = min(data[1, :])
    max_val_X = max(data[0, :])
    max_val_Y = max(data[1, :])

    # initialize centers
    centers = np.zeros((k, 2), np.float64 )
    for i in range(k):
        centers[i, 0] = random.uniform(min_val_X, max_val_X)
        centers[i, 1] = random.uniform(min_val_Y, max_val_Y)

    n = 0
    for j in range(len(data[0, :])):
        center_index = determineWinnerCentroid(centers, data[:, j])
        n += 1
        centers[center_index, :] += 1/float(n)*(data[:, j] - centers[center_index, :])

    index = assignPointsToNearestCluster(centers, data)

    return index, centers


def plotData(data , indexes , centers , k,  str, axs):
    colors = ['red', 'orange', 'green']
    for i in range(0, k):
        bool_idx = (indexes == i)
        axs.scatter(data[0, bool_idx], data[1, bool_idx], color=colors[i])
        axs.scatter(centers[i, 0], centers[i, 1], s=100, color=colors[i], edgecolors='black')

    axs.set_title(str)
    return axs


def measureAlgRunTimes(data):
    start = time.time()
    for i in range(10):
        LIoyds_Built_in(data, 3)
    end = time.time()
    avg_time = (end - start)/10.0

    print "LIoyds algorithm built-in time:   ",avg_time

    start = time.time()
    for i in range(10):
        LIoyds(data, 3)
    end = time.time()
    avg_time = (end - start)/10.0

    print "LIoyds algorithm average time:   ",avg_time

    start = time.time()
    for i in range(10):
        Hartigan(data, 3)
    end = time.time()
    avg_time = (end - start)/10.0

    print "Hartigan algorithm average time:   ",avg_time

    start = time.time()
    for i in range(10):
        MacQueen(data, 3)
    end = time.time()
    avg_time = (end - start)/10.0

    print "MacQueen algorithm average time:   ",avg_time


data = np.loadtxt('resources/data-clustering-1.csv', None, comments='#', delimiter=',')
fig = plt.figure()
axs1 = fig.add_subplot(141)
axs2 = fig.add_subplot(142)
axs3 = fig.add_subplot(143)
axs4 = fig.add_subplot(144)

[indexes, centers] = LIoyds_Built_in(data, 3)
axs1 = plotData(data, indexes, centers, 3, "LIoyds built-in", axs1)

[indexes, centers] = LIoyds(data, 3)
axs2 = plotData(data, indexes, centers, 3, "LIoyds", axs2)

[indexes, centers] = Hartigan(data, 3)
axs3 = plotData(data, indexes, centers, 3, "Hartigan", axs3)

[indexes, centers] = MacQueen(data, 3)
axs4 = plotData(data, indexes, centers, 3, "MacQueen", axs4)


plt.show()
measureAlgRunTimes(data)


