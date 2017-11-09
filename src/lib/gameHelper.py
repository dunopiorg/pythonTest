from lib import DBConnection as db
from enum import Enum
import  random

class GameHelper():
    # Setting Mysql Connector
    def __init__(self):
        self.MySqlHost = 'localhost'
        self.MySqlUser = 'root'
        self.MySqlPw = '0000'
        self.MySqlDB = 'baseball'
        self.LiveData = None
        self.CondTuple = None
        self.set_cond_dict()
        self.curr_away_score = 0 # 원정팀 현재 점수
        self.curr_home_score = 0 # 홈팀 현재 점수
        self.prev_away_score = 0  # 원정팀 현재 점수
        self.prev_home_score = 0  # 홈팀 현재 점수
        self.game_event = None
        # TEST 를 위한 변수
        self.currRowNum = 0

    def set_cond_dict(self):
        db_my_conn = db.MySqlConnector(host=self.MySqlHost, user=self.MySqlUser, pw=self.MySqlPw, db=self.MySqlDB)
        query = "select EVENT, CONDITIONS from baseball.event_cond"
        self.CondTuple = db_my_conn.select(query, True)

    def get_live_data(self):
        db_my_conn = db.MySqlConnector(host=self.MySqlHost, user=self.MySqlUser, pw=self.MySqlPw, db=self.MySqlDB)
        query = "select * from baseball.livetext_score_mix order by seqNo limit 1"
        self.LiveData = db_my_conn.select(query, True)[0]
        return self.LiveData

    # Live가 아닌 Local Test를 위한 함수. getLiveData()로 대체될 것.
    def test_live_data(self, gameid):
        db_my_conn = db.MySqlConnector(host=self.MySqlHost, user=self.MySqlUser, pw=self.MySqlPw, db=self.MySqlDB)
        query = "SELECT (SELECT NAME FROM baseball.person WHERE A.pitcher = PCODE) AS pitcherNm "\
                       ", (SELECT NAME FROM baseball.person WHERE A.batter = PCODE) AS batterNm "\
                       ", (SELECT NAME FROM baseball.person WHERE A.catcher = PCODE) AS catcherNm "\
                       ", (SELECT NAME FROM baseball.person WHERE A.runner = PCODE) AS runnerNm "\
                       ", A.* "\
                       "FROM baseball.livetext_score_mix A "\
                       "WHERE A.gameID = '%s' "\
                       "ORDER BY seqNo" % gameid

        self.LiveData = db_my_conn.select(query, True)
        return self.LiveData

    def get_what_info(self, livetext):
        result = {}
        live_data_dict = self.LiveData[self.currRowNum]
        word_list = livetext.split()

        for condDict in self.CondTuple:
            if condDict['EVENT'] in word_list:
                self.game_event = condDict['EVENT']
                cond_list = condDict['CONDITIONS'].split(',')
                for cond in cond_list:
                    method = getattr(self, cond)
                    t_dict = method()
                    if t_dict:
                        result.update(t_dict)

        return result

    def make_sentence(self, data):
        class HREnum(Enum):
            baseState, scoreState, HR_CN, HR, RUN = range(1, 6)
        hr_dict = {'baseState': ['name', 'baseState'], 'HR_CN': ['pitcher_name', 'HR_CN'], 'HR': ['name','HR'], 'RUN': ['RUN']}
        hi_list = [{'RUN': ['RUN']}]

        live_data_dict = self.LiveData[self.currRowNum]
        curr_wpa = None
        msg_code = None
        msg_list = []
        if 'currWPA' in data:
            curr_wpa = data['currWPA']

        if data['kindOfScore'] == '홈런':
            for hr_key, hr_values in hr_dict.items():
                if hr_key in data:
                    if data[hr_key] is None:
                        continue
                    msg_code = 'HR%02d%02d' % (getattr(HREnum, hr_key).value, random.randrange(0, 1))
                    db_my_conn = db.MySqlConnector(host=self.MySqlHost, user=self.MySqlUser, pw=self.MySqlPw,
                                                   db=self.MySqlDB)
                    query = "SELECT * FROM baseball.castermsg_mas WHERE CODE = '%s' limit 1" % msg_code
                    template = db_my_conn.select(query, True)[0]

                    msg_value = ()
                    for v in hr_values:
                        msg_value += (data[v],)

                    msg = template['MSG'] % (msg_value)
                    msg_list.append(msg)
            return msg_list

        elif data['kindOfScore'] == '홈인':
            print("캐스터: " + '홈인!')

    """ 이하 Activation Functions """
    # [HR]점수차 변화 : 도망(1), 추격(1), 동점(2), 리드(3), 역전(4)
    def get_score_status(self):
        live_data_dict = self.LiveData[self.currRowNum]
        score_state = None
        score_state_name = None

        if live_data_dict['bTop'] == 1:
            self.prev_away_score = self.curr_away_score
            self.curr_away_score += 1
        else:
            self.prev_home_score = self.curr_home_score
            self.curr_home_score += 1

        if self.prev_away_score == 0 and self.prev_home_score == 0:
            score_state = 3
            score_state_name = '리드'
        elif self.curr_away_score == self.curr_home_score:
            score_state = 3
            score_state_name = '동점'
        elif self.prev_away_score == self.prev_home_score:
            score_state = 5
            score_state_name = '역전'
        elif self.curr_away_score > self.curr_home_score:
            if self.prev_away_score > self.prev_home_score and live_data_dict['bTop'] == 1:
                score_state = 1
                score_state_name = '도망'
            else:
                score_state = 1
                score_state_name = '추격'
        elif self.curr_away_score < self.curr_home_score:
            if self.prev_away_score < self.prev_home_score and live_data_dict['bTop'] == 0:
                score_state = 1
                score_state_name = '도망'
            else:
                score_state = 1
                score_state_name = '추격'

        return {'scoreState': score_state, 'scoreStateNm': score_state_name}

    # [HR]득점 종류: 안타,홈런,희생FL,실책,내야 땅볼 등
    def get_kind_score(self):
        return {'kindOfScore': self.game_event}

    # [HR]주자 상황 : no, 1, 1-2or2-3, 1-2-3
    # return 1, 2, 3, 4
    def get_base_state(self):
        live_data_dict = self.LiveData[self.currRowNum]
        count = 1
        base_list = ['base1', 'base2', 'base3']

        for s in base_list:
            if live_data_dict[s] > 0:
                count += 1
        return {'baseState': count}

    # [HR]리그 종류와 시즌에 대한 선수 기록
    def get_player_league(self):
        live_data_dict = self.LiveData[self.currRowNum]
        db_my_conn = db.MySqlConnector(host=self.MySqlHost, user=self.MySqlUser, pw=self.MySqlPw, db=self.MySqlDB)
        query = "select * " \
                " from baseball.battotal " \
                "where PCODE = '%s' " \
                "and GYEAR = %s " \
                "limit 1"
        if self.game_event == '홈런':
            batter = live_data_dict['batter']
            name = live_data_dict['batterNm']
        elif self.game_event == '홈인':
            batter = live_data_dict['runner']
            name = live_data_dict['runnerNm']
        else:
            batter = live_data_dict['batter']
            name = live_data_dict['batterNm']

        query = query % (batter, live_data_dict['GYEAR'])
        data = db_my_conn.select(query, True)[0]
        result = {'RUN': data['RUN'], 'HR': data['HR'], 'HRA': data['HRA'], 'GAMENUM': data['GAMENUM'],
                  'AB': data['AB'], 'HIT': data['HIT'], 'pitcher_name': live_data_dict['pitcherNm'], 'name': name}
        return result

    # WPA 정보 - currWPA(후), prevWPA(전), varWAP(변화)
    def get_wpa(self):
        live_data_dict = self.LiveData[self.currRowNum]
        db_my_conn = db.MySqlConnector(host=self.MySqlHost, user=self.MySqlUser, pw=self.MySqlPw, db=self.MySqlDB)
        query = "select BEFORE_WE_RT, AFTER_WE_RT, WPA_RT " \
                " from baseball.ie_record_matrix " \
                "where GAMEID = '%s' " \
                "and GYEAR = %s " \
                "and SEQNO = %s " \
                "limit 1"
        query = query % (live_data_dict['gameID'], live_data_dict['GYEAR'], live_data_dict['seqNO'])
        result = db_my_conn.select(query, True)[0]
        return {'currWPA': result['AFTER_WE_RT'], 'prevWPA': result['BEFORE_WE_RT'], 'varWAP': result['WPA_RT']}

    # [HR]상대선수와의 기록
    def get_vs_pitcher(self):
        live_data_dict = self.LiveData[self.currRowNum]
        result = {}
        db_my_conn = db.MySqlConnector(host=self.MySqlHost, user=self.MySqlUser, pw=self.MySqlPw, db=self.MySqlDB)
        query = "SELECT * " \
                "FROM baseball.season_hitter_vspitcher " \
                "WHERE GYEAR = %s " \
                "AND pitcher = %s " \
                "AND hitter = %s " \
                "limit 1"
        query = query % (live_data_dict['GYEAR'], live_data_dict['pitcher'], live_data_dict['batter'])
        data = db_my_conn.select(query, True)[0]
        if data:
            result = {'PA_CN': data['PA_CN'], 'AB_CN': data['AB_CN'], 'HR_CN': data['HR_CN'], 'HRA_RT': data['HRA_RT']}

        return result



