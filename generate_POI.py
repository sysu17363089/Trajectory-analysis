from geopy.distance import geodesic
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import DBSCAN
from sklearn.cluster import OPTICS, cluster_optics_dbscan


def cal_distance(lon1, lat1, lon2, lat2):
    return geodesic((lat1, lon1), (lat2, lon2)).km


def cal_time(time1, time2):
    delta_t = time2 - time1
    return delta_t / np.timedelta64(1, 'D') * 24 * 60


def get_distance(p1, p2):
    lat1, lon1 = p1[1], p1[2]
    lat2, lon2 = p2[1], p2[2]
    distance = cal_distance(lon1, lat1, lon2, lat2)
    return distance


def get_stop_points(container, dis_threshold=0.2, time_threshold=30):
    # dis(km); time(min)
    stop_points_of_day = []
    for index in range(len(container)):
        df = container[index]
        points_dic = {'Latitude': [], 'Longitude': [], 'start_time': [], 'end_time': []}
        i = 0
        while i < len(df) - 1:
            j = i + 1
            while j < len(df) - 1 and cal_distance(df.Longitude[i], df.Latitude[i], df.Longitude[j],
                                                   df.Latitude[j]) < dis_threshold:
                j += 1
            if cal_time(df.Date_Time[i], df.Date_Time[j]) > time_threshold:
                lat = np.mean(df.Latitude[i: j + 1])
                lng = np.mean(df.Longitude[i: j + 1])
                points_dic['Latitude'].append(lat)
                points_dic['Longitude'].append(lng)
                points_dic['start_time'].append(df.Date_Time[i])
                points_dic['end_time'].append(df.Date_Time[j])
                i = j + 1
            else:
                i += 1
                while i <= j and df.Velocity[i] > 1.5:
                    i += 1
        if len(points_dic['Latitude']) > 0:
            points_df = pd.DataFrame(points_dic)
            stop_points_of_day.append(points_df)
    return stop_points_of_day


def create_cluster(df, eps=0.03, min_samples=5, cluster=0):
    distance_matrix = squareform(pdist(df, (lambda u, v: get_distance(u, v))))
    if cluster == 0:
        db = DBSCAN(eps=eps, min_samples=min_samples, metric='precomputed')
        cluster = db.fit_predict(distance_matrix)
    else:
        opt = OPTICS(min_samples=50, xi=.05, min_cluster_size=.03, metric='precomputed')
        cluster = opt.fit(distance_matrix)

    return cluster


def create_whole_df(container):
    whole_df = pd.DataFrame()
    for df in container:
        whole_df = pd.concat([whole_df, df], ignore_index=True)
    return whole_df


def get_true_cluster(df, cluster):
    df['cluster'] = cluster
    df = df[df.cluster != -1]
    df.reset_index(drop=True, inplace=True)
    return df
