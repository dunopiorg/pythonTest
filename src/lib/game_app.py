from datetime import datetime
from math import exp, log
from lib import DBConnection as db
from lib import message_maker
from lib import player
from lib import record
from lib import commentate
from lib import message_teller
from lib import score_table
from lib import game_status
from lib import message_log
from korean import Noun
import config
import time
import korean


class GameApp(object):
    __HOST = config.DB_HOST
    __USER = config.DB_USER
    __PASSWORD = config.DB_PASSWORD
    __DB = config.DB_NAME
    __PORT = config.DB_PORT

    # region Initialize 필요한 정보
    def __init__(self, game_key):
        # database connection 상수 정보
        self.HOST = config.DB_HOST
        self.USER = config.DB_USER
        self.PASSWORD = config.DB_PASSWORD
        self.DB = config.DB_NAME
        self.PORT = config.DB_PORT

        # state 상수 정보
        self.HIT_LIST = ['H1', 'H2', 'H3', 'HR', 'HI', 'HB']
        self.HR_LIST = ['HR']
        self.BB_LIST = ['BB', 'IB']
        self.SO_LIST = ['KK', 'KN', 'KB', 'KW', 'KP']
        self.PA_LIST = ['H1', 'H2', 'H3', 'HR', 'HI', 'HB', 'BB', 'IB', 'HP', 'KK', 'KN', 'KB'
							,'KW','KP','IN','OB','IP','XX','SH','SF','FC','GD','TP','GR','BN','FL','LL','IF','FF']
        self.TEAM_KOR_DICT = {"WO": "넥센", "SS": "삼성", "SK": "SK", "OB": "두산",
                         "NC": "NC", "LT": "롯데", "LG": "LG", "KT ": "KT", "HT": "기아", "HH": "한화"}

        # 기본 전역 변수
        self.prev_pitcher = None
        self.prev_hitter = None
        self.curr_hitter = None
        self.curr_pitcher = None
        self.hitter_category_score = {}
        self.pitcher_category_score = {}
        self.common_category_score = {}
        self.starting_category_score = {}
        self.pitcher_mound_list =[]

        # 기본 전역 상수
        self.LEAGUE_SEASON_SCORE = 4
        self.LEAGUE_ALL_SCORE = 3
        self.PRE_THRESHOLD = 70
        self.SEASON = "SEASON"
        self.ALL = "ALL"
        self.HITTER_STARTING_SPLIT = "HITTER_STARTING_SPLIT"
        self.PITCHER_EVENT = "PITCHER_EVENT"
        self.COMMON_EVENT = "COMMON_EVENT"
        self.HITTER_EVENT = "HITTER_EVENT"
        self.HITTER_STARTING = "HITTER_STARTING"
        self.PITCHER_STARTING = "PITCHER_STARTING"
        self.PITCHER_ON_MOUND = "PITCHER_ON_MOUND"

        # 기본 전역 객체 변수
        self.recorder = record.Record()
        self.msg_maker = message_maker.MessageMaker()
        self.commentator = commentate.Commentate()
        self.score_table = score_table.ScoreTable()
        self.msg_teller = message_teller.MsgTeller()
        self.game_status = game_status.GameStatus(game_key)
        self.logger = message_log.MsgLog()

        # initialize data
        self.set_category_score()

    def set_category_score(self):
        """
        이벤트 카테고리 별 점수
        :return:  category score dictionary
        """
        db_my_conn = db.MySqlConnector(host=self.HOST, port=self.PORT, user=self.USER, pw=self.PASSWORD,
                                       db=self.DB)
        query = "select event, state_split, category, score from baseball.event_score"
        rows = db_my_conn.select(query, True)
        for row in rows:
            if row["event"] == self.HITTER_STARTING_SPLIT:
                self.hitter_category_score.update({row["category"]: row["score"], "state_split": row["state_split"]})
            elif row["event"] == self.PITCHER_EVENT:
                self.pitcher_category_score.update({row["category"]: row["score"], "state_split": row["state_split"]})
            elif row["event"] == self.COMMON_EVENT:
                self.common_category_score.update({row["category"]: row["score"], "state_split": row["state_split"]})
            elif row["event"] == self.HITTER_STARTING:
                self.starting_category_score.update({row["category"]: row["score"], "state_split": row["state_split"]})

    @classmethod
    def test_live_data(cls, game_id):
        """
        Live가 아닌 Local Test를 위한 함수. getLiveData()로 대체될 것.
        :param game_id:
        :return:
        """
        db_my_conn = db.MySqlConnector(host=cls.__HOST, port=cls.__PORT,
                                       user=cls.__USER, pw=cls.__PASSWORD, db=cls.__DB)
        query = "SELECT (SELECT NAME FROM baseball.person WHERE A.pitcher = PCODE) AS PITCHER_NAME " \
                ", (SELECT NAME FROM baseball.person WHERE A.batter = PCODE) AS batter_name " \
                ", (SELECT NAME FROM baseball.person WHERE A.catcher = PCODE) AS catcher_name " \
                ", (SELECT NAME FROM baseball.person WHERE A.runner = PCODE) AS runner_name " \
                ", A.* " \
                "FROM baseball.ie_livetext_score_mix A " \
                "WHERE A.gameID = '%s' " \
                "ORDER BY seqNo" % game_id

        live_data = db_my_conn.select(query, True)
        return live_data
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

        live_dict = self.game_status.get_live_text_info(live_text_dict)
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
        inning= live_text_dict['inning']
        pitname = live_dict['pitname']
        is_statring = False
        if inning == 99:
            return None
        self.game_status.set_gamecontapp_info(hitter, pitcher, inning, how)

        # region 게임 시작 정보 (경기장, 심판, 날씨 등)
        if seq_num == 0:
            game_info_data = self.commentator.get_game_info(game_id)
            if game_info_data:
                self.set_score(self.COMMON_EVENT, game_info_data)
            # team_info_data = self.commentator.get_team_info(self.game_status.team_info)
            # if team_info_data:
            #     self.set_score(self.COMMON_EVENT, team_info_data)
        # endregion

        # region 게임 진행 중계 정보 (대부분)
        if bat_order == 0 and inning == 1:
            starting_line_data = self.commentator.get_starting_line_info(live_dict['tb'], self.game_status.starting_line_up)
            if starting_line_data:
                self.set_score(self.COMMON_EVENT, starting_line_data)

        current_game_info = self.commentator.get_current_game_info(live_dict)
        if current_game_info:
            self.set_score(self.COMMON_EVENT, current_game_info)

        how_event_info = self.game_status.get_explain_how_event(hitter, pitcher, inning, how)
        if how_event_info:
            self.set_score(self.COMMON_EVENT, how_event_info)
        # endregion

        # region [기록] 투수 등판 또는 교체시 투수 등록 및 투수의 기록을 가져온다.
        if pitcher:
            is_statring = self.game_status.is_starting_pitcher(live_dict['tb'], pitcher)
        if is_statring and pitcher not in self.pitcher_mound_list:  # 선발등판
            self.pitcher_mound_list.append(pitcher)
            self.curr_pitcher = player.Pitcher(pitcher)
            pitcher_starting = self.get_pitcher_record_data(pitcher, live_dict['hitteam'])
            if pitcher_starting:
                result_pitcher.update({self.PITCHER_STARTING: pitcher_starting})
        elif pitcher and pitcher not in self.pitcher_mound_list:
            self.pitcher_mound_list.append(pitcher)
            self.prev_pitcher = self.curr_pitcher
            self.curr_pitcher = player.Pitcher(pitcher)
            pitcher_list = self.get_pitcher_record_data(pitcher, live_dict['hitteam'], batter)
            if pitcher_list:
                result_pitcher.update({self.PITCHER_ON_MOUND: pitcher_list})
        # endregion [기록] 투수 등판 또는 교체시 투수 등록 및 투수의 기록을 가져온다.

        # region [기록] 타자 등판 또는 교체시 타자 등록
        if batter and self.curr_hitter is None:
            self.curr_hitter = player.Hitter(batter)
        elif self.curr_hitter is not None and batter != self.curr_hitter.player_code:
            self.prev_hitter = self.curr_hitter
            self.curr_hitter = player.Hitter(batter)

        if text_style == 8:
            self.prev_hitter = self.curr_hitter
            # HITTER 의 오늘 기록 및 통산 기록
            today_record = self.get_hitter_basic_record_data(batter, game_id)
            if today_record:
                result_today.update({self.HITTER_STARTING: today_record})
            # HITTER의 상황별 기록
            hitter_list = self.get_hitter_split_record_data(live_dict)
            if hitter_list:
                result_hitter.update({self.HITTER_STARTING_SPLIT: hitter_list})
            self.curr_hitter.set_prev_total_record()  #total 기록을 previous 기록으로 복사
        # endregion [기록] 타자 등판 또는 교체시 타자 등록

        # region 구종 정보
        if text_style == 1 and live_state_sc == 1 and ball_type != 'H' and ball_type != 'F':
            ball_style_dict = self.commentator.get_ball_style_data(game_id, bat_order, ball_count,
                                                       pitcher, hitter, self.curr_hitter.hit_type, pitname)
            if ball_style_dict:
                self.set_score(self.COMMON_EVENT, ball_style_dict)
        # endregion

        # region 초구 정보
        if ball_count == 1 and ball_type not in ('F', 'H') and text_style == 1:
            first_ball_result = self.commentator.get_first_ball_info(self.curr_hitter.player_code, ball_type)
            if first_ball_result:
                self.set_score(self.COMMON_EVENT, first_ball_result)
        # endregion

        # region [기록] Hitter How Event 발생
        if text_style == 13 or text_style == 23:
            how_event = None
            hitter_record = None

            # region Update Hitter Record
            if how in self.HIT_LIST:
                if how == 'H2' or how == 'H3':
                    how_event = how
                    self.curr_hitter.update_hitter_record(how_event, live_dict)  # update H2 or H3 기록
                elif how in self.HR_LIST:
                    how_event = 'HR'
                    self.curr_hitter.update_hitter_record(how_event, live_dict)  # update HR 기록
                else:
                    how_event = 'HIT'
                    self.curr_hitter.update_hitter_record(how_event, live_dict)  # update HIT 기록
            elif how in self.BB_LIST:
                how_event = 'BB'
                self.curr_hitter.update_hitter_record(how_event, live_dict)  # update BB 기록
            elif how in self.SO_LIST:
                how_event = 'SO'
                self.curr_hitter.update_hitter_record(how_event, live_dict)  # update SO 기록
            # endregion Update Hitter Record

            if how_event:
                hitter_record = self.get_hitter_split_record_data(live_dict, how_event)
                if hitter_record:
                    result_hit_event.update({self.HITTER_EVENT: hitter_record})

        if how in self.PA_LIST:
            self.curr_hitter.update_hitter_pa_record(live_dict)  # update PA count
        # endregion [기록] Hitter How Event 발생

        # region [기록] Pitcher How Event
        if how:
            pitcher_event = self.get_pitcher_record_data(pitcher, live_dict['hitteam'], batter, how)
            # pitcher_event = self.curr_pitcher.get_how_event_data(how, hitter, live_dict['hitteam'])
            if pitcher_event:
                result_pitcher.update({self.PITCHER_EVENT: pitcher_event})
        # endregion [기록] Pitcher How Event

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

    # region Score Table Queue Functions
    def put_score_table(self, msg):
        """
        Score Table 에 넣는다.
        :param msg: 생성된 Message
        :return:
        """
        data = msg

        # for d in data:
        #    print(d)
        while True:
            if self.score_table.get_async() == 0:
                self.score_table.set_async(1)
                self.score_table.put(data)
                self.score_table.set_async(0)
                break

    def score_thread(self):
        """
        Queue 에서 뺀 후에 Decreasing 한다. [Thread]
        :return:
        """
        while True:
            if self.score_table.is_ready():
                parameter_list = []
                event_group = ''
                event = ''

                event, event_group, parameter_list = self.score_table.get_group()

                if parameter_list:
                    msg = None
                    if event == self.PITCHER_EVENT:
                        msg = self.msg_maker.get_pitcher_message(event, parameter_list)
                    elif event == self.PITCHER_STARTING:
                        msg = self.msg_maker.get_pitcher_starting_message(event, parameter_list)
                    elif event == self.PITCHER_ON_MOUND:
                        msg = self.msg_maker.get_pitcher_on_mound_message(event, parameter_list)
                    elif event == self.HITTER_EVENT:
                        msg = self.msg_maker.get_hit_event_message_new(event, parameter_list)
                    elif event == self.HITTER_STARTING:
                        if parameter_list[0][3] == self.HITTER_STARTING + "_BASIC":
                            msg = self.msg_maker.get_today_basic_event_message(event, parameter_list)
                        else:
                            msg = self.msg_maker.get_today_event_message(event, parameter_list)
                    elif event == self.HITTER_STARTING_SPLIT:
                        #  msg = self.msg_maker.get_hitter_message(parameter_list)
                        # msg = self.msg_maker.get_hitter_split_message(event, parameter_list)
                        msg = self.msg_maker.get_hitter_split_message_v2(event, parameter_list)
                    elif event == self.COMMON_EVENT:
                        msg = self.msg_maker.get_common_message(event, parameter_list)

                    if msg:
                        if event == self.PITCHER_EVENT or event == self.PITCHER_STARTING or event == self.PITCHER_ON_MOUND:
                            subject = self.curr_pitcher.player_code
                        elif event == self.HITTER_EVENT or event == self.HITTER_STARTING or event == self.HITTER_STARTING_SPLIT:
                            subject = self.curr_hitter.player_code
                        else:
                            subject = 'COMMENTATOR'
                        msg_dict = {'log_kind': event, 'subject': subject, 'game_id': self.game_status.game_key, 'message': msg,
                                    'group_id': event_group, 'parameters': parameter_list[0][4], 'inning': self.game_status.inning}
                        self.put_message_table(msg_dict)
                    else:
                        print(msg)

                self.score_table.clear_none()
    # endregion

    # region Message Table Queue Functions
    def put_message_table(self, msg_dict, is_front=False):
        if is_front:
            self.msg_teller.put_front(msg_dict)  #Queue의 가장 앞에 넣는다.
        else:
            self.msg_teller.put_rear(msg_dict)  #Queue의 마지막에 넣는다.

    def message_thread(self):
        while True:
            message_dict = self.msg_teller.say()
            if message_dict:
                if message_dict['log_kind'] == self.COMMON_EVENT:
                    self.logger.insert_log(message_dict)
                    print("캐스터: ", message_dict['message'].rstrip('\n'))
                else:
                    msg_count = self.logger.get_count(message_dict)[0]
                    if int(msg_count['count']) == 0:
                        self.logger.insert_log(message_dict)
                        print("캐스터: ", message_dict['message'].rstrip('\n'))
    # endregion

    # region 기능 관련 Functions
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
                league_score = self.LEAGUE_ALL_SCORE
            else:
                league_score = self.LEAGUE_SEASON_SCORE

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
                league_score = self.LEAGUE_ALL_SCORE
            else:
                league_score = self.LEAGUE_SEASON_SCORE

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
                league_score = self.LEAGUE_ALL_SCORE
            else:
                league_score = self.LEAGUE_SEASON_SCORE

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

    def starting_score_generator(self, data_dict):
        result = None
        state_score_val = 0
        league_score = 0
        event_score = 100
        if 'STATE' in data_dict:
            if 'LEAGUE' in data_dict and data_dict['LEAGUE'] == 'ALL':
                league_score = self.LEAGUE_ALL_SCORE
            else:
                league_score = self.LEAGUE_SEASON_SCORE

            state_split = data_dict['STATE_SPLIT']

            if state_split in self.starting_category_score:
                state_score_val = self.starting_category_score.get(state_split)
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

        # region History 관리
        # endregion

        for data_dict in pre_scored_list:
            if event == self.HITTER_STARTING_SPLIT or event == self.HITTER_EVENT:
                score = self.hitter_score_generator(data_dict)
            elif event == self.PITCHER_EVENT:
                score = self.pitcher_score_generator(data_dict)
            elif event == self.COMMON_EVENT:
                score = self.common_score_generator(data_dict)
            elif event == self.HITTER_STARTING:
                score = self.starting_score_generator(data_dict)
            else:
                score = self.common_score_generator(data_dict)

            if score:
                try:
                    score_data.append([score, event, data_dict["STATE_SPLIT"], data_dict["DATA_GROUP"], data_dict])
                except Exception as ex:
                    print(ex)
        if score_data:
            self.put_score_table(score_data)

    def pre_score_generator(self, subject, data_list):
        if subject == self.HITTER_STARTING_SPLIT or subject == self.HITTER_EVENT:
            state_group_data = {}
            compare_temp_list = []
            new_data_list = []
            state_list = ["BB", "H2", "HIT", "HRA", "SO", "OBA", "RBI", "SLG", "H3", "HR"]
            rate_list = ["HRA", "OBA", "SLG"]
            split_list = ["1UNIT", "RANKER", "NPA", "NGAME"]

            for state in state_list:
                temp_list = [data_dict for data_dict in data_list if state == data_dict['STATE'] and data_dict['RESULT'] > 0]
                if temp_list:
                    state_group_data[state] = temp_list

            season_rate = 0
            all_rate = 0
            # total, season 기본 rate 구성
            for state_key, state_data_list in state_group_data.items():
                compare_temp_list = []
                hitter_total_list = self.curr_hitter.get_hitter_basic_data(self.curr_hitter.player_code, state_key)
                if hitter_total_list:
                    for hitter_total in hitter_total_list:
                        if hitter_total['LEAGUE'] == self.SEASON:
                            if hitter_total["STATE"] in rate_list:
                                season_rate = hitter_total["RESULT"]
                            else:
                                season_rate = hitter_total['RATE']
                        else:
                            if hitter_total["STATE"] in rate_list:
                                all_rate = hitter_total["RESULT"]
                            else:
                                all_rate = hitter_total['RATE']

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

                    if league_info == self.SEASON:
                        if season_rate == 0:
                            rate_score = 0
                        else:
                            if state_info in rate_list:
                                divide_rate = state_result / season_rate
                            else:
                                divide_rate = state_rate / season_rate
                    elif league_info == self.ALL:
                        if all_rate == 0:
                            rate_score = 0
                        else:
                            if state_info in rate_list:
                                divide_rate = state_result / all_rate
                            else:
                                divide_rate = state_rate / all_rate
                    pos_neg = divide_rate - 1
                    rate_score = round(abs(pos_neg) * 100)
                    state_data_dict["RATE_SCORE"] = rate_score

                    # Add Positive Negative field.
                    if divide_rate >= 0:
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
                    elif rate_score > self.PRE_THRESHOLD:
                        if state_info not in rate_list and state_result > 2:
                            compare_temp_list.append([rate_score, state_split, state_data_dict])
                        elif state_info in rate_list:
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
                    new_dict["DATA_GROUP"] = subject + "_" + new_dict['STATE']
            except Exception as ex:
                print(ex)

            return new_data_list
        elif subject == self.PITCHER_EVENT:
            new_data_dict = {}

            for data_dict in data_list:
                if data_dict['STATE_SPLIT'] == 'BASIC':
                    if data_dict['STATE_SPLIT'] not in new_data_dict:
                        new_data_dict[data_dict['STATE_SPLIT']] = data_dict
                    else:
                        if data_dict['STATE'] == 'SO':
                            if new_data_dict[data_dict['STATE_SPLIT']]['RATE'] < data_dict['RATE']:
                                new_data_dict[data_dict['STATE_SPLIT']] = data_dict
                        else:
                            if new_data_dict[data_dict['STATE_SPLIT']]['RATE'] > data_dict['RATE']:
                                new_data_dict[data_dict['STATE_SPLIT']] = data_dict
                elif data_dict['STATE_SPLIT'] == 'VERSUS_TEAM':
                    if data_dict['LEAGUE'] == 'SEASON' and data_dict['RESULT'] % 10 == 0:
                        new_data_dict[data_dict['STATE_SPLIT']] = data_dict
                    elif data_dict['LEAGUE'] == 'ALL' and data_dict['RESULT'] % 100 == 0:
                        new_data_dict[data_dict['STATE_SPLIT']] = data_dict
                else:
                    new_data_dict[data_dict['STATE_SPLIT']] = data_dict
            new_data_list = list(new_data_dict.values())
            # add group code
            for data_dict in new_data_list:
                data_dict["DATA_GROUP"] = self.PITCHER_EVENT + "_" + data_dict['STATE_SPLIT']
            return new_data_list
        elif subject == self.PITCHER_STARTING or subject == self.PITCHER_ON_MOUND:
            # 기록이 0이상인 시즌 기록
            # 시즌 기록과 비교해서 상당히 차이나는 기록만?
            new_data_list = []
            for data_dict in data_list:
                if data_dict['LEAGUE'] == self.SEASON and data_dict['STATE'] == "STARTING":
                    new_data_list.append(data_dict)
                else:
                    if data_dict['LEAGUE'] == self.SEASON:
                        if data_dict['RESULT'] > 0:
                            new_data_list.append(data_dict)
                        elif data_dict['STATE'] == 'LOSSES' or data_dict['STATE'] == 'WINS':
                            data_dict['RESULT'] = '무'
                            new_data_list.append(data_dict)
            for new_data_dict in new_data_list:
                new_data_dict["DATA_GROUP"] = subject + "_" + new_data_dict['STATE_SPLIT']
            return new_data_list
        elif subject == self.HITTER_STARTING: #todo
            new_data_list = []
            for data_dict in data_list:
                if data_dict['LEAGUE'] == self.SEASON or data_dict['LEAGUE'] == 'TODAY':
                    new_data_list.append(data_dict)
            # add Today group code
            for data_dict in new_data_list:
                data_dict["DATA_GROUP"] = self.HITTER_STARTING + "_" + data_dict['STATE_SPLIT']
            return new_data_list
        else:
            # add Common  group code
            for data_dict in data_list:
                try:
                    data_dict["DATA_GROUP"] = self.COMMON_EVENT + "_" + data_dict['STATE']
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
            if config.hitter_basic:
                result_list.extend(basic_record)
            nine_record = self.curr_hitter.get_nine_record(basic_record)
            if nine_record:
                result_list.extend(nine_record)

            ranker_record = self.curr_hitter.get_ranker_record(basic_record)
            if ranker_record:
                result_list.extend(ranker_record)

        hitter_game_number = self.curr_hitter.get_hitter_game_number(hitter)
        if hitter_game_number:
            result_list.extend(hitter_game_number)

        return result_list

    def get_hitter_split_record_data(self, live_dict, state_event=None):
        """
        hitter 의 기록을 가져와 dictionary 로 만든다.
        :param live_dict:
        :param state_event:
        :return:
        """
        hitter = live_dict['hitter']
        hitter_name = live_dict['hitname']
        pitcher = live_dict['pitcher']
        pit_team = live_dict['pitteam']
        score = live_dict['score']
        base = live_dict['base']
        game_id = live_dict['game_id']
        result_list = []
        state_iterator = [state_event]

        if state_event is not None and state_event in self.HIT_LIST:
            state_iterator.append("HIT")

        for event in state_iterator:
            # HITTER 의 전체 기본 기록
            if event:
                basic_record = self.curr_hitter.get_hitter_basic_data(hitter, event)
                if basic_record:
                    if config.hitter_basic:
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

                    # ranker_record = self.curr_hitter.get_ranker_record(basic_record)
                    # if ranker_record:
                    #     result_list.extend(ranker_record)

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
                n_continue_record = self.curr_hitter.get_hitter_n_continue_data(game_id, hitter_name, event)
                if n_continue_record:
                    result_list.extend(n_continue_record)

        if result_list:
            return result_list
        else:
            return None
    # endregion

    # region 투수 관련 함수
    def get_pitcher_record_data(self, pitcher, hit_team, hitter=None, state_event=None):
        result_list = []
        how_dict = {'KK': 'SO', 'KN': 'SO', 'KB': 'SO', 'KW': 'SO', 'KP': 'SO',
                    # 'H1': 'HIT', 'H2': 'HIT', 'H3': 'HIT', 'HR': 'HIT', 'HI': 'HIT', 'HB': 'HIT',
                    # 'HR': 'HR',
                    # 'BB': 'BB', 'IB': 'BB',
                    # 'HP': 'HP'
                    }

        if state_event is None:
            pitcher_basic_record = self.curr_pitcher.get_pitcher_basic_total_data(pitcher)
            if pitcher_basic_record:
                result_list.extend(pitcher_basic_record)

            prev_game_record = self.curr_pitcher.get_previous_game_pitcher_data(self.game_status.game_key, pitcher)
            if prev_game_record:
                prev_game_record[0]['TEAM'] = self.game_status.TEAM_KOR[prev_game_record[0]['TEAM']]
                result_list.extend(prev_game_record)

            pitcher_game_number = self.curr_pitcher.get_pitcher_game_number(pitcher)
            if pitcher_game_number:
                result_list.extend(pitcher_game_number)
        else:
            if state_event in how_dict:
                basic_record = self.curr_pitcher.get_pitcher_basic_data(pitcher, how_dict[state_event])
                if basic_record:
                    result_list.extend(basic_record)

        if state_event in how_dict:
            pitcher_vs_team_record = self.curr_pitcher.get_pitcher_vs_team_data(pitcher, hit_team, how_dict[state_event])
            if pitcher_vs_team_record:
                result_list.extend(pitcher_vs_team_record)

            if hitter is not None:
                pitcher_vs_hitter_record = self.curr_pitcher.get_pitcher_vs_hitter_data(pitcher, hitter, how_dict[state_event])
                if pitcher_vs_hitter_record:
                    result_list.extend(pitcher_vs_hitter_record)

        if result_list:
            nine_record = self.curr_pitcher.get_pitcher_nine_record(result_list)
            if nine_record:
                result_list.extend(nine_record)

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
            self.set_score(key, value_dict)
    # endregion

    # endregion
