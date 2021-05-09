from utils import *
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import DBSCAN
import math

def calc_distance(lat1, lon1, lat2, lon2):
    theta = lon1 -lon2
    dist = math.sin(math.radians(lat1))*math.sin(math.radians(lat2)) \
            + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))\
            * math.cos(math.radians(theta))
    if dist - 1 > 0 :
        dist = 1
    elif dist +1 < 0 :
        dist = -1
    dist = math.acos(dist)
    dist = math.degrees(dist)
    miles = dist * 60 * 1.1515
    return miles


def get_distance(p1, p2):
    lat1, lon1 = p1[0], p1[1]
    lat2, lon2 = p2[0], p2[1]
    distance = calc_distance(lat1, lon1, lat2, lon2) * 1.609344
    return distance


def denoise(df):
    new_column = [0 for index in range(len(df))]
    df['Distance'] = new_column  # 单位为m
    df['Velocity'] = new_column  # 单位为km/h
    df['delta_t'] = new_column  # 单位为秒
    for i in range(1, len(df)):
        delta_t = df.Date_Time[i] - df.Date_Time[i - 1]
        dis = cal_distance(df.Latitude[i], df.Longitude[i], df.Latitude[i - 1], df.Longitude[i - 1])
        vel = cal_velocity(df.Latitude[i], df.Longitude[i], df.Latitude[i - 1], df.Longitude[i - 1], delta_t)
        delta_t = delta_t / np.timedelta64(1, 'D') * 24 * 3600
        df.loc[i, 'Distance'] = dis
        if vel == -1 or dis == -1:
            df.drop(i)
        else:
            df.loc[i, 'Velocity'] = vel
            df.loc[i, 'delta_t'] = delta_t
    df.reset_index(drop=True, inplace=True)

    max_velocity = {'walk': 12, 'bus': 60, 'bike': 20, 'taxi': 80, 'subway': 80, 'airplane': 900, 'train': 300}

    trans_list = list(set(df['Label']))
    trans_dic = {}
    for trans in trans_list:
        trans_dic[trans] = df[(df.Label == trans) & (df.Velocity < max_velocity[trans]) & (df.Velocity >= 0)]
    for trans in trans_list:
        tmp_df = trans_dic[trans]
        distance_matrix = squareform(pdist(tmp_df, (lambda u, v: get_distance(u, v))))
        time = (tmp_df.delta_t.mean() + 0.1) / 3600
        vel = max_velocity[trans]
        s = time * vel
        db = DBSCAN(eps=s, min_samples=3, metric='precomputed')
        cluster = db.fit_predict(distance_matrix)
        tmp_df['Cluster'] = cluster

    new_df = pd.DataFrame()
    for key in trans_dic.keys():
        new_df = pd.concat([new_df, trans_dic[key]])
    new_df = new_df.drop(new_df[new_df['Cluster'] == -1].index)
    new_df = new_df.sort_index()
    new_df.reset_index(drop=True, inplace=True)
    return new_df
