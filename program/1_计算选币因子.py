"""
花式网格船队 第1期 | 邢不行 | 2022分享会
author: 邢不行
微信: xbx719
"""
import warnings
from functools import partial
from multiprocessing import cpu_count, Pool
from program.Function import *
from program.Grid_function import *
from program.Facny_grid_func import *

warnings.filterwarnings('ignore')


def select_grid_coin(bench, symbol):
    # symbol = 'BTCST-USDT.csv'
    print(symbol)
    # 过滤的不跑网格的币种，剔除币种名中的usdt、busd等，例如输入BTCST-USDT.csv，输出BTCST
    if symbol.replace('-USDT', '').replace('BUSD', '').replace('.csv', '').replace('.pkl', '') in filters:
        return pd.DataFrame()

    # 读取币种数据,兼容csv格式和pkl格式
    if symbol[-4:] == '.csv':
        df = pd.read_csv(candle_path + symbol, encoding='gbk', parse_dates=['candle_begin_time'], skiprows=1)
    else:  # pkl的数据读取速度优于csv，可以将下载的数据手动改成pkl格式的
        df = pd.read_pickle(candle_path + symbol)

    # 和基准数据merge，补全空值
    df = merge_with_benchmark_for_grid(df, bench)
    if df.empty:
        return pd.DataFrame()

    # exg_dict = {'Spread': 'last'}
    exg_dict = {}
    # 将分钟数据转为日线数据
    df = trans_period_for_grid(df, period, exg_dict=exg_dict)
    # 计算选币因子
    df = cal_factor(df)

    # 删除最后两行数据，因为最后一天是没有数据的，需要删除掉两行数据
    df = df[:-2]

    return df


if __name__ == '__main__':
    # 导入基准数据
    benchmark = import_benchmark_data(candle_path + 'BTC-USDT.%s' % file_type, start='2019-10-01', end=strategy_end,
                                      rul_type='60s')

    # 获取所有币种的数据
    coin_list = os.listdir(candle_path)
    coin_list = [c for c in coin_list if c[-3:] == file_type]  # 只保留csv或者pkl格式的文件

    # 先将固定的参数传入函数,偏函数（Dataframe,类型的参数用偏函数，相对于dict能减小内存开销）
    p_select_grid_coin = partial(select_grid_coin, benchmark)

    # 批量读取K线数据
    start_time = datetime.datetime.now()
    # 并行或串行读取数据
    multiply_process = True
    if multiply_process:
        # 开始并行
        with Pool(max(cpu_count() - 1, 1)) as pool:
            df_list = pool.map(p_select_grid_coin, sorted(coin_list))
    else:
        df_list = []
        for c in coin_list:
            data = p_select_grid_coin(c)
            df_list.append(data)

    all_coin_data = pd.concat(df_list, ignore_index=True)

    # 计算截面因子，例如：xx因子的排名，扩散指标等
    all_coin_data = cal_cross_factor(all_coin_data)
    print(all_coin_data)
    all_coin_data.to_pickle(root_path + f'/data/数据整理/all_coin_factor_data.pkl')
