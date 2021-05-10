import os
import pandas as pd
import numpy as np
from utils import *
from traj_cluster import *
from compress import compress_traj
from generate_POI import *
from POI_anylysis import *


class HandledFilesProcessor:
    def __init__(self, path):
        files = os.listdir(path)
        self.df_container = []
        self.df_cluster_dic = None
        self.stop_points = None
        self.interest_of_cluster = None
        self.cluster_of_traj = None
        self.cluster_for_points = None
        for file in files:
            df = pd.read_csv(path + '/' + file, converters={'Date_Time': parse_dates})
            self.df_container.append(df)

    def get_whole_points(self):
        whole_points = []
        for df in self.df_container:
            for i in range(len(df)):
                whole_points.append([df.Longitude[i], df.Latitude[i]])
        return whole_points

    def get_center(self):
        points = self.get_whole_points()
        lon = [points[i][0] for i in range(len(points))]
        lat = [points[i][1] for i in range(len(points))]
        return np.median(lon), np.median(lat)

    def get_whole_traj(self):
        whole_traj = []
        for df in self.df_container:
            whole_traj.append([[df.Longitude[i], df.Latitude[i]] for i in range(len(df))])
        return whole_traj

    def compress(self):
        for i in range(len(self.df_container)):
            self.df_container[i] = compress_traj(self.df_container[i])

    def generate_traj_cluster(self):
        if self.df_cluster_dic is None:
            self.df_cluster_dic = traj_cluster(self.df_container, time_min_threshold=0.6, dis_max_threshold=0.03)

        keys = self.df_cluster_dic.keys()
        cluster_of_traj = []
        for key in keys:
            trajs = []
            for i in self.df_cluster_dic[key]:
                length = len(self.df_container[i])
                trajs.append([[self.df_container[i].Longitude[index], self.df_container[i].Latitude[index]] for index in range(length)])
            cluster_of_traj.append(trajs)
        return cluster_of_traj

    def get_stop_points(self):
        if self.stop_points is None:
            self.stop_points = get_stop_points(self.df_container)
            # self.stop_points = pd.read_csv('stop_points.csv',
            #                                converters={'start_time': parse_dates, 'end_time': parse_dates})
        whole_df = create_whole_df(self.stop_points)
        print(self.stop_points)
        whole_df = self.stop_points
        coors = [[whole_df['Longitude'][i], whole_df['Latitude'][i]] for i in range(len(whole_df))]
        return coors

    def generate_POI(self):
        if self.stop_points is None:
            self.stop_points = get_stop_points(self.df_container)
            # self.stop_points = pd.read_csv('stop_points.csv',
            #                                converters={'start_time': parse_dates, 'end_time': parse_dates})
        whole_df = create_whole_df(self.stop_points)
        whole_df = self.stop_points
        clusters = create_cluster(whole_df, eps=0.10, min_samples=3)
        poi = get_true_cluster(whole_df, clusters)
        cluster_set = list(set(poi.cluster))
        cluster_of_POI = {}
        for c in cluster_set:
            tmp_df = poi[poi['cluster'] == c]
            tmp_df.reset_index(drop=True, inplace=True)
            cluster_of_POI[str(c)] = [[tmp_df.Longitude[index], tmp_df.Latitude[index]] for index in range(len(tmp_df))]
        return cluster_of_POI

    def get_area_interest(self):
        # 真实应用中应该要whole_df = create_whole_df(self.stop_points)
        whole_df = self.stop_points
        interest_of_cluster, cluster_for_points = cal_interest(whole_df)
        self.cluster_for_points = cluster_for_points
        self.interest_of_cluster = interest_of_cluster
        return interest_of_cluster

    def get_main_traj_semantic(self):
        # test_trajs = []
        # for key in self.df_cluster_dic.keys():
        #     if len(self.df_cluster_dic[key]) > 5:
        #         test_trajs.append(self.df_cluster_dic[key][1])
    #     TODO: need to complete, this is a show sample
        traj_1 = [
                    {'Longitude': 116.37934829203542, 'Latitude': 39.898900566371694, 'type': '工作地'},
                    {'Longitude': 116.33738663505751, 'Latitude': 39.92641110344823, 'type': '居住地'}
                  ]
        traj_2 = [
                    {'Longitude': 116.33769266101696, 'Latitude': 39.925048466101714, 'type': '居住地'},
                    {'Longitude': 116.38360090243903, 'Latitude': 39.90042758536585, 'type': '工作地'}
                  ]
        traj_3 = [
                    {'Longitude': 116.35752140000002, 'Latitude':  39.93757655, 'type': '餐饮'},
                    {'Longitude': 116.38592079874209, 'Latitude':  39.89846633962268, 'type': '工作地'},
                    {'Longitude': 116.33744147488585, 'Latitude': 39.926220621004525, 'type': '居住地'}
                  ]
        return [traj_1, traj_2, traj_3]




    def generate_homeAngWork_place_points(self):
        if self.df_cluster_dic is None:
            self.generate_traj_cluster()
        if self.interest_of_cluster is None:
            self.get_area_interest()
        max1_index, max2_index = get_max2_in_dic(self.interest_of_cluster)
        if cal_val(self.cluster_for_points[max1_index])>cal_var(self.cluster_for_points[max2_index]):
            to_work_cluster = max1_index
            to_home_cluster = max2_index
        else:
            to_work_cluster = max2_index
            to_home_cluster = max1_index

        home_place_points = []
        work_place_points = []
        if to_home_cluster is not None:
            for i in self.df_cluster_dic[to_home_cluster]:
                work_place_points.append([self.df_container[i].Longitude[0], self.df_container[i].Latitude[0]])
                home_place_points.append([list(self.df_container[i].Longitude)[-1], list(self.df_container[i].Latitude)[-1]])
        if to_work_cluster is not None:
            for i in self.df_cluster_dic[to_work_cluster]:
                home_place_points.append([self.df_container[i].Longitude[0], self.df_container[i].Latitude[0]])
                work_place_points.append([list(self.df_container[i].Longitude)[-1], list(self.df_container[i].Latitude)[-1]])
        return home_place_points, work_place_points

