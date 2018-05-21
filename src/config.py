import os

hitter_basic = False

if 'USER' in os.environ:
    SYSTEM_ENV = 'SERVER'
else:
    SYSTEM_ENV = 'LOCAL'

if SYSTEM_ENV == 'LOCAL':
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = 'lab2ai64'
    DB_NAME = 'baseball'
    DB_PORT = 3307
else:
    DB_HOST = 'myrds.cqqe2lakgloq.ap-northeast-2.rds.amazonaws.com'
    DB_USER = 'lab2ai'
    DB_PASSWORD = 'lab2ailab2ai'
    DB_NAME = 'baseball'
    DB_PORT = 3306

LOG_FOLDER = './log/'
DEBUG_LOG_FILENAME = 'test_log.txt'
RUN_LOG_FILENAME = 'run_log.txt'

RUN_MODE = 'DEBUG'  # 'RUN'

VERSION_LEVEL = 0  # 0 (SKT 옥수수), 1 (해설자)
SLEEP_TIME = 0

# 쿼리 load path 설정
current_path = os.getcwd().split('\\')
RUN_PATH = None
if current_path[-1] == 'lib':
    RUN_PATH = 'TEST'

GAME_LIST = ['20170914SKOB0', '20170926HHLT0', '20170912OBNC0', '20170609SSHH0']  #
    
# Google Sheet 정보
GSHEET_DICT = {
  "type": "service_account",
  "project_id": "coral-inverter-197804",
  "private_key_id": "6509e406439dd0944b11ed01f9895fe5b58dcc22",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDByIJq40xXA0Mv\nhe10ythKM8leaFqiM5CRqWLce4OKCvmVQZqzFEuJKLqhSCvURKAbAd8+Ni63Bz4+\nk8OfiL6KqwUYcLRponqL4L6P61vRPFo+ZU3ncmVoYekIXBVGnCTw2v4eB0qqBZTG\ngkXTWhSfg5eDDciBowaBFS4JVo6bVNR/hUBv7fMQa4vLcdi31KHQ2zYTEzYol83l\nEl3NTXCqCGMZAsNAvmqSV36Ye7uU5YftV7yAf0FPViXzgQ5m3M04V+kfMOuXSlde\nBNXNMWMNWzMJpiOk6mS9O6MTw4E+mbYbeDR57jP5bzctqjIM9i2JJMOn4AegHXrP\nZsolOEvRAgMBAAECggEAHuR39BHN0P5OZuRXJVwUDIpCcyg4MKz/QlVqUwNmxio3\nPSXjA2L8Ir7JN95xTErvajbLb9fD7T48nE3CrStn0uPuMUYAYOm71xJKVte6wLm6\nGkHcoEXSqEgZlhFV+/Z3BiWnRsK7Uq0GmXnZp1awPHjGPeiD2zTR2+C0QN1ZaSYe\nhizfUAFRHgYNGb96chHKZeJp1pj/MSTqBnS2jwMWZymnHn54QyCmMmx8GsiDd+8d\niLnNSp/5XZbl9WtiBho8mlJSjNaw9Z5iGsW0u1ITPXvWZDZj3Vp1Xd0PyQuGzHKb\nzSXrGlTTqCIMmUGNW2c4b92QQO+SjEyQJHKsINV8ZQKBgQD9y/1i8LX1J29Nq2rM\na6UFxRaKYs5pQQhjfAa975WxFfWqfhCB4yoHBuvi4cdSVYV2wyP9+eGlWKcKu+WZ\nTA7Jggk0oV/Y4kbvT0hTC4oSQBs3cHV+5CvC6MhNFHkBOHxV5BeDr7tc1QUO46rY\nfPknayUNY8Rtk5BI0jtZAENJZQKBgQDDdybrfCcWhWIS2H7cxekXTz9oAVQNb3/m\ntFMeDnmUm0HaBHjQEWVu8Vqghy9DLW/ljbl/ugv9I/cKGz4wSFfVAhpSLpSo+DQ9\nytsT+N6TA2McWfWlFXe72aWbJ2zbYi40BnPKYhNH7hSi+tGeWvsJdbBFTTiVOzI5\nP2Y/POsH/QKBgFVPFSwFt1PhXoNgBDUUVdL7rZj0n2c3yecO0IFVoB53QC1/1HKk\ndgMIq4+GzuX5AzSpYVbEgLmAdB2ijQmbTDklsYx0VfBkFu3n22q2rUF3NO7MqWHu\ntlr8vh9Sq13iq8B/O/wyvKr2m42mr023rFQ4qqq2h1dBy7T+nZ5L/VIVAoGBALQa\nO9BLCzEjIaS/utTtvsJtkLziTHI8xJrsmJFfQQN+swSRjkgZX18EID89kHzThwD6\nv2tDH/zVgLDdPUX7woJQd7Q1m2C9olU1bvtOGrdXLaFX+pFr4HFEL+VwREs4gd4J\n+/MEv0NNydIKTc8dgaXLvOl+J57JdpNtKWcnWGB5AoGBALG6jeGUd2c2JIpOEPPK\nW9JnBYSqlJk+yxS5XCHQq/7gNFbCc3FEWXSfhSaeG+QGtxo9u+Z2V2Y3qzBCMktO\nI1IAUPnJv95wAJuWNSf4blHOKxPemtKOafjxDoSPZJrQDBQXv5zN0/2ySYco7D+6\n/C1QhOvaci+qbF5fq74w3IKE\n-----END PRIVATE KEY-----\n",
  "client_email": "lab2ai@coral-inverter-197804.iam.gserviceaccount.com",
  "client_id": "102141783558926477928",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://accounts.google.com/o/oauth2/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/lab2ai%40coral-inverter-197804.iam.gserviceaccount.com"
}

    

