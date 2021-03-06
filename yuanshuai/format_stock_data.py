import pandas as pd
from pandas import DataFrame, Series
import get_stock_data as gsd
import uuid
import time


def format_data(raw_data):
    """
    处理数据
    :param raw_data:
    :return:
    """
    data = raw_data[0]
    code = raw_data[1]
    data['code'] = code
    data['name'] = gsd.get_name(code)
    data['classify'] = gsd.get_type(code)
    # 添加一些列
    data = DataFrame(data, columns=['uuid', 'date', 'code', 'name', 'classify', 'open', 'close', 'high', 'low', 'volume', 'amount', \
                                    'y_close', 'p_change', 'p_change_rate'])
    close_p = data['close']  # 收盘
    data['y_close'] = close_p.shift(-1)  # 昨收盘
    for i in data.index:
        data.loc[i, 'date'] = i.to_datetime().strftime('%Y-%m-%d')  # date
        data.loc[i, 'uuid'] = str(uuid.uuid1()) + "_" + data.loc[i, 'date']  # uuid
        # data.code = code  # 股票代码
        data.loc[i, 'p_change'] = data.loc[i, 'close'] - data.loc[i, 'y_close']  # 涨跌额
        data.loc[i, 'p_change_rate'] = data.loc[i, 'p_change'] / data.loc[i, 'y_close']  # 涨跌幅
        i = data.loc[i, 'uuid']
    return data


def main():
    raw_data = gsd.get_data('000001')
    data = format_data(raw_data)
    print(data)


if __name__ == '__main__':
    main()

