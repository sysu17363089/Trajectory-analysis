from geog import distance
import numpy as np


class Douglas_Peuker:
    "Douglas–Peucker algorithm压缩轨迹"

    def douglasPecker(self, coordinate, dMax):
        """

        :param coordinate: 原始轨迹
        :param dMax: 允许最大距离误差
        :return: douglasResult 抽稀后的轨迹
        """
        self.df = coordinate
        cor_with_index = [[i, self.df['Latitude'][i], self.df['Longitude'][i]] for i in range(len(self.df))]
        result = self.compressLine(cor_with_index, [], 0, len(cor_with_index)-1, dMax)
        result.append(0)
        result.append(len(cor_with_index) - 1)
        result.sort()
        return result

    def compressLine(self, coordinate, result, start, end, dMax):
        "递归方式压缩轨迹"
        if start<end:
            maxDist = 0
            currentIndex = 0
            startPoint = coordinate[start][1:]
            endPoint = coordinate[end][1:]
            for i in range(start+1, end):
                currentDist = self.disToSegment(startPoint, endPoint, coordinate[i][1:])
                if currentDist>maxDist:
                    maxDist = currentDist
                    currentIndex = i
            if maxDist>=dMax:
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
        p = (a+b+c) / 2
        s = np.sqrt(abs(p*(p-a)*(p-b)*(p-c)))
        return s*2/a


def compress_traj(df, point_with_vel=1.5):
    # 轨迹压缩
    compress_class = Douglas_Peuker()
    compress_traj_index = compress_class.douglasPecker(df, 5)
    for i in range(len(df)):
        if df.Velocity[i] < point_with_vel:
            compress_traj_index.append(i)
    compress_traj_index.sort()
    items = df.iloc[compress_traj_index]
    compress_df = items
    compress_df.reset_index(drop=True, inplace=True)
    return compress_df