# 연습
    
from collections import defaultdict
import pprint
from korean import l10n

def tree():
    return defaultdict(tree)

def add(t, path):
    for node in path:
        t = t[node]

def dicts(t):
    return {k: dicts(k) for k in t}

# data_list = ['민병헌 선수,| 지난 시즌까지 |{}기록하고 있습니다.|2시즌 연속 |150 안타 ','민병헌 선수,| 지난 시즌까지 |{}기록하고 있습니다.|2시즌 연속 |10 홈런', '민병헌 선수,| 지난 시즌까지 |{}기록하고 있습니다.|5시즌 연속 |10 도루']

data_list = ['민병헌 선수, {}|지난 시즌까지 {}|{}을(를) 기록하고 있습니다.|3시즌 연속 {},|150안타',
                        '민병헌 선수, {}|지난 시즌까지 {}|{}을(를) 기록하고 있습니다.|2시즌 연속 {},|10홈런',
                        '민병헌 선수, {}|지난 시즌까지 {}|{}을(를) 기록하고 있습니다.|2시즌 연속 {},|10도루',
                        '민병헌 선수, {}|올 시즌 {}|{}에 올라 있습니다.|2루타 40개로 현재 2위',
                        '민병헌 선수, {}|올 시즌 {}|{}에 올라 있습니다.|타율 0.366으로 현재 8위',
                        '민병헌 선수, {}|올 시즌 {}|{}을(를) 기록합니다.|2시즌 연속 {}|150안타',
                        '민병헌 선수, {}|지난 시즌까지 {}|{}을(를) 기록하고 있습니다.|5시즌 연속 {},|안타',
                        '민병헌 선수, {}|지난 시즌까지 {}|{}을(를) 기록하고 있습니다.|3시즌 연속 {},|홈런',
                        '민병헌 선수, {}|지난 시즌까지 {}|{}을(를) 기록하고 있습니다.|3시즌 연속 {},|타점']

s_list = []
data = tree()

for s in data_list:
    add(data, s.split('|'))

def get_msg(d):
    temp_list = []
    join_flag = False
    for k, v in d.items():
        if len(v) == 0:
            temp_list.append(k)
            join_flag = True
        else:
            temp_list.append(k.format(get_msg(v)))
            join_flag = False
    if join_flag:
        temp = ', '.join(temp_list)
    else:
        if temp_list[-1][-1] == ',':
            temp_list[-1] = temp_list[-1][:-1]
        temp = ' '.join(temp_list)
    return temp

def get_msg_v0(d):
    temp_list = []
    for k, v in d.items():
        if len(v) == 0:
            temp_list.append(k)
        else:
            temp_list.append(k.format(get_msg(v)))
    if temp_list[0][-1] != '.':
        temp = ', '.join(temp_list)
    else:
        temp = ' '.join(temp_list)
    return temp

t = get_msg(data)
t = l10n.proofread(t)
# print(t)
