import numpy as np
import datetime

zero_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,0, 0, 0)
one_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,1, 0, 0)
two_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,2, 0, 0)
three_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,3, 0, 0)
four_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,4, 0, 0)
five_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,5, 0, 0)
six_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,6, 0, 0)
seven_colock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,7, 0, 0)
eight_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,8, 0, 0)
nine_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,9, 0, 0)
ten_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,10, 0, 0)
eleven_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,11, 0, 0)
tw_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,12, 0, 0)
thirt_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,13, 0, 0)
ft_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,14, 0, 0)
fivt_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,15, 0, 0)
st_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,16, 0, 0)
sevt_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,17, 0, 0)
et_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,18, 0, 0)
nit_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,19, 0, 0)
twty_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,20, 0, 0)
tw_1_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,21, 0, 0)
tw_2_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,22, 0, 0)
tw_3_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,23, 0, 0)
tw_4_clock = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day + 1,0, 0, 0)

clocks_list = \
    [zero_clock, one_clock, two_clock, three_clock, four_clock,five_clock, six_clock, seven_colock, eight_clock,
     nine_clock, ten_clock, eleven_clock, tw_clock, thirt_clock, ft_clock, fivt_clock, st_clock, sevt_clock, et_clock,
     twty_clock, tw_1_clock, tw_2_clock, tw_3_clock, tw_4_clock]


def cal_time(time1, time2):
    delta_t = time2 - time1
    return delta_t/np.timedelta64(1, 'D') * 24 * 60


def cal_days(df):
    days = set()
    for i in range(len(df)):
        date = df.start_time[i]
        year, month, day = date.year, date.month, date.day
        days.add(f"{year}-{month}-{day}")
    return len(days)


def cal_interest(whole_df, w_times=0.8, w_duration=0.6, m=0.3):
    whole_times = cal_days(whole_df)
    whole_duration = np.sum([cal_time(whole_df.start_time[index], whole_df.end_time[index]) for index in range(len(whole_df))])
    t_min, t_max = whole_df.start_time[0], list(whole_df.end_time)[-1]
    cluster_for_points = {}
    interest_of_cluster = {}
    clusters = list(set(whole_df.cluster))
    for c in clusters:
        tmp_df = whole_df[whole_df['cluster']==c]
        tmp_df.reset_index(drop=True, inplace=True)
        cluster_for_points[c] = tmp_df
        times = cal_days(tmp_df)
        print(c, times)
        duration = np.sum([cal_time(tmp_df.start_time[i], tmp_df.end_time[i]) for i in range(len(tmp_df))])
        interest = w_times * times / whole_times + w_duration * duration / whole_duration
        interest = interest * (m * (list(tmp_df.end_time)[-1] - t_min) / (t_max - t_min) + 1 - m)
        interest_of_cluster[c] = interest
    return interest_of_cluster, cluster_for_points


def create_time_hist(df):
    time_hist = np.zeros((7, 24))
    for i in range(len(df)):
        start_time = df.start_time[i]
        end_time = df.end_time[i]
        start = datetime.datetime(start_time.year,start_time.month,start_time.day,start_time.hour, 0, 0)
        end = datetime.datetime(end_time.year,end_time.month,end_time.day,end_time.hour, 0, 0)
        while start <= end:
            current = 0
            while start.time() > clocks_list[current].time():
                current += 1
            day = datetime.datetime.weekday(start)
            time_hist[day][current - 1] += 1
            if start.hour == 23:
                start = start.replace(hour=0, day=start.day+1)
            else:
                start = start.replace(hour=start.hour+1)
    return time_hist


def cal_var(df):
    c = create_time_hist(df)
    c_list = np.sum(c, axis=1)
    std = np.std(c_list)
    var = std / np.mean(c_list)
    return var
