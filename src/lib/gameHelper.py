from lib import DBConnection as db
from lib import casterq
from lib import record
from enum import Enum
from math import exp
import korean
import random
import time

class GameHelper(object):
    # Setting Mysql Connector
    def __init__(self):
        self.MySqlHost = 'localhost'
        self.MySqlUser = 'root'
        self.MySqlPw = 'lab2ai64'
        self.MySqlDB = 'baseball'
        self.MySqlPort = 3307
        self.LiveData = None
        self.CondTuple = None
        self.curr_away_score = 0 # 원정팀 현재 점수
        self.curr_home_score = 0 # 홈팀 현재 점수
        self.prev_away_score = 0  # 원정팀 현재 점수
        self.prev_home_score = 0  # 홈팀 현재 점수
        self.game_event = None
        self.caster_queue = casterq.CasterQueue()
        self.prev_pitcher = None
        self.prev_hitter = None
        self.catg_score ={}
        self.get_cond_dict()
        self.get_catg_score()
        # TEST 를 위한 변수
        self.currRowNum = 0

    def get_cond_dict(self):
        db_my_conn = db.MySqlConnector(host=self.MySqlHost, port=self.MySqlPort, user=self.MySqlUser, pw=self.MySqlPw, db=self.MySqlDB)
        query = "select EVENT, CONDITIONS from baseball.event_cond"
        self.CondTuple = db_my_conn.select(query, True)

    # 이벤트 카테고리 별 점수
    def get_catg_score(self):
        db_my_conn = db.MySqlConnector(host=self.MySqlHost, port=self.MySqlPort, user=self.MySqlUser, pw=self.MySqlPw,
                                       db=self.MySqlDB)
        query = "select category, score from baseball.catg_score"
        rows = db_my_conn.select(query, True)
        self.catg_score = {row["category"]: row["score"] for row in rows}

    # 이번 시즌 투수 기록
    def get_df_season_pitcher_record(self, pitcher):
        result = {}
        df_pitcher = record.get_df_season_pitcher_record(pitcher)
        if len(df_pitcher) > 0:
            pitcher_dict = df_pitcher.to_dict()
            for key, value in pitcher_dict.items():
                result.update({key: value[pitcher]})
            return result
        else:
            return {}

    # 이번 시즌 타자 기록
    def get_df_season_hitter_record(self, hitter):
        result = {}
        df_hitter = record.get_df_season_hitter_record(hitter)
        if len(df_hitter) > 0:
            hitter_dict = df_hitter.to_dict()
            for key, value in hitter_dict.items():
                result.update({key: value[hitter]})
            return result
        else:
            return {}

    # 이번 시즌 투수상대 타자 기록
    def get_df_season_bitter_vs_pitcher(self, hitter, pitcher):
        result = {}
        df_hitterVspitcher = record.get_df_season_hitter_vs_pitcher(hitter, pitcher)
        if len(df_hitterVspitcher) > 0:
            hitter_dict = df_hitterVspitcher.to_dict()
            for key, value in hitter_dict.items():
                result.update({key: value[hitter]})
            return result
        else:
            return {}

    # 실시간 데이터를 가져온다.
    def get_live_data(self):
        db_my_conn = db.MySqlConnector(host=self.MySqlHost, port=self.MySqlPort, user=self.MySqlUser, pw=self.MySqlPw, db=self.MySqlDB)
        query = "select * from baseball.livetext_score_mix order by seqNo limit 1"
        self.LiveData = db_my_conn.select(query, True)[0]
        return self.LiveData

    # Live가 아닌 Local Test를 위한 함수. getLiveData()로 대체될 것.
    def test_live_data(self, gameid):
        db_my_conn = db.MySqlConnector(host=self.MySqlHost, port=self.MySqlPort, user=self.MySqlUser, pw=self.MySqlPw, db=self.MySqlDB)
        query = "SELECT (SELECT NAME FROM baseball.person WHERE A.pitcher = PCODE) AS PITCHER_NAME "\
                       ", (SELECT NAME FROM baseball.person WHERE A.batter = PCODE) AS batter_name "\
                       ", (SELECT NAME FROM baseball.person WHERE A.catcher = PCODE) AS catcher_name "\
                       ", (SELECT NAME FROM baseball.person WHERE A.runner = PCODE) AS runner_name "\
                       ", A.* "\
                       "FROM baseball.livetext_score_mix A "\
                       "WHERE A.gameID = '%s' "\
                       "ORDER BY seqNo" % gameid

        self.LiveData = db_my_conn.select(query, True)
        return self.LiveData

    # 무엇을 할 지 결정한다.
    def get_what_info(self, livetext):
        result = {}
        result_condition = {}
        result_pitcher = {}
        result_hitter = {}
        result_hitter_vs_pitcehr = {}

        live_data_dict = self.LiveData[self.currRowNum]
        curr_pitcher = live_data_dict['pitcher']
        curr_hitter = live_data_dict['batter']

        # 투수 정보 설정
        if self.prev_pitcher != curr_pitcher :
            if len(curr_pitcher) > 0:
                self.prev_pitcher = curr_pitcher
                pitcher_dict = self.get_df_season_pitcher_record(curr_pitcher) # 이번 시즌 투수 기록
                if pitcher_dict:
                    result_pitcher.update({'event_type': 'pitcher_season_record'})
                    result_pitcher.update(pitcher_dict)

        # 타자 설정
        if self.prev_hitter != curr_hitter:
            if len(curr_hitter) > 0:
                self.prev_hitter = curr_hitter
                # 이번 시즌 타자 기록
                hitter_dict = self.get_df_season_hitter_record(curr_hitter)
                if hitter_dict:
                    result_hitter.update({'event_type': 'hitter_on_mound'})
                    result_hitter.update(hitter_dict)

                # 이번 시즌 타자 vs 투수 기록
                hitter_vs_pitcher_dict = self.get_df_season_bitter_vs_pitcher(curr_hitter, curr_pitcher)
                if hitter_vs_pitcher_dict:
                    result_hitter_vs_pitcehr.update({'event_type': 'hitter_on_mound'})
                    result_hitter_vs_pitcehr.update(hitter_vs_pitcher_dict)

        word_list = livetext.split()

        # 게임중 나타나는 이벤트 설정
        for condDict in self.CondTuple:
            if condDict['EVENT'] in word_list:
                self.game_event = condDict['EVENT']
                cond_list = condDict['CONDITIONS'].split(',')
                for cond in cond_list:
                    method = getattr(self, cond)
                    t_dict = method()
                    if t_dict:
                        result_condition.update(t_dict)

        if result_pitcher:
            result.update({'pitcher_info': result_pitcher})
        if result_hitter:
            result.update({'hitter_info': result_hitter})
        if result_hitter_vs_pitcehr:
            result.update({'hitter_vs_pitcher_info': result_hitter_vs_pitcehr})
        if result_condition:
            result.update({'condition_info': result_condition})

        return result

    def make_sentence(self, data):
        class HREnum(Enum):
            BASE_STATE, score_state, HR_CN, HR, RUN = range(1, 6)

        class HMEnum(Enum):
            RBI, BB, SB, H2, HIT, HR, KK, HRA  = range(1, 9)

        class HVSPEnum(Enum):
            HR_CN, HIT_CN, H2_CN, BB_CN = range(1, 5)

        hr_dict = {'BASE_STATE': ['NAME', 'BASE_STATE'], 'HR_CN': ['PITCHER_NAME', 'HR_CN'], 'HR': ['NAME','HR'], 'RUN': ['RUN']}

        for key, value_dict in data.items():
            msg_list = []
            event_type = value_dict['event_type']
            # 홈런 상황
            if event_type == '홈런':
                for hr_key, hr_values in hr_dict.items():
                    if hr_key in value_dict:
                        if value_dict[hr_key] is None:
                            continue

                        msg_code = 'HR%02dL0%02d' % (getattr(HREnum, hr_key).value, random.randrange(0, 2))
                        db_my_conn = db.MySqlConnector(host=self.MySqlHost, port=self.MySqlPort, user=self.MySqlUser,
                                                       pw=self.MySqlPw,
                                                       db=self.MySqlDB)
                        query = "SELECT MSG FROM baseball.castermsg_mas WHERE CODE = '%s' limit 1" % msg_code
                        template = db_my_conn.select(query, True)[0]

                        msg_value = {}
                        for v in hr_values:
                            msg_value.update({v: value_dict[v]})

                        msg = korean.l10n.Template(template['MSG']).format(**msg_value)
                        msg_list.append([0.5, msg])
                self.put_queue(msg_list)

            elif event_type == '홈인':
                print("캐스터: " + '홈인!')

            # 투수 등판 시
            elif event_type == 'pitcher_season_record':
                print("캐스터: ",  value_dict)

            # 타자 등판 시
            elif event_type == 'hitter_on_mound':
                # 타자 정보
                if key is 'hitter_info':
                    for hm_key, hm_value in value_dict.items():
                        if hm_value == 0:
                            continue

                        if hm_key in HMEnum.__members__:
                            msg_code = 'HM%02dL0%02d' % (getattr(HMEnum, hm_key).value, random.randrange(0, 2))
                            db_my_conn = db.MySqlConnector(host=self.MySqlHost, port=self.MySqlPort,
                                                           user=self.MySqlUser,
                                                           pw=self.MySqlPw,
                                                           db=self.MySqlDB)
                            query = "SELECT MSG FROM baseball.castermsg_mas WHERE CODE = '%s' limit 1" % msg_code
                            template = db_my_conn.select(query, True)[0]

                            msg = korean.l10n.Template(template['MSG']).format(**value_dict)
                            value = self.score_generator(hm_key, value_dict)
                            msg_list.append([value, msg])

                    if len(msg_list) > 0:
                        self.put_queue(msg_list)

                # 타자와 투수 대결 정보
                elif key is 'hitter_vs_pitcher_info':
                    for hvsp_key, hvsp_value in value_dict.items():
                        if hvsp_value == 0:
                            continue

                        if hvsp_key in HVSPEnum.__members__:
                            msg_code = 'VS%02dL0%02d' % (getattr(HVSPEnum, hvsp_key).value, random.randrange(0, 1))
                            db_my_conn = db.MySqlConnector(host=self.MySqlHost, port=self.MySqlPort,
                                                           user=self.MySqlUser,
                                                           pw=self.MySqlPw,
                                                           db=self.MySqlDB)
                            query = "SELECT * FROM baseball.castermsg_mas WHERE CODE = '%s' limit 1" % msg_code
                            template = db_my_conn.select(query, True)[0]

                            msg = korean.l10n.Template(template['MSG']).format(**value_dict)
                            value = self.score_generator(hvsp_key, value_dict)
                            msg_list.append([value, msg])

                    if len(msg_list) > 0:
                        self.put_queue(msg_list)

                # 주자 상황에 따른 타자 정보
                elif key is 'on_base_info':
                    print('주자 상황')

                # 점수차 상황에 따른 타자 정보
                elif key is 'score_gap_info':
                    print('점수차')

                # 점수차와 주자 상황에 따른 타자 정보
                elif key is 'score_base_info':
                    print('점수차와 주자상황')

    def put_queue(self, msg):
        data = msg
        self.caster_queue.put(data)
        self.caster_queue.sort()

    def get_queue(self):
        while True:
            if self.caster_queue.size() > 0:
                sentence = self.caster_queue.get()[1]
                if sentence:
                    print("캐스터: " + sentence)
                    time.sleep(0.01*len(sentence))
                    self.caster_queue.decrease_q(0.01)


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

        return {'score_state': score_state, 'score_state_name': score_state_name}

    # [HR]득점 종류: 안타,홈런,희생FL,실책,내야 땅볼 등
    def get_kind_score(self):
        return {'event_type': self.game_event}

    # [HR]주자 상황 : no, 1, 1-2or2-3, 1-2-3
    # return 1, 2, 3, 4
    def get_base_state(self):
        live_data_dict = self.LiveData[self.currRowNum]
        count = 1
        base_list = ['base1', 'base2', 'base3']

        for s in base_list:
            if live_data_dict[s] > 0:
                count += 1
        return {'BASE_STATE': count}

    # [HR]리그 종류와 시즌에 대한 선수 기록
    def get_player_league(self):
        live_data_dict = self.LiveData[self.currRowNum]
        db_my_conn = db.MySqlConnector(host=self.MySqlHost, port=self.MySqlPort, user=self.MySqlUser, pw=self.MySqlPw, db=self.MySqlDB)
        query = "select * " \
                " from baseball.battotal " \
                "where PCODE = '%s' " \
                "and GYEAR = %s " \
                "limit 1"
        if self.game_event == '홈런':
            batter = live_data_dict['batter']
            name = live_data_dict['batter_name']
        elif self.game_event == '홈인':
            batter = live_data_dict['runner']
            name = live_data_dict['runner_name']
        else:
            batter = live_data_dict['batter']
            name = live_data_dict['batter_name']

        query = query % (batter, live_data_dict['GYEAR'])
        data = db_my_conn.select(query, True)[0]
        result = {'RUN': data['RUN'], 'HR': data['HR'], 'HRA': data['HRA'], 'GAMENUM': data['GAMENUM'],
                  'AB': data['AB'], 'HIT': data['HIT'], 'PITCHER_NAME': live_data_dict['PITCHER_NAME'], 'NAME': name}
        return result

    # WPA 정보 - currWPA(후), prevWPA(전), varWAP(변화)
    def get_wpa(self):
        live_data_dict = self.LiveData[self.currRowNum]
        db_my_conn = db.MySqlConnector(host=self.MySqlHost, port=self.MySqlPort, user=self.MySqlUser, pw=self.MySqlPw, db=self.MySqlDB)
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
        pitcher = live_data_dict['pitcher']
        hitter = live_data_dict['batter']

        return self.get_df_season_bitter_vs_pitcher(hitter, pitcher)

    # 메시지 점수 계산, list: 계산할 카테고리, dict: 해당 값
    def score_generator(self, mkey, dict):
        rank_score = 0.1
        m_key = mkey.split('_')[0]

        if (m_key+'_RNK') in dict:
            rank_score = round(0.5 - (dict.get(m_key+'_RNK') / 200), 3)

        if mkey in self.catg_score:
            catg_score_val = self.catg_score.get(mkey)

        result = round(self.get_new_sigmoid(rank_score + catg_score_val/2), 3)

        return result

    # 변경된 Sigmoid 함수 return -0.49 ~ 0.99
    def get_new_sigmoid(self, x):
        return 1 / (0.667 + exp(-10*x + 5)) - 0.5

