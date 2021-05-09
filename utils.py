import numpy as np
from geopy.distance import geodesic
import random
from geog import distance
import datetime
import similaritymeasures
import math
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import DBSCAN


def parse_dates_with_convert(x):
    return datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)


def parse_dates(x):
    return datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')


def random_color():
    colorArr = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    color = ""
    for i in range(6):
        color += colorArr[random.randint(0, 14)]
    return "#" + color


def check_lat(lat):
    if -90 <= lat <= 90:
        return True
    else:
        return False


def check_lon(lon):
    if -180 <= lon <= 180:
        return True
    else:
        return False


def check(lat1, lon1, lat2, lon2):
    if check_lat(lat1) and check_lat(lat2) and check_lon(lon1) and check_lon(lon2):
        return True
    else:
        return False


def cal_distance(lon1, lat1, lon2, lat2):
    # 单位为米
    if check(lat1, lon1, lat2, lon2):
        return geodesic((lat1, lon1), (lat2, lon2)).km * 1000
    else:
        return -1


def calc_distance(lon1, lat1, lon2, lat2):
    theta = lon1 - lon2
    dist = math.sin(math.radians(lat1))*math.sin(math.radians(lat2)) \
            + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))\
            * math.cos(math.radians(theta))
    if dist - 1 > 0:
        dist = 1
    elif dist + 1 < 0:
        dist = -1
    dist = math.acos(dist)
    dist = math.degrees(dist)
    miles = dist * 60 * 1.1515
    return miles


def get_distance(p1, p2):
    lat1, lon1 = p1[1], p1[0]
    lat2, lon2 = p2[1], p2[0]
    distance = calc_distance(lat1, lon1, lat2, lon2) * 1.609344
    return distance


def get_max2_in_dic(dic):
    max1 = 0
    max2 = 0
    max1_index = None
    max2_index = None
    for key in dic.keys():
        if dic[key] > max1:
            max2 = max1
            max1 = dic[key]
            max2_index = max1_index
            max1_index = key
        elif dic[key] > max2:
            max2 = dic[key]
            max2_index = key
    return max1_index, max2_index


def create_circle(points):
    median = [np.median([coor[0] for coor in points]), np.median([coor[1] for coor in points])]
    radius = np.median([cal_distance(median[0], median[1], coor[0], coor[1]) for coor in points])
    distance_matrix = squareform(pdist(points, (lambda u, v: get_distance(u, v))))
    db = DBSCAN(eps=radius, min_samples=2, metric='precomputed')
    cluster = db.fit_predict(distance_matrix)
    is_in_cluster = [i for i in range(len(cluster)) if cluster[i] != -1]
    useful_points = [points[i] for i in is_in_cluster]
    center = [np.mean([coor[0] for coor in useful_points]), np.mean([coor[1] for coor in useful_points])]
    radius = np.max([cal_distance(center[0], center[1], coor[0], coor[1]) for coor in useful_points])
    return center, radius


def cal_velocity(lon1, lat1, lon2, lat2, delat_time):
    if check(lat1, lon1, lat2, lon2):
        dis = geodesic((lat1, lon1), (lat2, lon2)).km  # 单位为千米
        time = delat_time / np.timedelta64(1, 'D') * 24  # 单位为小时
        velocity = -1
        if time != 0:
            velocity = dis / time
        return velocity
    else:
        return -1


class DouglasPeuker:
    "Douglas–Peucker algorithm压缩轨迹"
    def douglasPecker(self, coordinate, dMax):
        """
        :param coordinate: 原始轨迹
        :param dMax: 允许最大距离误差
        :return: douglasResult 抽稀后的轨迹
        """
        self.df = coordinate
        cor_with_index = [[i, x[0], x[1]] for i, x in enumerate(coordinate)]
        result = self.compressLine(cor_with_index, [], 0, len(cor_with_index) - 1, dMax)
        result.append(0)
        result.append(len(cor_with_index) - 1)
        result.sort()
        return result

    def compressLine(self, coordinate, result, start, end, dMax):
        "递归方式压缩轨迹"
        if start < end:
            maxDist = 0
            currentIndex = 0
            startPoint = coordinate[start][1:]
            endPoint = coordinate[end][1:]
            for i in range(start + 1, end):
                currentDist = self.disToSegment(startPoint, endPoint, coordinate[i][1:])
                if currentDist > maxDist:
                    maxDist = currentDist
                    currentIndex = i
            if maxDist >= dMax or self.df['Velocity'][currentIndex] < 1.5:
                # 将当前点的index加入到过滤数组中
                result.append(currentIndex)
                # 将原来的线段以当前点为中心拆成两段，分别进行递归处理
                self.compressLine(coordinate, result, start, currentIndex, dMax)
                self.compressLine(coordinate, result, currentIndex, end, dMax)
        return result

    def disToSegment(self, start, end, center):
        "计算垂距，用海伦公式计算面积"
        a = distance(start, end)
        b = distance(start, center)
        c = distance(end, center)
        p = (a + b + c) / 2
        s = np.sqrt(abs(p * (p - a) * (p - b) * (p - c)))
        return s * 2 / a


def similarity_of_time(df1, df2):
    time1 = list(df1.Date_Time)
    time2 = list(df2.Date_Time)
    time1_begin = datetime.datetime.combine(datetime.date.today(), time1[0].time())
    time1_end = datetime.datetime.combine(datetime.date.today(), time1[-1].time())
    time2_begin = datetime.datetime.combine(datetime.date.today(), time2[0].time())
    time2_end = datetime.datetime.combine(datetime.date.today(), time2[-1].time())
    left = max(time1_begin, time2_begin)
    right = min(time1_end, time2_end)
    whole_time = max(time1_end, time2_end) - min(time1_begin, time2_begin)
    if left > right:
        return -(left - right) / whole_time
    else:
        return (right - left) / whole_time


def similarity_of_dis(df1, df2):
    coor1 = [[df1.Latitude[i], df1.Longitude[i]] for i in range(len(df1))]
    coor2 = [[df2.Latitude[i], df2.Longitude[i]] for i in range(len(df2))]
    dis = similaritymeasures.frechet_dist(coor1, coor2)
    return dis


def is_neighbor(df1, df2, time_min_threshold=-0.1, dis_max_threshold=0.003):
    if similarity_of_time(df1, df2) < time_min_threshold:
        return False
    return similarity_of_dis(df1, df2) < dis_max_threshold