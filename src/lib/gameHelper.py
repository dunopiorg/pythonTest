from datetime import datetime
from math import exp
from lib import DBConnection as db
from lib import casterq
from lib import player
from lib import record
import time
import korean


class GameHelper(object):
    caster_queue = casterq.CasterQueue()
    __HOST = 'localhost'
    __USER = 'root'
    __PASSWORD = 'lab2ai64'
    __DB = 'baseball'
    __PORT = 3307

    # region Initialize 필요한 정보
    def __init__(self):
        # database connection 상수 정보
        self._HOST = 'localhost'
        self._USER = 'root'
        self._PASSWORD = 'lab2ai64'
        self._DB = 'baseball'
        self._PORT = 3307

        # state 상수 정보
        self._HIT = ['H1', 'H2', 'H3', 'HR', 'HI', 'HB']
        self._HR = ['HR']
        self._BB = ['BB', 'IB']
        self._KK = ['KK']

        # test를 위한 변수 (실제 운영시 고쳐야 한다)
        self.live_data = None

        # 기본 전역 변수
        self.curr_away_score = 0  # 원정팀 현재 점수
        self.curr_home_score = 0  # 홈팀 현재 점수
        self.prev_away_score = 0  # 원정팀 이전 점수
        self.prev_home_score = 0  # 홈팀 이전 점수
        self.game_event = None
        self.prev_pitcher = None
        self.prev_hitter = None
        self.curr_hitter = None
        self.curr_pitcher = None
        self.hitter_category_score = {}
        self.pitcher_category_score = {}
        self.common_category_score = {}
        self.game_info = {}
        self.curr_row_num = 0

        # 기본 전역 객체 변수
        self.recorder = record.Record()

        # initialize data
        self.set_category_score()

    def set_category_score(self):
        """
        이벤트 카테고리 별 점수
        :return:  category score dictionary
        """
        db_my_conn = db.MySqlConnector(host=self._HOST, port=self._PORT, user=self._USER, pw=self._PASSWORD,
                                       db=self._DB)
        query = "select subject, category, score from baseball.catg_score"
        rows = db_my_conn.select(query, True)
        self.hitter_category_score = {row["category"]: row["score"] for row in rows if row["subject"] == "HITTER"}
        self.pitcher_category_score = {row["category"]: row["score"] for row in rows if row["subject"] == "PITCHER"}
        self.common_category_score = {row["category"]: row["score"] for row in rows if row["subject"] == "COMMON"}

    def get_live_data(self):
        """
        실시간 데이터를 가져온다.
        :return:
        """
        db_my_conn = db.MySqlConnector(host=self._HOST, port=self._PORT,
                                       user=self._USER, pw=self._PASSWORD, db=self._DB)
        query = "select * from baseball.livetext_score_mix order by seqNo limit 1"
        self.live_data = db_my_conn.select(query, True)[0]
        return self.live_data

    def test_live_data(self, game_id):
        """
        Live가 아닌 Local Test를 위한 함수. getLiveData()로 대체될 것.
        :param game_id:
        :return:
        """
        db_my_conn = db.MySqlConnector(host=self._HOST, port=self._PORT,
                                       user=self._USER, pw=self._PASSWORD, db=self._DB)
        query = "SELECT (SELECT NAME FROM baseball.person WHERE A.pitcher = PCODE) AS PITCHER_NAME " \
                ", (SELECT NAME FROM baseball.person WHERE A.batter = PCODE) AS batter_name " \
                ", (SELECT NAME FROM baseball.person WHERE A.catcher = PCODE) AS catcher_name " \
                ", (SELECT NAME FROM baseball.person WHERE A.runner = PCODE) AS runner_name " \
                ", A.* " \
                "FROM baseball.livetext_score_mix A " \
                "WHERE A.gameID = '%s' " \
                "ORDER BY seqNo" % game_id

        self.live_data = db_my_conn.select(query, True)
        return self.live_data
    # endregion

    # region 게임진행 Functions
    def get_what_info(self, live_text_dict):
        """
        무엇을 할 지 결정한다.
        :param live_text_dict: live text dictionary data
        :return: data parameters
        """
        result = {}
        result_condition = {}
        result_hitter = {}

        result_accum_pitcher = {}
        result_accum_hitter = {}
        result_hit_event = {}

        text = live_text_dict['LiveText']
        ball_count = live_text_dict['ballcount']
        ball_type = live_text_dict['ball_type']
        text_style = live_text_dict['textStyle']
        live_state_sc = live_text_dict['STATE_SC']
        how = live_text_dict['HOW']
        batter = live_text_dict['batter']
        bat_order = live_text_dict['batorder']
        game_id = live_text_dict['gameID']
        seq_num = live_text_dict['seqNO']
        hitter = live_text_dict['batter']
        pitcher = live_text_dict['pitcher']
        live_dict = self.get_current_game_state(live_text_dict)

        # region 투수 등판 또는 교체시 투수 등록 및 투수의 기록을 가져온다.
        if pitcher and self.curr_pitcher is None:
            self.curr_pitcher = player.Pitcher(pitcher)
            pitcher_list = self.get_pitcher_record_data(pitcher, batter, live_dict['hitteam'])
            if pitcher_list:
                result_accum_pitcher.update({'pitcher_on_mound': pitcher_list})
        elif self.curr_pitcher is not None and pitcher != self.curr_pitcher.player_code:
            self.prev_pitcher = self.curr_pitcher
            self.curr_pitcher = player.Pitcher(pitcher)
            pitcher_list = self.get_pitcher_record_data(pitcher, batter, live_dict['hitteam'])
            if pitcher_list:
                result_accum_pitcher.update({'pitcher_on_mound': pitcher_list})
        # endregion

        # region 타자 등판 또는 교체시 타자 등록
        if batter and self.curr_hitter is None:
            self.curr_hitter = player.Hitter(batter)
        elif self.curr_hitter is not None and batter != self.curr_hitter.player_code:
            self.prev_hitter = self.curr_hitter
            self.curr_hitter = player.Hitter(batter)
        # endregion

        # region 게임 시작 정보 (경기장, 심판, 날씨 등)
        if seq_num == 0:
            game_info_data = self.get_game_info(game_id)
            if game_info_data:
                self.set_score("COMMON", game_info_data)
        # endregion

        # region 타자 등판 - 타자의 기록을 가져온다.
        if text_style == 8:
            self.prev_hitter = self.curr_hitter
            hitter_list = self.get_hitter_record_data(live_dict)
            if hitter_list:
                result_accum_hitter.update({'hitter_on_mound': hitter_list})
        # endregion

        # region 구종 정보
        if text_style == 1 and live_state_sc == 1 and ball_type != 'H':
            ball_style_dict = self.get_ball_style_data(game_id, bat_order, ball_count,
                                                       pitcher, hitter, self.curr_hitter.hit_type)
            if ball_style_dict:
                self.set_score("COMMON", ball_style_dict)
        # endregion

        # region 초구 정보
        if ball_count == 1 and ball_type not in ('F', 'H') and text_style == 1:
            print("캐스터: ", text)
            self.get_first_ball_info(self.curr_hitter.player_code, ball_type)
        # endregion

        # region 타격 Event 발생
        if ball_type == 'H' and text_style == 1:
            print("캐스터: 쳤습니다.")
        elif ball_type == 'H' and text_style == 13:
            start_time = time.time()
            if how in self._HIT:
                how_event = 'HIT'
                self.curr_hitter.update_hitter_record(how_event, live_dict)  # update HIT 기록
                if how == 'H2' or how == 'H3':
                    how_event = how
                    self.curr_hitter.update_hitter_record(how_event, live_dict)  # update H2 기록
            elif how in self._HR:
                how_event = 'HR'
                self.curr_hitter.update_hitter_record(how_event, live_dict)  # update HR 기록
            elif how in self._BB:
                how_event = 'BB'
                self.curr_hitter.update_hitter_record(how_event, live_dict)  # update BB 기록
            elif how in self._KK:
                how_event = 'KK'
                self.curr_hitter.update_hitter_record(how_event, live_dict)  # update KK 기록

            print('Update hitter record: %s' % (time.time() - start_time))
            start_time = time.time()
            hitter_record = self.get_hitter_record_data(live_dict)
            print('Get Hitter record: %s' % (time.time() - start_time))
            if hitter_record:
                result_hit_event.update({'hit_the_ball': hitter_record})
        # endregion

        if result_hitter:
            result.update({'hitter_info': result_hitter})
        if result_condition:
            result.update({'text_condition_info': result_condition})
        if result_accum_hitter:
            result.update(result_accum_hitter)
        if result_hit_event:
            result.update(result_hit_event)
        if result_accum_pitcher:
            result.update(result_accum_pitcher)

        return result
    # endregion

    # region Queue Functions
    @classmethod
    def put_queue(cls, msg):
        """
        Queue 에 넣는다.
        :param msg: 생성된 Message
        :return:
        """
        data = msg
        cls.caster_queue.put(data)
        cls.caster_queue.sort()

    @classmethod
    def get_queue(cls):
        """
        Queue 에서 뺀 후에 Decreasing 한다. [Thread]
        :return:
        """
        while True:
            if cls.caster_queue.size() > 0:
                score, sentence = cls.caster_queue.get()

                if sentence:
                    # HIT_BASIC_A_A - STATE, STATE_SPLIT, OPPONENT, LEAGUE
                    msg = cls.print_msg(sentence)
                    if msg:
                        print("캐스터: ", msg)
                    time.sleep(0.01*len(sentence))
                    cls.caster_queue.decrease_q(0.01)
    # endregion

    # region 기능 관련 Functions
    @classmethod
    def get_new_sigmoid(cls, x):
        """
        변경된 Sigmoid 함수 return -0.49 ~ 0.99
        :param x: 점수
        :return:
        """
        return 1 / (0.667 + exp(-10*x + 5)) - 0.5

    @classmethod
    def get_current_game_state(cls, live_data):
        """
        현재 경기 상황 정보 return dict: hitter, hitteam, pitcher, pitteam, score, base, game_id
        :param live_data:  live text data
        :return: 가공된 dictionary 정보
        """
        game_id = live_data['gameID']
        if live_data['bTop'] == 1:
            hit_team = game_id[8:10]
            pit_team = game_id[10:12]
            t_score = live_data['H_Run'] - live_data['A_Run']
        else:
            t_score = live_data['A_Run'] - live_data['H_Run']
            hit_team = game_id[10:12]
            pit_team = game_id[8:10]

        if t_score < 0:
            t = 'L'
        elif t_score == 0:
            t = 'D'
        else:
            t = 'W'

        if abs(t_score) == 1 or abs(t_score) == 0:
            score = "{0}{1}".format(abs(t_score), t)
        else:
            score = "{0}{0}".format(t)

        hitter = live_data['batter']
        pitcher = live_data['pitcher']

        if live_data['base1'] + live_data['base2'] + live_data['base3'] == 0:
            base = 'NOB'
        elif live_data['base1'] > 0 and live_data['base2'] + live_data['base3'] == 0:
            base = '1B'
        elif live_data['base2'] > 0 and live_data['base1'] + live_data['base3'] == 0:
            base = '2B'
        elif live_data['base3'] > 0 and live_data['base1'] + live_data['base1'] == 0:
            base = '3B'
        elif live_data['base1'] > 0 and live_data['base2'] > 0 and live_data['base3'] == 0:
            base = '12B'
        elif live_data['base1'] > 0 and live_data['base3'] > 0 and live_data['base2'] == 0:
            base = '13B'
        elif live_data['base2'] > 0 and live_data['base3'] > 0 and live_data['base1'] == 0:
            base = '23B'
        else:
            base = '123B'

        out_count = live_data['out']
        ball_count = [live_data['ball'], live_data['strike'], live_data['out']]

        result_dict = {'hitter': hitter, 'hitteam': hit_team, 'pitcher': pitcher, 'pitteam': pit_team,
                       'score': score, 'base': base, 'game_id': game_id, 'out_count': out_count,
                       'ball_count': ball_count}
        return result_dict

    @classmethod
    def get_game_info_data(cls, game_key):
        """
        게임 환경 정보
        :param game_key:
        :return:
        """
        db_my_conn = db.MySqlConnector(host=cls.__HOST, port=cls.__PORT, user=cls.__USER, pw=cls.__PASSWORD,
                                       db=cls.__DB)
        query = "SELECT Stadium, Vteam, Hteam, Umpc, Ump1, Ump2, Ump3, Mois, Weath, Wind Crowd, Chajun "\
                "FROM baseball.gameinfo "\
                "WHERE GmKey = '%s'" % game_key
        result_dict = db_my_conn.select(query, use_dict=True)
        return result_dict

    def get_game_info(self, game_key):
        info_dict = self.get_game_info_data(game_key)[0]
        if info_dict:
            result = [{'STADIUM': info_dict['Stadium'], 'VTEAM': info_dict['Vteam'], 'HTEAM': info_dict['Hteam'],
                       'UMPC': info_dict['Umpc'], 'UMP1': info_dict['Ump1'], 'UMP2': info_dict['Ump2'],
                       'UMP3': info_dict['Ump3'], 'MOIS': info_dict['Mois'], 'CHAJUN': info_dict['Chajun'],
                       'STATE': 'GAMEINFO', 'STATE_SPLIT': 'GAMEINFO', 'RANK': 1}]
            return result
        else:
            return None

    # region 점수 관련 함수
    def hitter_score_generator(self, data_dict):
        """
        scoring parameters
        :param data_dict:
        :return:  계산된 score
        """
        result = None
        state_score_val = 0
        state_split_score_val = 0
        rank_score = 0
        if 'STATE' in data_dict:
            state = data_dict['STATE']
            state_split = data_dict['STATE_SPLIT']

            if state in self.hitter_category_score:
                state_score_val = self.hitter_category_score.get(state)
                if 'RANK' in data_dict and type(data_dict.get('RANK')) is int:
                    rank_score = round(0.5 - (data_dict.get('RANK') / 200), 3)
                else:
                    print("Rank Exist: ", 'RANK' in data_dict, "Rank:", data_dict.get('RANK'),
                          "Type: ", type(data_dict.get('RANK')))
                    rank_score = round(0.5 - (10 / 200), 3)
            else:
                state_score_val = 0.5
                rank_score = 0.5

            if state_split in self.hitter_category_score:
                state_split_score_val = self.hitter_category_score.get(state_split)

        if state_score_val is not None and rank_score is not None:
            result = round(self.get_new_sigmoid(rank_score + (state_score_val + state_split_score_val) / 2), 3)

        return result

    def pitcher_score_generator(self, data_dict):
        result = None
        state_score_val = 0
        state_split_score_val = 0
        rank_score = 0
        if 'STATE' in data_dict:
            state = data_dict['STATE']
            state_split = data_dict['STATE_SPLIT']

            if state in self.pitcher_category_score:
                state_score_val = self.pitcher_category_score.get(state)
                if 'RANK' in data_dict and type(data_dict.get('RANK')) is int:
                    rank_score = round(0.5 - (data_dict.get('RANK') / 200), 3)
                else:
                    print("Rank Exist: ", 'RANK' in data_dict, "Rank:", data_dict.get('RANK'),
                          "Type: ", type(data_dict.get('RANK')))
                    rank_score = round(0.5 - (10 / 200), 3)
            else:
                state_score_val = 0.5
                rank_score = 0.5

            if state_split in self.pitcher_category_score:
                state_split_score_val = self.pitcher_category_score.get(state_split)

        if state_score_val is not None and rank_score is not None:
            result = round(self.get_new_sigmoid(rank_score + (state_score_val + state_split_score_val) / 2), 3)

        return result

    def common_score_generator(self, data_dict):
        result = None
        state_score_val = 0
        state_split_score_val = 0
        rank_score = 0
        if 'STATE' in data_dict:
            state = data_dict['STATE']
            state_split = data_dict['STATE_SPLIT']

            if state in self.common_category_score:
                state_score_val = self.common_category_score.get(state)
                if 'RANK' in data_dict and type(data_dict.get('RANK')) is int:
                    rank_score = round(0.5 - (data_dict.get('RANK') / 200), 3)
                else:
                    print("Rank Exist: ", 'RANK' in data_dict, "Rank:", data_dict.get('RANK'),
                          "Type: ", type(data_dict.get('RANK')))
                    rank_score = round(0.5 - (10 / 200), 3)
            else:
                state_score_val = 0.5
                rank_score = 0.5

            if state_split in self.common_category_score:
                state_split_score_val = self.common_category_score.get(state_split)

        if state_score_val is not None and rank_score is not None:
            result = round(self.get_new_sigmoid(rank_score + (state_score_val + state_split_score_val) / 2), 3)

        return result

    def set_score(self, subject, data_list):
        """
        DB 에서 메시지 가져오고, Value 계산한 후에 Score Table Queue 에 넣는다.
        :param subject:
        :param data_list:
        :return:
        """
        score_data = []
        for data_dict in data_list:
            if subject == "HITTER":
                score = self.hitter_score_generator(data_dict)
            elif subject == "PITCHER":
                score = self.pitcher_score_generator(data_dict)
            elif subject == "COMMON":
                score = self.common_score_generator(data_dict)

            if score:
                score_data.append([score, data_dict])
        if score_data:
            self.put_queue(score_data)

    # endregion

    # region 타자 관련 함수
    def set_hitter_record_with_state(self, how, live_data):
        """
        타자 이벤트 발생시 기록 UPDATE
        :param how:  HIT, HR, BB, KK, RBI
        :param live_data:  live text data
        :return:
        """
        live_dict = self.get_current_game_state(live_data)
        pitcher = live_data['pitcher']
        hitter = live_dict['hitter']
        year = datetime.now().year
        count_record_lists = [
            {'hitter': hitter, 'state': how, 'state_split': 'BASIC', 'opponent': 'ALL', 'gyear': year,
             'pitcher': 'NA', 'pitteam': 'NA'},  # 시즌 통산 기록
            {'hitter': hitter, 'state': how, 'state_split': 'VERSUS', 'opponent': 'PITCHER', 'gyear': year,
             'pitcher': pitcher, 'pitteam': 'NA'},  # 선수 대결 통산 기록
            {'hitter': hitter, 'state': how, 'state_split': 'VERSUS', 'opponent': 'TEAM', 'gyear': year,
             'pitcher': 'NA', 'pitteam': live_dict['pitteam']},  # 팀 대결 시즌 통산 기록
            {'hitter': hitter, 'state': how, 'state_split': live_dict['score'], 'opponent': 'ALL', 'gyear': year,
             'pitcher': 'NA', 'pitteam': 'NA'},  # 점수차 시즌 통산 기록
            {'hitter': hitter, 'state': how, 'state_split': live_dict['base'],  'opponent': 'ALL', 'gyear': year,
             'pitcher': 'NA', 'pitteam': 'NA'},  # 주자 상황 시즌 통산 기록
        ]

        for count_record_dict in count_record_lists:
            self.recorder.update_hitter_count_record(count_record_dict)

    def get_hitter_record_data(self, live_dict, state_event=None):
        """
        hitter 의 기록을 가져와 dictionary 로 만든다.
        :param live_dict:
        :param state_event:
        :return:
        """

        game_id = live_dict['game_id']
        hitter = live_dict['hitter']
        pitcher = live_dict['pitcher']
        pit_team = live_dict['pitteam']
        score = live_dict['score']
        base = live_dict['base']
        result_list = []

        # HITTER 의 오늘 기록
        today_record = self.curr_hitter.get_hitter_today_data(game_id)
        if today_record:
            result_list.extend(today_record)

        # HITTER 의 전체 기본 기록
        basic_record = self.curr_hitter.get_hitter_basic_data()
        if basic_record:
            result_list.extend(basic_record)

        # hitter vs pitcher 기록
        hitter_vs_pitcher_record = self.curr_hitter.get_hitter_vs_pitcher_data(hitter, pitcher, state_event)
        if hitter_vs_pitcher_record:
            result_list.extend(hitter_vs_pitcher_record)

        # hitter vs pitteam 기록
        hitter_vs_team_record = self.curr_hitter.get_hitter_vs_team_data(hitter, pit_team, state_event)
        if hitter_vs_team_record:
            result_list.extend(hitter_vs_team_record)

        # hitter 점수차 기록
        hitter_score_record = self.curr_hitter.get_hitter_score_data(hitter, score, state_event)
        if hitter_score_record:
            result_list.extend(hitter_score_record)

        # hitter 주자상황 기록
        hitter_base_record = self.curr_hitter.get_hitter_base_data(hitter, base, state_event)
        if hitter_base_record:
            result_list.extend(hitter_base_record)

        if result_list:
            self.curr_hitter.get_nine_record(result_list)
            # N 경기 연속기록 / N 타석 연속기록
            n_continue_record = self.curr_hitter.get_hitter_n_continue_data()
            if n_continue_record:
                result_list.extend(n_continue_record)
            return result_list
        else:
            return None

    def get_event_hitter_record(self, live_data):
        pass

    def get_first_ball_info(self, hitter, ball_type):
        """
        초구 정보
        :param hitter:
        :param ball_type: S: 헛스윙, T:기다리는 Strike
        :return:
        """
        data_dict = {'SUBJECT': 'HITTER', 'OPPONENT': 'NA', 'LEAGUE': 'NA', 'PITCHER': 'NA', 'PITNAME': 'NA',
                     'GYEAR': 'NA', 'PITTEAM': 'NA', 'STATE_SPLIT': 'FIRSTBALL', 'HITTER': hitter}

        result = []
        first_ball_info = self.recorder.get_hitter_first_ball(hitter)[0]

        if ball_type == 'S':
            if first_ball_info['T_CNT_RNK'] < 11:
                first_ball_dict = data_dict.copy()
                first_ball_dict['HITNAME'] = first_ball_info['HITNAME']
                first_ball_dict['RNK'] = 1
                first_ball_dict['STATE'] = '0S'
                first_ball_dict['PA'] = first_ball_info['PA']
                result.append(first_ball_dict)

        elif ball_type == 'T':
            if first_ball_info['S_CNT_RNK'] < 11:
                first_ball_dict = data_dict.copy()
                first_ball_dict['HITNAME'] = first_ball_info['HITNAME']
                first_ball_dict['RNK'] = 1
                first_ball_dict['STATE'] = '0T'
                first_ball_dict['PA'] = first_ball_info['PA']
                result.append(first_ball_dict)

        if result:
            self.set_score("HITTER", result)
    # endregion

    # region 투수 관련 함수
    def get_pitcher_record_data(self, pitcher, hitter, hit_team, state_event=None):
        result_list = []

        basic_record = self.curr_pitcher.get_pitcher_basic_data(pitcher)
        if basic_record:
            result_list.extend(basic_record)

        pitcher_vs_team_record = self.curr_pitcher.get_pitcher_vs_team_data(pitcher, hit_team, state_event)
        if pitcher_vs_team_record:
            result_list.extend(pitcher_vs_team_record)

        pitcher_vs_hitter_record = self.curr_pitcher.get_pitcher_vs_hitter_data(pitcher, hitter, state_event)
        if pitcher_vs_hitter_record:
            result_list.extend(pitcher_vs_hitter_record)

        if result_list:
            # self.curr_hitter.get_nine_record(result_list)
            # N 경기 연속기록 / N 타석 연속기록
            return result_list
        else:
            return None

    # endregion

    # region 메시지 관련 함수
    def make_sentence(self, data):
        """
        상황별 문장을 만든다.
        :param data:  query data parameters
        :return:
        """
        for key, value_dict in data.items():
            # 타자 등판 시
            subject = ''
            if key == 'hitter_on_mound':
                subject = "HITTER"
            elif key == 'hit_the_ball':
                subject = "HITTER"
            # 투수 등판 시
            elif key == 'pitcher_on_mound':
                subject = "PITCHER"
            # 경기장 상황

            if subject:
                self.set_score(subject, value_dict)

    @classmethod
    def print_msg(cls, value_dict):
        """
        Print Message
        :param value_dict:
        :return: None or Message string
        """
        # msg_code = "{}L0{:02d}".format(mcode, random.randrange(0, 2))
        msg = None
        msg_code = cls.get_msg_code(value_dict)

        if msg_code is None:
            return None

        db_my_conn = db.MySqlConnector(host=cls.__HOST, port=cls.__PORT,
                                       user=cls.__USER,
                                       pw=cls.__PASSWORD,
                                       db=cls.__DB)

        query = "SELECT MSG FROM baseball.castermsg_mas WHERE CODE = '%s' limit 1" % msg_code
        template = db_my_conn.select(query, True)
        if template:
            try:
                if 'RESULT' in value_dict and value_dict['RESULT'] > 1:
                    value_dict['RESULT'] = int(value_dict['RESULT'])

                msg = korean.l10n.Template(template[0]['MSG']).format(**value_dict)
            except Exception as ex:
                print(ex)
            return msg
        else:
            return None

    @classmethod
    def get_msg_code(cls, data_dict):
        """
        Message Code 생성
        :param data_dict:  data parameters
        :return: message code
        """
        msg_code_type1 = '{0}_{1}_{2}_{3}'
        msg_code_type2 = '{0}_{1}'

        if 'STATE' in data_dict:
            state = data_dict['STATE']
        else:
            state = None

        if 'STATE_SPLIT' in data_dict:
            if data_dict['STATE_SPLIT'] == 'VERSUS':
                state_split = 'VS'
            else:
                state_split = data_dict['STATE_SPLIT']
        else:
            state_split = None

        if 'OPPONENT' in data_dict:
            opponent = data_dict['OPPONENT'][0]
        else:
            opponent = None

        if 'LEAGUE' in data_dict:
            league = data_dict['LEAGUE'][0]
        else:
            league = None

        if state is not None and state_split is not None and opponent is not None and league is not None:
            msg = msg_code_type1.format(state, state_split, opponent, league)
        elif state is not None and state_split is not None:
            msg = msg_code_type2.format(state, state_split)
        else:
            msg = None

        return msg
    # endregion

    def get_ball_style_data(self, game_key, bat_order, ball_count, pitcher, hitter, hit_type):
        """
        ball style 설명
        :param game_key:
        :param bat_order:
        :param ball_count:
        :param hitter:
        :param pitcher:
        :param hit_type:
        :return:
        """

        stuff = {'FAST': '빠른 볼', 'CUTT': '커터', 'SLID': '슬라이더', 'CURV': '커브', 'CHUP': '체인지업',
                 'SPLI': '스플리터', 'SINK': '싱커볼', 'TWOS': '투심패스트볼', 'FORK': '포크볼', 'KNUC': '너클볼'}

        db_my_conn = db.MySqlConnector(host=self._HOST, port=self._PORT, user=self._USER, pw=self._PASSWORD,
                                       db=self._DB)
        query = "select ball, stuff, speed, zonex, zoney, x, y from baseball.pitzone " \
                "where gmkey = '{0}' and batorder = '{1}' and ballcount = '{2}' and " \
                "batter = '{3}' and pitcher = '{4}' limit 1".format(game_key, bat_order, ball_count, hitter, pitcher)
        data_list = db_my_conn.select(query, use_dict=True)

        if data_list:
            pitch_data = data_list[0]

            if pitch_data['stuff'] in stuff:
                pitch_type = stuff[pitch_data['stuff']]
            else:
                pitch_type = ''

            area_x = pitch_data['x']
            area_y = pitch_data['y']
            zone_x = pitch_data['zonex']
            zone_y = pitch_data['zoney']
            ball_type = pitch_data['ball']
            comment = ''

            if ball_type == 'B':  # 볼 판정
                if hit_type == '우타':
                    if zone_x < 2:
                        comment = '바깥으로 빠진 '
                    elif zone_x > 6:
                        comment = '몸 안쪽 '
                else:
                    if zone_x < 2:
                        comment = '몸 안쪽 '
                    elif zone_x > 6:
                        comment = '바깥으로 빠진 '
                if 50 < area_x < 177 and 63 < area_y < 225:
                    comment = '스트라이크 같았는데요'
            elif ball_type == 'T':  # 기다린 스트라이크
                if hit_type == '우타':  # 우타
                    if zone_x == 1 or zone_x == 2:  # 바깥쪽 스트라이크
                        if 45 < area_x < 55:
                            comment = '바깥쪽 꽉찬 스트라이크'
                        else:
                            comment = '바깥쪽 스트라이크'
                    elif zone_x == 6 or zone_x == 7:  # 몸쪽 스트라이크
                        if 215 < area_x < 235:
                            comment = '몸쪽 꽉찬 스크라이크'
                        else:
                            comment = '몸쪽 스트라이크'
                else:  # 좌타
                    if zone_x == 1 or zone_x == 2:  # 몸쪽 스트라이크
                        if 45 < area_x < 55:
                            comment = '몸쪽 꽉찬 스크라이크'
                        else:
                            comment = '몸쪽 스트라이크'
                    elif zone_x == 6 or zone_x == 7:  # 바깥쪽 스트라이크
                        if 215 < area_x < 235:
                            comment = '바깥쪽 꽉찬 스트라이크'
                        else:
                            comment = '바깥쪽 스트라이크'
            elif ball_type == 'S':  # 헛스윙
                if zone_y < 6:
                    comment = '낮은 공이였는데 휘둘렀어요'

            result = [{'SUBJECT': 'PITCHER', 'OPPONENT': 'NA', 'LEAGUE': 'NA', 'PITCHER': pitcher, 'PITNAME': 'NA',
                       'GYEAR': 'NA', 'PITTEAM': 'NA', 'STATE': 'BALLINFO', 'STATE_SPLIT': 'BALLINFO',
                       'COMMENT': comment, 'HITTER': hitter, 'STUFF': pitch_type,  'SPEED': pitch_data['speed'],
                       'RANK': 1}]

            return result
        else:
            return None
    # endregion
