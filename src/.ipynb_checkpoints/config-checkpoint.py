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

GAME_LIST = ['20170914SKOB0', '20170609SSHH0']  # 20170912OBNC0 20170926HHLT0
    
    
    
    
    
    
    
# 연습
    
from collections import defaultdict
import pprint

def tree():
    return defaultdict(tree)

def add(t, path):
    for node in path:
        t = t[node]

def dicts(t):
    return {k: dicts(k) for k in t}

# data_list = ['민병헌 선수,| 지난 시즌까지 |{}기록하고 있습니다.|2시즌 연속 |150 안타 ','민병헌 선수,| 지난 시즌까지 |{}기록하고 있습니다.|2시즌 연속 |10 홈런', '민병헌 선수,| 지난 시즌까지 |{}기록하고 있습니다.|5시즌 연속 |10 도루']

data_list = ['민병헌 선수, {} |지난 시즌까지 {} |{}기록하고 있습니다.|2시즌 연속 {} ,|150 안타',
                        '민병헌 선수, {} |지난 시즌까지 {} |{}기록하고 있습니다.|2시즌 연속 {} ,|10 홈런',
                        '민병헌 선수, {} |지난 시즌까지 {} |{}기록하고 있습니다.|2시즌 연속 {} ,|10 도루',
                        '민병헌 선수, {} |올 시즌 {} |{}에 올라 있습니다.|2루타 40개로 현재 2위',
                        '민병헌 선수, {} |올 시즌 {} |{}에 올라 있습니다.|타율 0.366으로 현재 8위',
                        '민병헌 선수, {} |올 시즌 {} |{}기록합니다.|2시즌 연속 {} |150 안타']

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
# print(t)
