import numpy as np
import pandas as pd
from utils import *


def is_to_work_time(time_interval):
    begin_time = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,6, 0, 0)
    end_time = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,12, 0, 0)
    if time_interval[0] > begin_time and time_interval[1] < end_time:
        return True
    else:
        return False


def is_to_home_time(time_interval):
    begin_time = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,16, 0, 0)
    end_time = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,23, 59, 0)
    if time_interval[0] > begin_time and time_interval[1] < end_time:
        return True
    else:
        return False


def get_time_interval(container, indexs):
    tmp_df = pd.DataFrame()
    for index in indexs:
        tmp_df = pd.concat([tmp_df, container[index]], ignore_index=True)
    tmp_df.Date_Time = [datetime.datetime.combine(datetime.date.today(), tmp_time.time()) for tmp_time in tmp_df.Date_Time]
    time_list = list(tmp_df.Date_Time)
    time_list.sort()
    return time_list[0], time_list[-1]


class VisitList:
    def __init__(self, count):
        self.unvisited_list = [i for i in range(count)]
        self.visited_list = list()
        self.unvisited_num = count

    def visit(self, point_id):
        self.visited_list.append(point_id)
        self.unvisited_list.remove(point_id)
        self.unvisited_num -= 1

def traj_cluster(df_container, minPts = 3, time_min_threshold=0.5, dis_max_threshold=0.10):
    length = len(df_container)
    dis_matrix = np.zeros((length, length))
    for i in range(length):
        for j in range(i + 1, length):
            time_sim = similarity_of_time(df_container[i], df_container[j])
            if time_sim > time_min_threshold:
                dis = similarity_of_dis(df_container[i], df_container[j])
                dis_matrix[i][j] = dis_matrix[j][i] = dis
            else:
                dis_matrix[i][j] = dis_matrix[j][i] = 1000
    db = DBSCAN(eps=dis_max_threshold, min_samples=minPts, metric='precomputed')
    cluster = db.fit_predict(dis_matrix)
    cluster_type = list(set(cluster))
    if -1 in cluster_type:
        cluster_type.remove(-1)
    cluster_container = {}
    for c in cluster_type:
        cluster_container[c] = np.where(cluster == c)[0]
    return cluster_container


def traj_cluster_old(df_container, minPts = 3, time_min_threshold=0.05, dis_max_threshold=0.10):
    length = len(df_container)
    is_neighbor_matrix = np.zeros((length, length))
    for i in range(length):
        for j in range(i+1,length):
            if is_neighbor(df_container[i], df_container[j], time_min_threshold=time_min_threshold, dis_max_threshold=dis_max_threshold):
                is_neighbor_matrix[i][j] = is_neighbor_matrix[j][i] = 1
    vPoints = VisitList(count=length)
    cluster_num = -1
    cluster_container = [-1 for i in range(length)]
    while vPoints.unvisited_num > 0:
        choice = vPoints.unvisited_list[0]
        vPoints.visit(choice)
        neighbors = np.array([i*is_neighbor_matrix[choice][i] for i in range(length)])
        neighbors = list(neighbors[neighbors != 0])
        if len(neighbors) > minPts:
            cluster_num += 1
            cluster_container[choice] = cluster_num
            for neighbor in neighbors:
                neighbor = int(neighbor)
                if neighbor in vPoints.unvisited_list:
                    vPoints.visit(neighbor)
                    if cluster_container[neighbor] == -1:
                        cluster_container[neighbor] = cluster_num
                    tmp_neighbors = np.array([i*is_neighbor_matrix[neighbor][i] for i in range(length)])
                    tmp_neighbors = list(tmp_neighbors[tmp_neighbors != 0])
                    if len(tmp_neighbors) > minPts:
                        for n in tmp_neighbors:
                            if n not in neighbors:
                                neighbors.append(n)
    ans = {}
    print(cluster_container)
    for i in range(0, cluster_num+1):
        ans[i] = [index for index in range(length) if cluster_container[index] == i]
    return ans
