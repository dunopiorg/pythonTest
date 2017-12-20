from lib import DBConnection as db
from lib import casterq
from lib import record
from math import exp
from datetime import datetime
import korean
import time


class GameHelper(object):

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

        # 기본 전역 변수
        self.event_cond_tuple = None
        self.event_category_tuple = None
        self.curr_away_score = 0  # 원정팀 현재 점수
        self.curr_home_score = 0  # 홈팀 현재 점수
        self.prev_away_score = 0  # 원정팀 이전 점수
        self.prev_home_score = 0  # 홈팀 이전 점수
        self.game_event = None
        self.prev_pitcher = None
        self.prev_hitter = None
        self.category_score = {}
        self.curr_row_num = 0

        # 기본 전역 객체 변수
        self.caster_queue = casterq.CasterQueue()
        self.recorder = record.Record()

        # initialize data
        self.get_cond_dict()
        self.get_category_score()
        self.get_event_category()

    def get_event_category(self):
        """
        MSG Code 생성시 필요한 인자 정보 테이블
        :return:
        """
        db_my_conn = db.MySqlConnector(host=self._HOST, port=self._PORT, user=self._USER, pw=self._PASSWORD,
                                       db=self._DB)
        query = "select mcode, event, param from baseball.event_catg"
        self.event_category_tuple = db_my_conn.select(query, False)

    def get_cond_dict(self):
        """
        Text 이벤트에 따른 함수 활성화 정의 테이블
        :return:
        """
        db_my_conn = db.MySqlConnector(host=self._HOST, port=self._PORT,
                                       user=self._USER, pw=self._PASSWORD, db=self._DB)
        query = "select EVENT, CONDITIONS from baseball.event_cond"
        self.event_cond_tuple = db_my_conn.select(query, True)

    def get_category_score(self):
        """
        이벤트 카테고리 별 점수
        :return:  category score dictionary
        """
        db_my_conn = db.MySqlConnector(host=self._HOST, port=self._PORT, user=self._USER, pw=self._PASSWORD,
                                       db=self._DB)
        query = "select category, score from baseball.catg_score"
        rows = db_my_conn.select(query, True)
        self.category_score = {row["category"]: row["score"] for row in rows}
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

        result_accum_hitter = {}
        result_hit_event = {}

        text = live_text_dict['LiveText']
        curr_hitter = live_text_dict['batter']
        ball_count = live_text_dict['ballcount']
        ball_type = live_text_dict['ball_type']
        text_style = live_text_dict['textStyle']
        how = live_text_dict['HOW']
        game_id = live_text_dict['gameID']

        # 타자 설정
        if self.prev_hitter != curr_hitter and text_style == 8:
            if len(curr_hitter) > 0:
                self.prev_hitter = curr_hitter
                # 타자의 기록을 가져온다.
                start_time = time.time()
                hitter_list = self.get_hitter_record(live_text_dict)
                print('Second: %s' % (time.time() - start_time))
                if hitter_list:
                    result_accum_hitter.update({'hitter_on_mound': hitter_list})

        # 게임중 나타나는 이벤트 설정
        """
        word_list = text.split()
        for cond_dict in self.event_cond_tuple:
            if cond_dict.get('EVENT') in word_list:
                self.game_event = cond_dict.get('EVENT')
                cond_list = cond_dict.get('CONDITIONS').split(',')
                for cond in cond_list:
                    method = getattr(self, cond)
                    t_dict = method()
                    if t_dict:
                        result_condition.update(t_dict)
        """

        # 초구 정보
        if ball_count == 1 and ball_type not in ('F', 'H') and text_style == 1:
            print("캐스터: ", text)
            self.get_first_ball_info(curr_hitter, ball_type)

        # 타격 Event 발생
        if ball_type == 'H' and text_style == 1:
            print("캐스터: 쳤습니다.")
        elif ball_type == 'H' and text_style == 13:
            if how in self._HIT:
                how_event = 'HIT'
                if how == 'H2' or how == 'H3':
                    how_event = how
            elif how in self._HR:
                how_event = 'HR'
            elif how in self._BB:
                how_event = 'BB'
            elif how in self._KK:
                how_event = 'KK'
            else:
                how_event = 'HIT'
            self.set_hitter_record_with_state(how_event, live_text_dict)  # update 기록
            hitter_record = self.get_hitter_record(live_text_dict)
            if hitter_record:
                result_hit_event.update({'hit_the_ball': hitter_record})

        if result_hitter:
            result.update({'hitter_info': result_hitter})
        if result_condition:
            result.update({'text_condition_info': result_condition})
        if result_accum_hitter:
            result.update(result_accum_hitter)
        if result_hit_event:
            result.update(result_hit_event)

        return result
    # endregion

    # region Queue Functions
    def put_queue(self, msg):
        """
        Queue 에 넣는다.
        :param msg: 생성된 Message
        :return:
        """
        data = msg
        self.caster_queue.put(data)
        self.caster_queue.sort()

    def get_queue(self):
        """
        Queue 에서 뺀 후에 Decreasing 한다. [Thread]
        :return:
        """
        while True:
            if self.caster_queue.size() > 0:
                sentence = self.caster_queue.get()[1]

                if sentence:
                    # HIT_BASIC_A_A - STATE, STATE_SPLIT, OPPONENT, LEAGUE
                    msg = self.print_msg(sentence)
                    if msg:
                        print("캐스터: ", msg)
                    time.sleep(0.01*len(sentence))
                    self.caster_queue.decrease_q(0.01)
    # endregion

    # region 기능 관련 Functions
    def make_sentence(self, data):
        """
        상황별 문장을 만든다.
        :param data:  query data parameters
        :return:
        """
        for key, value_dict in data.items():
            # 타자 등판 시
            if key == 'hitter_on_mound':
                self.set_score(value_dict)
            elif key == 'hit_the_ball':
                self.set_score(value_dict)
            # 홈런 상황
            # 투수 등판 시
            # 타자 등판 시

    def get_hitter_record(self, data):
        """
        hitter 의 기록을 가져와 dictionary 로 만든다.
        :param data: live text dictionary data
        :return:
        """
        live_dict = self.get_current_game_state(data)

        game_id = live_dict['game_id']
        hitter = live_dict['hitter']

        result_list = []

        today_record = self.get_today_hitter_data(game_id, hitter)  # HITTER 의 오늘 기록
        if today_record:
            result_list.extend(today_record)

        total_record = self.recorder.get_total_hitter_record(live_dict)  # HITTER 의 전체 기록
        if total_record:
            result_list.extend(total_record)

        if result_list:
            self.set_nine_record(result_list)
            ngame_record = self.get_ngame_continuous_data(hitter)  # N 경기 연속기록
            if ngame_record:
                result_list.extend(ngame_record)
            npa_record = self.get_npa_continuous_data(hitter)  # N 타석 연속기록
            if npa_record:
                result_list.extend(npa_record)
            return result_list
        else:
            return None

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
        first_ball_info = self.recorder.get_first_ball_info(hitter)[0]

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
            self.set_score(result)

    def get_new_sigmoid(self, x):
        """
        변경된 Sigmoid 함수 return -0.49 ~ 0.99
        :param x: 점수
        :return:
        """
        return 1 / (0.667 + exp(-10*x + 5)) - 0.5

    def score_generator(self, data):
        """
        scoring parameters
        :param data:
        :return:  계산된 score
        """
        result = None
        state_score_val = None
        state_split_score_val = None
        rank_score = None
        if 'STATE' in data:
            state = data['STATE']
            state_split = data['STATE_SPLIT']

            if state in self.category_score:
                state_score_val = self.category_score.get(state)
                rank_score = round(0.5 - (data.get('RNK') / 200), 3)
            else:
                state_score_val = 0.5
                rank_score = 0.5

            if state_split in self.category_score:
                state_split_score_val = self.category_score.get(state_split)

        if state_score_val is not None and rank_score is not None:
            result = round(self.get_new_sigmoid(rank_score + (state_score_val + state_split_score_val) / 2), 3)

        return result

    def set_score(self, data):
        """
        DB 에서 메시지 가져오고, Value 계산한 후에 Score Table Queue 에 넣는다.
        :param data:
        :return:
        """
        score_data = []
        for data_dict in data:
            score = self.score_generator(data_dict)
            if score:
                score_data.append([score, data_dict])
        if score_data:
            self.put_queue(score_data)

    def print_msg(self, value_dict):
        """
        Print Message
        :param value_dict:
        :return: None or Message string
        """
        # msg_code = "{}L0{:02d}".format(mcode, random.randrange(0, 2))
        msg = None
        msg_code = self.get_msg_code(value_dict)

        db_my_conn = db.MySqlConnector(host=self._HOST, port=self._PORT,
                                       user=self._USER,
                                       pw=self._PASSWORD,
                                       db=self._DB)

        query = "SELECT MSG FROM baseball.castermsg_mas WHERE CODE = '%s' limit 1" % msg_code
        template = db_my_conn.select(query, True)
        if template:
            try:
                if value_dict['RESULT'] > 1:
                    value_dict['RESULT'] = int(value_dict['RESULT'])

                msg = korean.l10n.Template(template[0]['MSG']).format(**value_dict)
            except Exception as ex:
                print(ex)
            return msg
        else:
            return None

    def set_nine_record(self, data_list):
        """
        10단위, 100단위 생성
        :param data_list: 기존 기록 결과
        :return:  기존기록 결과에 추가로 단위수 결과 생성
        """
        categories = ['HIT', 'HR', 'RBI', 'BB']
        for data_dict in data_list:
            if data_dict['STATE'] in categories and data_dict['STATE_SPLIT'] == 'BASIC':
                result_record = data_dict['RESULT']
                league = data_dict['LEAGUE']

                if league == 'SEASON':
                    if result_record % 10 == 9:
                        copy_dict = data_dict.copy()
                        copy_dict['RESULT'] = copy_dict['RESULT'] + 1
                        copy_dict['STATE_SPLIT'] = 'UNIT10'
                        data_list.append(copy_dict)
                else:
                    if result_record % 100 == 99:
                        copy_dict = data_dict.copy()
                        copy_dict['RESULT'] = copy_dict['RESULT'] + 1
                        copy_dict['STATE_SPLIT'] = 'UNIT100'
                        data_list.append(copy_dict)

    def get_ngame_continuous_data(self, hitter):
        """
        N경기 연속  데이터 생성
        :param hitter:
        :return:  dictionary parameter 결과
        """
        state_dict = {'HIT': ['H1', 'H2', 'H3', 'HR', 'HI', 'HB'], 'HR': ['HR'],
                      'RBI': ['E', 'R', 'H'], 'BB': ['BB', 'IB'], 'KK': ['KK']}
        data_dict = {'SUBJECT': 'HITTER', 'OPPONENT': 'ALL', 'LEAGUE': 'SEASON',
                     'PITCHER': 'NA', 'PITNAME': 'NA', 'PITTEAM': 'NA'}

        hitter_gm_list = self.recorder.get_hitter_continuous_record(hitter)
        result = []

        for state_k, state_v_list in state_dict.items():
            counter = 0
            gmkey = ''
            for hitter_gm_dict in hitter_gm_list:
                if gmkey != hitter_gm_dict['GMKEY']:
                    gmkey = hitter_gm_dict['GMKEY']
                    if state_k == 'RBI':
                        how = hitter_gm_dict['PLACE']
                    else:
                        how = hitter_gm_dict['HOW']

                    if how in state_v_list:
                        counter += 1
                        continue
                    else:
                        if counter > 1:
                            data_dict['RESULT'] = counter
                            data_dict['STATE'] = state_k
                            data_dict['STATE_SPLIT'] = 'NGAME'
                            result.append(data_dict)
                        break
        return result

    def get_npa_continuous_data(self, hitter):
        """
        N타석 연속 데이터 생성
        :param hitter:
        :return: dictionary parameter 결과
        """
        state_dict = {'HIT': ['H1', 'H2', 'H3', 'HR', 'HI', 'HB'], 'HR': ['HR'], 'RBI': ['E', 'R', 'H'],
                      'BB': ['BB', 'IB'], 'KK': ['KK']}
        data_dict = {'SUBJECT': 'HITTER', 'OPPONENT': 'ALL', 'LEAGUE': 'SEASON', 'PITCHER': 'NA', 'PITNAME': 'NA',
                     'PITTEAM': 'NA'}

        hitter_gm_list = self.recorder.get_hitter_continuous_record(hitter)
        result = []
        for state_k, state_v_list in state_dict.items():
            counter = 0
            for hitter_gm_dict in hitter_gm_list:
                if state_k == 'RBI':
                    how = hitter_gm_dict['PLACE']
                else:
                    how = hitter_gm_dict['HOW']

                if how in state_v_list:
                    counter += 1
                    continue
                else:
                    if counter > 1:
                        data_dict['RESULT'] = counter
                        data_dict['STATE'] = state_k
                        data_dict['STATE_SPLIT'] = 'NPA'
                        result.append(data_dict)
                    break
        return result

    def get_msg_code(self, data_dict):
        """
        Message Code 생성
        :param data_dict:  data parameters
        :return: message code
        """
        msg_code = '{0}_{1}_{2}_{3}'
        state = data_dict['STATE']
        if data_dict['STATE_SPLIT'] == 'VERSUS':
            state_split = 'VS'
        else:
            state_split = data_dict['STATE_SPLIT']
        opponent = data_dict['OPPONENT'][0]
        league = data_dict['LEAGUE'][0]

        return msg_code.format(state, state_split, opponent, league)

    def get_today_hitter_data(self, gmkey, hitter):
        """
        오늘 경기 기록
        :param gmkey: game key
        :param hitter:  hitter
        :return: query에 들어갈 정보
        """
        result = []
        today = self.recorder.get_today_hitter_record(gmkey, hitter)
        if today:
            data_dict = {'SUBJECT': 'HITTER', 'OPPONENT': 'NA', 'LEAGUE': 'NA', 'PITCHER': 'NA', 'PITNAME': 'NA',
                         'GYEAR': 'NA', 'PITTEAM': 'NA', 'STATE_SPLIT': 'TODAY',
                         'RNK': 1, 'HITTER': hitter, 'HITNAME': today[0]['HITNAME'], 'PA': int(today[0]['PA'])}

            for k, v in today[0].items():
                if k == 'PA' or k == 'HITNAME':
                    continue
                set_dict = data_dict.copy()
                set_dict['STATE'] = k
                set_dict['RESULT'] = int(v)
                result.append(set_dict)
        return result

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

        param_dict = {'state': how, 'splits': "'{0}', '{1}', '{2}', '{3}'".format(
            'BASIC', 'VERSUS', live_dict['score'], live_dict['base'])}
        self.recorder.call_update_state_rank(param_dict)

    def get_current_game_state(self, live_data):
        """
        현재 경기 상황 정보 return dict: hitter, hitteam, pitcher, pitteam, score, base, game_id
        :param live_data:  live text data
        :return: 가공된 dictionary 정보
        """
        game_id = live_data['gameID']
        if live_data['bTop'] == 1:
            hitteam = game_id[8:10]
            pitteam = game_id[10:12]
            t_score = live_data['H_Run'] - live_data['A_Run']
        else:
            t_score = live_data['A_Run'] - live_data['H_Run']
            hitteam = game_id[10:12]
            pitteam = game_id[8:10]

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

        result_dict = {'hitter': hitter, 'hitteam': hitteam, 'pitcher': pitcher, 'pitteam': pitteam,
                       'score': score, 'base': base, 'game_id': game_id}
        return result_dict
    # endregion
