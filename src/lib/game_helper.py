from datetime import datetime
from math import exp, log
from lib import DBConnection as db
from lib import message_maker
from lib import casterq
from lib import player
from lib import record
from korean import Noun
import time
import korean


class GameHelper(object):
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
        self._SO = ['KK','KN','KB','KW','KP']
        self._PA = ['H1','H2','H3','HR','HI','HB','BB','IB','HP','KK','KN','KB'
							,'KW','KP','IN','OB','IP','XX','SH','SF','FC','GD','TP','GR','BN','FL','LL','IF','FF']
        self._BALL_STUFF = {'FAST': '패스트볼', 'CUTT': '커터', 'SLID': '슬라이더', 'CURV': '커브',
                            'CHUP': '체인지업', 'SPLI': '스플리터', 'SINK': '싱커볼', 'TWOS': '투심패스트볼',
                            'FORK': '포크볼', 'KNUC': '너클볼'}
        self._TEAM_KOR = {"WO": "넥센", "SS": "삼성", "SK": "SK", "OB": "두산",
                         "NC": "NC", "LT": "롯데", "LG": "LG", "KT ": "KT", "HT": "기아", "HH": "한화"}
        # test를 위한 변수 (실제 운영시 고쳐야 한다)
        self.live_data = None

        # 기본 전역 변수
        self.prev_pitcher = None
        self.prev_hitter = None
        self.curr_hitter = None
        self.curr_pitcher = None
        self.hitter_category_score = {}
        self.pitcher_category_score = {}
        self.common_category_score = {}
        self.today_category_score = {}
        self.continue_ball_count_b = 0  # 연속 볼
        self.continue_ball_count_f = 0  # 연속 파울
        self.continue_ball_stuff = {}

        # 기본 전역 상수
        self._LEAGUE_SEASON_SCORE = 4
        self._LEAGUE_ALL_SCORE = 3
        self._PRE_THRESHOLD = 50
        self._SEASON = "SEASON"
        self._ALL = "ALL"
        self._HITTER_EVENT = "HITTER"
        self._PITCHER_EVENT = "PITCHER"
        self._COMMON_EVENT = "COMMON"
        self._HITTER_PLAY_EVENT = "HIT_EVENT"
        self._TODAY_EVENT = "TODAY"

        # 기본 전역 객체 변수
        self.recorder = record.Record()
        self.caster_queue = casterq.CasterQueue()
        self.msg_maker = message_maker.MessageMaker()

        # initialize data
        self.set_category_score()

    def set_category_score(self):
        """
        이벤트 카테고리 별 점수
        :return:  category score dictionary
        """
        db_my_conn = db.MySqlConnector(host=self._HOST, port=self._PORT, user=self._USER, pw=self._PASSWORD,
                                       db=self._DB)
        query = "select event, state_split, category, score from baseball.event_score"
        rows = db_my_conn.select(query, True)
        for row in rows:
            if row["event"] == self._HITTER_EVENT:
                self.hitter_category_score.update({row["category"]: row["score"], "state_split": row["state_split"]})
            elif row["event"] == self._PITCHER_EVENT:
                self.pitcher_category_score.update({row["category"]: row["score"], "state_split": row["state_split"]})
            elif row["event"] == self._COMMON_EVENT:
                self.common_category_score.update({row["category"]: row["score"], "state_split": row["state_split"]})
            elif row["event"] == self._TODAY_EVENT:
                self.today_category_score.update({row["category"]: row["score"], "state_split": row["state_split"]})

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

        result_pitcher = {}
        result_hitter = {}
        result_hit_event = {}
        result_today = {}

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

        # region 게임 시작 정보 (경기장, 심판, 날씨 등)
        if seq_num == 0:
            game_info_data = self.get_game_info(game_id)
            if game_info_data:
                self.set_score(self._COMMON_EVENT, game_info_data)
        # endregion

        # region 게임 진행 정보 (아웃카운트, 주루 상황, 점수상황)
        current_game_info = self.get_current_game_info(live_dict)
        if current_game_info:
            self.set_score(self._COMMON_EVENT, current_game_info)
        # endregion

        # region 투수 등판 또는 교체시 투수 등록 및 투수의 기록을 가져온다.
        if pitcher and self.curr_pitcher is None:
            self.curr_pitcher = player.Pitcher(pitcher)
            pitcher_list = self.get_pitcher_record_data(pitcher, batter, live_dict['hitteam'])
            if pitcher_list:
                result_pitcher.update({self._PITCHER_EVENT: pitcher_list})
        elif pitcher and self.curr_pitcher is not None and pitcher != self.curr_pitcher.player_code:
            self.prev_pitcher = self.curr_pitcher
            self.curr_pitcher = player.Pitcher(pitcher)
            pitcher_list = self.get_pitcher_record_data(pitcher, batter, live_dict['hitteam'])
            if pitcher_list:
                result_pitcher.update({self._PITCHER_EVENT: pitcher_list})
        # endregion

        # region 타자 등판 또는 교체시 타자 등록
        if batter and self.curr_hitter is None:
            self.curr_hitter = player.Hitter(batter)
        elif self.curr_hitter is not None and batter != self.curr_hitter.player_code:
            self.prev_hitter = self.curr_hitter
            self.curr_hitter = player.Hitter(batter)
        # endregion

        # region 타자 등판 - 타자의 기록을 가져온다.
        if text_style == 8:
            print("캐스터: ", text)
            self.prev_hitter = self.curr_hitter
            # HITTER 의 오늘 기록 및 통산 기록
            today_record = self.get_hitter_basic_record_data(batter, game_id)
            if today_record:
                result_today.update({self._TODAY_EVENT: today_record})
            # HITTER의 상황별 기록
            hitter_list = self.get_hitter_split_record_data(live_dict)
            if hitter_list:
                result_hitter.update({self._HITTER_EVENT: hitter_list})
            self.curr_hitter.set_prev_total_record()  #total 기록을 previous 기록으로 복사
        # endregion

        # region 구종 정보
        if text_style == 1 and live_state_sc == 1 and ball_type != 'H' and ball_type != 'F':
            ball_style_dict = self.get_ball_style_data(game_id, bat_order, ball_count,
                                                       pitcher, hitter, self.curr_hitter.hit_type)
            if ball_style_dict:
                self.set_score(self._COMMON_EVENT, ball_style_dict)
        # endregion

        # region 초구 정보
        if ball_count == 1 and ball_type not in ('F', 'H') and text_style == 1:
            self.get_first_ball_info(self.curr_hitter.player_code, ball_type)
        # endregion

        # region 타격 Event 발생
        if ball_type == 'H' and text_style == 1:
            print("캐스터: ", text)
            print("캐스터: 쳤습니다.")
        elif text_style == 13 or text_style == 23:
            print("캐스터: ", text)
            how_event = None
            hitter_record = None
            if how in self._HIT:
                if how == 'H2' or how == 'H3':
                    how_event = how
                    self.curr_hitter.update_hitter_record(how_event, live_dict)  # update H2 or H3 기록
                elif how in self._HR:
                    how_event = 'HR'
                    self.curr_hitter.update_hitter_record(how_event, live_dict)  # update HR 기록
                else:
                    how_event = 'HIT'
                    self.curr_hitter.update_hitter_record(how_event, live_dict)  # update HIT 기록
            elif how in self._BB:
                how_event = 'BB'
                self.curr_hitter.update_hitter_record(how_event, live_dict)  # update BB 기록
            elif how in self._SO:
                how_event = 'SO'
                self.curr_hitter.update_hitter_record(how_event, live_dict)  # update SO 기록

            if how_event:
                hitter_record = self.get_hitter_split_record_data(live_dict, how_event)
            if hitter_record:
                result_hit_event.update({self._HITTER_PLAY_EVENT: hitter_record})

        if how in self._PA:
            self.curr_hitter.update_hitter_pa_record(live_dict)  # update PA count
        # endregion

        if result_hitter:
            result.update(result_hitter)
        if result_hit_event:
            result.update(result_hit_event)
        if result_pitcher:
            result.update(result_pitcher)
        if result_today:
            result.update(result_today)

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
        # for d in data:
        #    print(d)
        while True:
            if self.caster_queue.async_flag == 0:
                self.caster_queue.async_flag = 1
                self.caster_queue.put(data)
                self.caster_queue.async_flag = 0
                break

    def get_queue(self):
        """
        Queue 에서 뺀 후에 Decreasing 한다. [Thread]
        :return:
        """
        while True:
            if self.caster_queue.async_flag == 0 and self.caster_queue.size() > 0:
                self.caster_queue.async_flag = 1
                self.caster_queue.sort()
                self.caster_queue.async_flag = 0
                parameter_list = []
                event_group = ''
                event = ''

                for i in range(self.caster_queue.size()):
                    if i == 0:
                        selected_row = self.caster_queue.get(i)
                        if selected_row[1] == self._HITTER_PLAY_EVENT:
                            grouping_event= 1
                        else:
                            grouping_event = 3
                        event_group = selected_row[grouping_event]
                        event = selected_row[1]
                        parameter_list.append(selected_row)
                        self.caster_queue.set(i, None)
                    else:
                        relative_row = self.caster_queue.get(i)
                        if event_group == relative_row[grouping_event]:
                            parameter_list.append(relative_row)
                            self.caster_queue.set(i, None)

                if parameter_list:
                    msg = None
                    if event == self._HITTER_EVENT:
                        #  msg = self.msg_maker.get_hitter_message(parameter_list)
                        msg = self.msg_maker.get_hitter_split_message(parameter_list)
                    elif event == self._PITCHER_EVENT:
                        msg = self.msg_maker.get_pitcher_message(parameter_list)
                    elif event == self._HITTER_PLAY_EVENT:
                        msg = self.msg_maker.get_hit_event_message_new(parameter_list)
                    elif event == self._TODAY_EVENT:
                        if parameter_list[0][4] == "TODAY_BASIC":
                            msg = self.msg_maker.get_today_basic_event_message(parameter_list)
                        else:
                            msg = self.msg_maker.get_today_event_message(parameter_list)
                    elif event == self._COMMON_EVENT:
                        msg = self.msg_maker.get_common_message(parameter_list)

                    if msg:
                        print("캐스터: ", msg.rstrip('\n'))

                self.caster_queue.delete_none()

                """
                if parameters:
                    # HIT_BASIC_A_A - STATE, STATE_SPLIT, OPPONENT, LEAGUE
                    msg = cls.print_msg(parameters)
                    if msg:
                        print("캐스터: ", msg)
                    time.sleep(0.01*len(msg))
                    cls.caster_queue.decrease_q(0.01)
                """
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

        if t_score == 0:
            score_detail = "0D"
        else:
            score_detail = "{0}{1}".format(abs(t_score), t)

        hitter = live_data['batter']
        pitcher = live_data['pitcher']

        if live_data['base1'] + live_data['base2'] + live_data['base3'] == 0:
            base = 'NOB'
        elif live_data['base2'] + live_data['base3'] > 0:
            base = 'SCORE_B'
        else:
            base = 'ONB'

        if live_data['base1'] + live_data['base2'] + live_data['base3'] == 0:
            base_detail = '0B'
        elif live_data['base1'] > 0 and live_data['base2'] + live_data['base3'] == 0:
            base_detail = '1B'
        elif live_data['base2'] > 0 and live_data['base1'] + live_data['base3'] == 0:
            base_detail = '2B'
        elif live_data['base3'] > 0 and live_data['base1'] + live_data['base1'] == 0:
            base_detail = '3B'
        elif live_data['base1'] > 0 and live_data['base2'] > 0 and live_data['base3'] == 0:
            base_detail = '12B'
        elif live_data['base1'] > 0 and live_data['base3'] > 0 and live_data['base2'] == 0:
            base_detail = '13B'
        elif live_data['base2'] > 0 and live_data['base3'] > 0 and live_data['base1'] == 0:
            base_detail = '23B'
        else:
            base_detail = '123B'

        out_count = live_data['out']
        full_count = [live_data['ball'], live_data['strike'], live_data['out']]
        bat_order = live_data['batorder']
        ball_count = live_data['ballcount']
        text_style = live_data['textStyle']
        ball_type = live_data['ball_type']

        result_dict = {'hitter': hitter, 'hitteam': hit_team, 'pitcher': pitcher, 'pitteam': pit_team,
                       'score': score, 'base': base, 'game_id': game_id, 'out_count': out_count,
                       'full_count': full_count, 'base_detail': base_detail, 'score_detail': score_detail,
                       'batorder': bat_order, 'ballcount': ball_count, 'textStyle': text_style,
                       'ball_type': ball_type}
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
        query = "SELECT Stadium, Vteam, Hteam, Umpc, Ump1, Ump2, Ump3, Mois, Weath, Wind, Crowd, Chajun "\
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
        state_list = ['HIT', 'H2', 'H3', 'RBI', 'BB', 'SO']
        result = None
        state_score_val = 0
        rank_score = 0
        league_score = 0
        rate_score = 0
        state_pa_val = 0
        state_result = 1

        if 'STATE' in data_dict:
            if 'LEAGUE' in data_dict and data_dict['LEAGUE'] == 'ALL':
                league_score = self._LEAGUE_ALL_SCORE
            else:
                league_score = self._LEAGUE_SEASON_SCORE

            if 'RANK' in data_dict:
                rank = data_dict['RANK']
                rank_score = log(rank, 0.8) + 20

            if 'RATE_SCORE' in data_dict:
                rate_score = data_dict['RATE_SCORE']

            state = data_dict['STATE']

            if state in self.hitter_category_score:
                if state in state_list:
                    state_result_val = data_dict['RESULT']
                    try:
                        state_pa_val = data_dict['PA']
                    except Exception as e:
                        print(e, data_dict)

                    if state_pa_val > 0:
                        state_result = state_result_val / state_pa_val
                else:
                    state_result = data_dict['RESULT']

                state_score_val = self.hitter_category_score.get(state)
            else:
                state_score_val = 0.1

        if state_score_val != 0:
            result = round((rate_score + rank_score + (state_score_val * league_score)) * state_result, 3)

        return result

    def pitcher_score_generator(self, data_dict):
        result = None
        state_score_val = 0
        rank_score = 0
        league_score = 0
        if 'STATE' in data_dict:
            if 'LEAGUE' in data_dict and data_dict['LEAGUE'] == 'ALL':
                league_score = self._LEAGUE_ALL_SCORE
            else:
                league_score = self._LEAGUE_SEASON_SCORE

            if 'RANK' in data_dict:
                rank = data_dict['RANK']
                rank_score = log(rank, 0.8) + 20

            state = data_dict['STATE']

            if state in self.pitcher_category_score:
                state_score_val = self.pitcher_category_score.get(state)
            else:
                state_score_val = 0.1

        if state_score_val != 0:
            result = round(rank_score + (state_score_val * league_score), 3)

        return result

    def common_score_generator(self, data_dict):
        result = None
        state_score_val = 0
        rank_score = 0
        league_score = 0
        if 'STATE' in data_dict:
            if 'LEAGUE' in data_dict and data_dict['LEAGUE'] == 'ALL':
                league_score = self._LEAGUE_ALL_SCORE
            else:
                league_score = self._LEAGUE_SEASON_SCORE

            if 'RANK' in data_dict:
                rank = data_dict['RANK']
                rank_score = log(rank, 0.8) + 20

            state = data_dict['STATE']

            if state in self.common_category_score:
                state_score_val = self.common_category_score.get(state)
            else:
                state_score_val = 0.1

        if state_score_val != 0:
            result = round(rank_score + (state_score_val * league_score), 3)

        return result

    def today_score_generator(self, data_dict):
        result = None
        state_score_val = 0
        league_score = 0
        event_score = 100
        if 'STATE' in data_dict:
            if 'LEAGUE' in data_dict and data_dict['LEAGUE'] == 'ALL':
                league_score = self._LEAGUE_ALL_SCORE
            else:
                league_score = self._LEAGUE_SEASON_SCORE

            state_split = data_dict['STATE_SPLIT']

            if state_split in self.today_category_score:
                state_score_val = self.today_category_score.get(state_split)
            else:
                state_score_val = 0.1

        if state_score_val != 0:
            result = round(event_score + (state_score_val * league_score), 3)

        return result

    def set_score(self, event, data_list):
        """
        DB 에서 메시지 가져오고, Value 계산한 후에 Score Table Queue 에 넣는다.
        :param event:
        :param data_list:
        :return:
        """
        score = None
        score_data = []

        pre_scored_list = self.pre_score_generator(event, data_list)

        for data_dict in pre_scored_list:
            if event == self._HITTER_EVENT or event == self._HITTER_PLAY_EVENT:
                score = self.hitter_score_generator(data_dict)
            elif event == self._PITCHER_EVENT:
                score = self.pitcher_score_generator(data_dict)
            elif event == self._COMMON_EVENT:
                score = self.common_score_generator(data_dict)
            elif event == self._TODAY_EVENT:
                score = self.today_score_generator(data_dict)

            if score:
                score_data.append([score, event, data_dict["STATE"], data_dict["DATA_GROUP"], data_dict])
        if score_data:
            self.put_queue(score_data)

    def pre_score_generator(self, subject, data_list):
        if subject == self._HITTER_EVENT or subject == self._HITTER_PLAY_EVENT:
            state_group_data = {}
            compare_temp_list = []
            new_data_list = []
            state_list = ["BB", "H2", "HIT", "HRA", "SO", "OBA", "RBI", "SLG", "H3", "HR"]
            rate_list = ["HRA", "OBA", "SLG"]
            split_list = ["1UNIT", "RANKER", "NPA", "NGAME"]

            for state in state_list:
                temp_list = [data_dict for data_dict in data_list if state == data_dict['STATE']]
                if temp_list:
                    state_group_data[state] = temp_list

            season_rate = 0
            all_rate = 0
            # total, season 기본 rate 구성
            for state_key, state_data_list in state_group_data.items():
                compare_temp_list = []
                hitter_total_list = self.curr_hitter.get_total_record()
                if hitter_total_list:
                    for hitter_total in hitter_total_list:
                        total_state = hitter_total["STATE"]
                        total_league = hitter_total['LEAGUE']
                        total_result = hitter_total["RESULT"]
                        total_rate = hitter_total['RATE']
                        if state_key == total_state:
                            if total_state in rate_list:
                                if total_league == self._SEASON:
                                    season_rate = total_result
                                else:
                                    all_rate = total_result
                            else:
                                if total_league == self._SEASON:
                                    season_rate = total_rate
                                else:
                                    all_rate = total_rate

                for state_data_dict in state_data_list:
                    rate_score = 0
                    divide_rate = 0
                    try:
                        state_rate = state_data_dict["RATE"]
                        state_split = state_data_dict["STATE_SPLIT"]
                        state_info = state_data_dict["STATE"]
                        league_info = state_data_dict["LEAGUE"]
                        state_result = state_data_dict["RESULT"]
                    except Exception as ex:
                        print(ex)

                    if league_info == self._SEASON:
                        if season_rate == 0:
                            rate_score = 0
                        else:
                            if state_info in rate_list:
                                divide_rate = state_result / season_rate
                            else:
                                divide_rate = state_rate / season_rate
                    elif league_info == self._ALL:
                        if all_rate == 0:
                            rate_score = 0
                        else:
                            if state_info in rate_list:
                                divide_rate = state_result / all_rate
                            else:
                                divide_rate = state_rate / all_rate
                    distance_rate = divide_rate - 1
                    rate_score = round(abs(distance_rate) * 100, 3)
                    state_data_dict["RATE_SCORE"] = rate_score

                    # Add Positive Negative field.
                    if distance_rate >= 0:
                        if state_info == "SO":
                            state_data_dict["POS_NEG"] = "NEG"
                        else:
                            state_data_dict["POS_NEG"] = "POS"
                    else:
                        if state_info == "SO":
                            state_data_dict["POS_NEG"] = "POS"
                        else:
                            state_data_dict["POS_NEG"] = "NEG"

                    if state_split in split_list:
                        new_data_list.append(state_data_dict)
                    elif rate_score > self._PRE_THRESHOLD:
                        if state_split not in rate_list and state_result != 1:
                            compare_temp_list.append([rate_score, state_split, state_data_dict])
                        elif state_split in rate_list:
                            compare_temp_list.append([rate_score, state_split, state_data_dict])
                    elif state_split == "BASIC":
                        compare_temp_list.append([rate_score, state_split, state_data_dict])

                if compare_temp_list:
                    compare_temp_list.sort(key=lambda x: x[0], reverse=True)
                    temp_dict = {}
                    for state_data_list in compare_temp_list:
                        data_split = state_data_list[1]
                        if data_split not in temp_dict:
                            temp_dict[data_split] = state_data_list[2]

                    new_data_list.extend(list(temp_dict.values()))
                # add group code
            try:
                for new_dict in new_data_list:
                    if subject == self._HITTER_PLAY_EVENT:
                        new_dict["DATA_GROUP"] = self._HITTER_PLAY_EVENT + "_" + new_dict['STATE']
                    else:
                        new_dict["DATA_GROUP"] = new_dict['HITTER'] + "_" + new_dict['STATE_SPLIT']
            except Exception as ex:
                print(ex)

            return new_data_list
        elif subject == self._PITCHER_EVENT:
            # add group code
            for data_dict in data_list:
                data_dict["DATA_GROUP"] = data_dict['PITCHER'] + "_" + data_dict['STATE_SPLIT']
            return data_list
        elif subject == self._TODAY_EVENT:
            # add group code
            for data_dict in data_list:
                data_dict["DATA_GROUP"] = self._TODAY_EVENT + "_" + data_dict['STATE_SPLIT']
            return data_list
        else:
            # add group code
            for data_dict in data_list:
                try:
                    data_dict["DATA_GROUP"] = self._COMMON_EVENT + "_" + data_dict['STATE_SPLIT']
                except Exception as ex:
                    print(data_dict)
            return data_list
    # endregion

    # region 타자 관련 함수
    def get_hitter_basic_record_data(self, hitter, game_id):
        result_list = []
        rank_basic_record = []

        today_record = self.curr_hitter.get_hitter_today_data(game_id)
        if today_record:
            result_list.extend(today_record)

        basic_record = self.curr_hitter.get_hitter_basic_data(hitter)
        if basic_record:
            for basic_dict in basic_record:
                if basic_dict['RANK'] < 11:
                    rank_basic_record.append(basic_dict)
            result_list.extend(rank_basic_record)
            nine_record = self.curr_hitter.get_nine_record(basic_record)
            if nine_record:
                result_list.extend(nine_record)

            ranker_record = self.curr_hitter.get_ranker_record(basic_record)
            if ranker_record:
                result_list.extend(ranker_record)

        return result_list

    def get_hitter_split_record_data(self, live_dict, state_event=None):
        """
        hitter 의 기록을 가져와 dictionary 로 만든다.
        :param live_dict:
        :param state_event:
        :return:
        """
        hitter = live_dict['hitter']
        pitcher = live_dict['pitcher']
        pit_team = live_dict['pitteam']
        score = live_dict['score']
        base = live_dict['base']
        result_list = []
        state_iterator = [state_event]

        if state_event is not None and state_event in self._HIT:
            state_iterator.append("HIT")

        for event in state_iterator:
            # HITTER 의 전체 기본 기록
            if event:
                basic_record = self.curr_hitter.get_hitter_basic_data(hitter, event)
                if basic_record:
                    result_list.extend(basic_record)
                    nine_record = self.curr_hitter.get_nine_record(basic_record)
                    if nine_record:
                        result_list.extend(nine_record)
                    ten_record = self.curr_hitter.get_ten_record(basic_record)
                    if ten_record:
                        result_list.extend(ten_record)
                    if self.curr_hitter.prev_total_record:
                        point_record = self.curr_hitter.get_point_record(basic_record, self.curr_hitter.prev_total_record)
                        if point_record:
                            result_list.extend(point_record)

                        change_rank_record = self.curr_hitter.get_change_rank_record(basic_record,
                                                                         self.curr_hitter.prev_total_record)
                        if change_rank_record:
                            result_list.extend(change_rank_record)

                    ranker_record = self.curr_hitter.get_ranker_record(basic_record)
                    if ranker_record:
                        result_list.extend(ranker_record)

            # hitter vs pitcher 기록
            hitter_vs_pitcher_record = self.curr_hitter.get_hitter_vs_pitcher_data(hitter, pitcher, event)
            if hitter_vs_pitcher_record:
                result_list.extend(hitter_vs_pitcher_record)

            # hitter vs pitteam 기록
            hitter_vs_team_record = self.curr_hitter.get_hitter_vs_team_data(hitter, pit_team, event)
            if hitter_vs_team_record:
                result_list.extend(hitter_vs_team_record)

            # hitter 점수차 기록
            hitter_score_record = self.curr_hitter.get_hitter_score_data(hitter, score, event)
            if hitter_score_record:
                result_list.extend(hitter_score_record)

            # hitter 주자상황 기록
            hitter_base_record = self.curr_hitter.get_hitter_base_data(hitter, base, event)
            if hitter_base_record:
                result_list.extend(hitter_base_record)

            if event and event in ['HIT', 'HR', 'RBI']:
                # N 경기 연속기록 / N 타석 연속기록
                n_continue_record = self.curr_hitter.get_hitter_n_continue_data(event)
                if n_continue_record:
                    result_list.extend(n_continue_record)

        if result_list:
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
        data_dict = {'HITTER': hitter, 'OPPONENT': 'NA', 'LEAGUE': 'NA', 'PITCHER': 'NA', 'PITNAME': 'NA',
                     'GYEAR': 'NA', 'PITTEAM': 'NA', 'STATE_SPLIT': 'FIRSTBALL'}

        result = []
        first_ball_data = self.recorder.get_hitter_first_ball(hitter)

        if first_ball_data:
            first_ball_info = first_ball_data[0]

            if ball_type == 'S':
                if first_ball_info['T_CNT_RNK'] < 30:
                    first_ball_dict = data_dict.copy()
                    first_ball_dict['HITNAME'] = first_ball_info['HITNAME']
                    first_ball_dict['RANK'] = 1
                    first_ball_dict['STATE'] = '0S'
                    first_ball_dict['PA'] = first_ball_info['PA']
                    first_ball_dict['RESULT'] = first_ball_info['T_CNT_RNK']  # 아무데이터
                    result.append(first_ball_dict)

            elif ball_type == 'T':
                if first_ball_info['S_CNT_RNK'] < 30:
                    first_ball_dict = data_dict.copy()
                    first_ball_dict['HITNAME'] = first_ball_info['HITNAME']
                    first_ball_dict['RANK'] = 1
                    first_ball_dict['STATE'] = '0T'
                    first_ball_dict['PA'] = first_ball_info['PA']
                    first_ball_dict['RESULT'] = first_ball_info['S_CNT_RNK']  # 아무데이터
                    result.append(first_ball_dict)

        if result:
            self.set_score(self._COMMON_EVENT, result)
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
            if key == self._HITTER_EVENT:
                subject = self._HITTER_EVENT
            elif key == self._HITTER_PLAY_EVENT:
                subject = self._HITTER_PLAY_EVENT
            # 투수 등판 시
            elif key == self._PITCHER_EVENT:
                subject = self._PITCHER_EVENT
            # 경기장 상황
            elif key == self._TODAY_EVENT:
                subject = self._TODAY_EVENT

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
            if data_dict['STATE_SPLIT'][:6] == 'VERSUS':
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
        db_my_conn = db.MySqlConnector(host=self._HOST, port=self._PORT, user=self._USER, pw=self._PASSWORD,
                                       db=self._DB)
        query = "select ball, stuff, speed, zonex, zoney, x, y from baseball.pitzone " \
                "where gmkey = '{0}' and batorder = '{1}' and ballcount = '{2}' and " \
                "batter = '{3}' and pitcher = '{4}' limit 1".format(game_key, bat_order, ball_count, hitter, pitcher)
        data_list = db_my_conn.select(query, use_dict=True)

        if data_list:
            pitch_data = data_list[0]

            if pitch_data['stuff'] in self._BALL_STUFF:
                pitch_type = self._BALL_STUFF[pitch_data['stuff']]
                if pitch_data['stuff'] in self.continue_ball_stuff:
                    self.continue_ball_stuff[pitch_data['stuff']] += 1
                else:
                    self.continue_ball_stuff.clear()
                    self.continue_ball_stuff[pitch_data['stuff']] = 1
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
                if 45 < area_x < 180 and 60 < area_y < 230:
                    comment = '스트라이크 같았는데요. '
            elif ball_type == 'T':  # 기다린 스트라이크
                if hit_type == '우타':  # 우타
                    if zone_x == 1 or zone_x == 2:  # 바깥쪽 스트라이크
                        if 45 < area_x < 60:
                            comment = '바깥쪽 꽉찬 스트라이크 '
                        else:
                            comment = '바깥쪽 스트라이크 '
                    elif zone_x == 6 or zone_x == 7:  # 몸쪽 스트라이크
                        if 210 < area_x < 235:
                            comment = '몸쪽 꽉찬 스크라이크 '
                        else:
                            comment = '몸쪽 스트라이크 '
                else:  # 좌타
                    if zone_x == 1 or zone_x == 2:  # 몸쪽 스트라이크
                        if 45 < area_x < 60:
                            comment = '몸쪽 꽉찬 스크라이크 '
                        else:
                            comment = '몸쪽 스트라이크 '
                    elif zone_x == 6 or zone_x == 7:  # 바깥쪽 스트라이크
                        if 210 < area_x < 235:
                            comment = '바깥쪽 꽉찬 스트라이크 '
                        else:
                            comment = '바깥쪽 스트라이크 '
            elif ball_type == 'S':  # 헛스윙
                if zone_y < 6:
                    comment = '낮은 공이였는데 휘둘렀어요. '

            result = [{'SUBJECT': 'PITCHER', 'OPPONENT': 'NA', 'LEAGUE': 'NA', 'PITCHER': pitcher, 'PITNAME': 'NA',
                       'GYEAR': 'NA', 'PITTEAM': 'NA', 'STATE': 'BALLINFO', 'STATE_SPLIT': 'BALLINFO',
                       'COMMENT': comment, 'HITTER': hitter, 'STUFF': pitch_type,  'SPEED': pitch_data['speed'],
                       'RANK': 1}]

            return result
        else:
            return None

    def get_current_game_info(self, live_dict):
        result_list = []
        data_dict = {'OPPONENT': 'NA', 'LEAGUE': 'NA', 'PITCHER': 'NA', 'PITNAME': 'NA',
                     'GYEAR': 'NA', 'PITTEAM': 'NA', 'STATE_SPLIT': 'CURRENT_INFO'}
        score_detail = live_dict['score_detail']
        base_detail = live_dict['base_detail']
        out_count = live_dict['out_count']
        bat_order = live_dict['batorder']
        ball_count = live_dict['ballcount']
        text_style = live_dict['textStyle']
        full_count = live_dict['full_count']
        ball_type = live_dict['ball_type']
        hit_team = live_dict['hitteam']

        # region 등판시 주루상황, 점수상황, 아웃상황
        if bat_order > 1 and ball_count == 0 and text_style == 8:
            self.continue_ball_count_b = 0  # 연속 볼
            self.continue_ball_count_f = 0  # 연속 파울
            self.continue_ball_stuff.clear()
            if out_count == 0:
                out = '노'
            elif out_count == 1:
                out = '원'
            else:
                out = '투'

            if base_detail == '0B':
                base = '없는 상황'
            elif base_detail == '1B':
                base = '1루'
            elif base_detail == '2B':
                base = '2루'
            elif base_detail == '3B':
                base = '3루'
            elif base_detail == '12B':
                base = '1,2루'
            elif base_detail == '13B':
                base = '1,3루'
            elif base_detail == '23B':
                base = '2,3루'
            else:
                base = '만루'

            if score_detail == '0D':
                score = '동점인 상황'
            else:
                if score_detail[1] == 'L':
                    score_temp = " 이기고 있는 상황"
                else:
                    score_temp = " 지고 있는 상황"
                score = "{0}점차로 {1}".format(score_detail[0], score_temp)

            current_game = data_dict.copy()
            current_game['LEAGUE'] = 'SEASON'
            current_game['STATE'] = 'CURRENT_INFO'
            current_game['out'] = out
            current_game['base'] = base
            current_game['score'] = score

            result_list.append(current_game)
        # endregion

        # region Ball Count 설명
        if text_style == 1:
            if ball_type == 'S' or ball_type == 'T':
                strike_counting = full_count[1]
                if strike_counting == 1:
                    print("캐스터: 원스트라이크")
                elif strike_counting == 2:
                    print("캐스터: 투스트라이크")
            elif ball_type == 'B':
                ball_counting = full_count[0]
                if ball_counting == 1:
                    print("캐스터: 원볼")
                elif ball_counting == 2:
                    print("캐스터: 투볼")
                elif ball_counting == 3:
                    print("캐스터: 스리볼")
        # endregion

        # region Full count
        if full_count[0] == 2 and full_count[1] == 3 and text_style == 1:
            full_count_dict = data_dict.copy()
            full_count_dict['LEAGUE'] = 'SEASON'
            full_count_dict['STATE'] = 'FULL_COUNT'
            result_list.append(full_count_dict)
        # endregion

        # region 연속 볼, 연속 파울 설정
        if ball_type == 'B' and text_style == 1:
            self.continue_ball_count_b += 1
            self.continue_ball_count_f = 0
        elif ball_type == 'F' and text_style == 1:
            self.continue_ball_count_f += 1
            self.continue_ball_count_b = 0
        else:
            self.continue_ball_count_b = 0
            self.continue_ball_count_f = 0

        if self.continue_ball_count_b > 2 and self.continue_ball_count_b < 4:
            continue_ball_dict = data_dict.copy()
            continue_ball_dict['LEAGUE'] = 'SEASON'
            continue_ball_dict['STATE'] = 'CONTINUE_BALL'
            continue_ball_dict['type'] = '볼'
            continue_ball_dict['count'] = self.continue_ball_count_b
            result_list.append(continue_ball_dict)
        elif self.continue_ball_count_f > 2:
            continue_ball_dict = data_dict.copy()
            continue_ball_dict['LEAGUE'] = 'SEASON'
            continue_ball_dict['STATE'] = 'CONTINUE_BALL'
            continue_ball_dict['type'] = '파울'
            continue_ball_dict['count'] = self.continue_ball_count_f
            result_list.append(continue_ball_dict)
        # endregion

        # region 연속 같은 볼
        if ball_type == 'H':
            self.continue_ball_stuff.clear()
        else:
            ball_stuff_value_list = list(self.continue_ball_stuff.values())
            ball_stuff_key_list = list(self.continue_ball_stuff.keys())
            if ball_stuff_value_list and ball_stuff_value_list[0] > 2:
                ball_stuff_dict = data_dict.copy()
                ball_stuff_dict['LEAGUE'] = 'SEASON'
                ball_stuff_dict['STATE'] = 'BALL_STUFF_COUNT'
                ball_stuff_dict['count'] = ball_stuff_value_list[0]
                ball_stuff_dict['ball_type'] = self._BALL_STUFF[ball_stuff_key_list[0]]
                result_list.append(ball_stuff_dict)
        # endregion

        return result_list
    # endregion
