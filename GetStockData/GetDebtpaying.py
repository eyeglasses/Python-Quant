# -*- coding=utf-8 -*-
# 获取偿债能力

import tushare as ts
import uuid
from sqlalchemy import create_engine
import cx_Oracle as cxo
import configparser
import pandas


def getConfig():
    cf = configparser.ConfigParser()
    cf.read("config.conf")
    oracleHost = str(cf.get("oracle", "ip"))
    oraclePort = int(cf.get("oracle", "port"))
    oracleUser = str(cf.get("oracle", "username"))
    oraclePassword = str(cf.get("oracle", "password"))
    oracleDatabaseName = str(cf.get("oracle", "databasename"))
    oracleConn = oracleUser + '/' + oraclePassword + '@' + oracleHost + '/' + oracleDatabaseName
    conn = cxo.connect(oracleConn)
    cursor = conn.cursor()
    print("已获取数据库连接")
    return cursor

# 检查表中是否存在数据
def haveData(cursor):
    cursor.execute("select count(1) from stock_debtpaying")
    pdata = cursor.fetchone()
    return pdata[0]


def getDebtpaying(cursor):
    for i in range(1992, 2017+1):
        for j in range(1, 4+1):
            try:
                print(i, j)
                df = ts.get_debtpaying_data(i, j)

                # 处理缺失值
                df = df.stack().replace('--', '0').unstack()

                dfLen = len(df)
                # print(dfLen)
                uuidList = []  # 添加uuid
                yearList = []  # 添加年份
                quarterList = []  # 添加季度
                for l in range(0, dfLen):
                    uuidList.append(uuid.uuid1())
                    yearList.append(str(i))
                    quarterList.append(str(j))
                df['uuid'] = uuidList
                df['year'] = yearList
                df['quarter'] = quarterList

                cursor = getConfig()
                for k in range(0, dfLen):
                    df2 = df[k:k+1]

                    cursor.execute("insert into stock_debtpaying(uuid, code, name, currentratio, quickratio, cashratio, "
                               "icratio, sheqratio, adratio, year, quarter) "
                               "values(:uuid, :code, :name, :currentratio, :quickratio, :cashratio, "
                               ":icratio, :sheqratio, :adratio, :year, :quarter)",
                               (str(list(df2['uuid'])[0]), str(list(df2['code'])[0]), str(list(df2['name'])[0]), round(float(df2['currentratio']), 4),
                                round(float(df2['quickratio']), 4), round(float(df2['cashratio']), 4),
                                round(float(df2['icratio']), 4), round(float(df2['sheqratio']), 4), round(float(df2['adratio']), 4),
                                str(list(df2['year'])[0]), str(list(df2['quarter'])[0])) )
                cursor.execute("commit")
            except Exception:
                pass


def main():
    cursor = getConfig()
    pdata = haveData(cursor)
    if pdata == 0:
        getDebtpaying(cursor)
    else:
        cursor.execute("truncate table stock_debtpaying")
        print("发现数据，清除完毕")
        getDebtpaying(cursor)

    # df = ts.get_debtpaying_data(1994, 2)
    # print(df['currentratio'][0])
    # if '--' in df['currentratio']:
    #     print(1)
    # df['currentratio'].replace('--', 0)
    # df = df.stack().replace('--', '0').unstack()
    # print(df)




if __name__ == '__main__':
    main()