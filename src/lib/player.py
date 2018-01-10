from lib import record
from datetime import  datetime


class Player(object):

    def __init__(self, player_code=None):
        self.player_code = player_code
        self.player_info = {}
        if self.player_code:
            self.recorder = record.Record()
            self.set_player_info()

        self.today_record_dict = {}
        self.total_basic_record_dict = {}
        self.total_split_record_dict = {}

        self.today_record = None
        self.total_record = None
        self.n_continue_record = None

    def set_player_info(self):
        self.player_info = self.recorder.get_personal_info(self.player_code)[0]


class Hitter(Player):

    def __init__(self, player_code=None):
        if player_code:
            Player.__init__(self, player_code)
            if self.player_info:
                self.hit_type = self.player_info['HITTYPE'][2:]
        else:
            Player.__init__(self)

    # region Return Hitter 경기기록
    def get_hitter_today_data(self, game_id):
        """
        오늘 hitter의 경기 기록을 가져온다.
        :param game_id:
        :return:
        """
        result = []
        today_result = record.Record().get_hitter_today_record(game_id, self.player_code)

        if today_result:
            today = {}
            for k, v in today_result[0].items():
                if type(v) == str:
                    today[k] = v
                else:
                    today[k] = int(v)

            data_dict = {'SUBJECT': 'HITTER', 'OPPONENT': 'NA', 'LEAGUE': 'NA', 'PITCHER': 'NA', 'PITNAME': 'NA',
                         'GYEAR': 'NA', 'PITTEAM': 'NA', 'STATE_SPLIT': 'TODAY',
                         'RANK': 1, 'HITTER': self.player_code, 'HITNAME': today['HITNAME'], 'PA': today['PA']}

            for k, v in today.items():
                if k == 'PA' or k == 'HITNAME':
                    continue
                set_dict = data_dict.copy()
                set_dict['STATE'] = k
                set_dict['RESULT'] = v
                result.append(set_dict)

            self.set_today_hitter_dict(today)

        if result:
            self.today_record = result
        return self.today_record

    def get_hitter_basic_data(self):
        self.total_record = self.recorder.get_hitter_basic_record(self.player_code)
        return self.total_record

    def get_hitter_vs_pitcher_data(self, hitter_code, pitcher_code, state=None):
        """
        database에서 hitter vs pitcher 정보를 가져온다.
        :param hitter_code:
        :param pitcher_code:
        :param state:
        :return:
        """
        result = self.recorder.get_hitter_vs_pitcher_record(hitter_code, pitcher_code, state)
        if result:
            return result
        else:
            return None

    def get_hitter_vs_team_data(self, hitter_code, pitcher_team, state=None):
        """
        상대 팀과에 대결 데이터를 가져온다 .
        :param hitter_code:
        :param pitcher_team:
        :param state:
        :return:
        """
        result = self.recorder.get_hitter_vs_team_record(hitter_code, pitcher_team, state)
        if result:
            return result
        else:
            return None

    def get_hitter_score_data(self, hitter_code, score_split, state=None):
        """
        점수상황에 따른 hitter data 를 가져온다.
        :param hitter_code:
        :param score_split:
        :param state:
        :return:
        """
        result = self.recorder.get_hitter_score_record(hitter_code, score_split, state)
        if result:
            return result
        else:
            return None

    def get_hitter_base_data(self, hitter_code, base_split, state=None):
        """
        주자 상황에 따른 hitter 데이터를 가져온다.
        :param hitter_code:
        :param base_split:
        :param state:
        :return:
        """
        result = self.recorder.get_hitter_base_record(hitter_code, base_split, state)
        if result:
            return result
        else:
            return None

    def get_hitter_n_continue_data(self):
        """
        N게임 연속 기록 데이터를 생성한다.
        :return:
        """
        state_dict = {'HIT': ['H1', 'H2', 'H3', 'HR', 'HI', 'HB'], 'HR': ['HR'],
                      'RBI': ['E', 'R', 'H'], 'BB': ['BB', 'IB'], 'KK': ['KK']}
        data_dict = {'SUBJECT': 'HITTER', 'OPPONENT': 'ALL', 'LEAGUE': 'SEASON',
                     'PITCHER': 'NA', 'PITNAME': 'NA', 'PITTEAM': 'NA', 'RANK': 1}
        counter_dict = {'HIT': 0, 'HR': 0, 'RBI': 0, 'BB': 0, 'KK': 0}

        hitter_gm_list = self.recorder.get_hitter_continuous_record(self.player_code)
        result = []
        n_game_data_exist = False
        n_pa_data_exist = False

        # region N경기 데이터
        new_gm_list = []
        how_list = []
        if hitter_gm_list:
            prev_game_key = ''
            for i, d in enumerate(hitter_gm_list):
                if i == 0:
                    prev_game_key = d['GMKEY']
                    how_list.append(d['PLACE'])
                    how_list.append(d['HOW'])
                else:
                    if prev_game_key == d['GMKEY']:
                        how_list.append(d['PLACE'])
                        how_list.append(d['HOW'])
                    else:
                        new_gm_list.append(list(set(how_list)))
                        del how_list[:]
                        how_list.append(d['PLACE'])
                        how_list.append(d['HOW'])
                        prev_game_key = d['GMKEY']

        break_flag = False
        for k_state, v_state in state_dict.items():
            for i, d_how_list in enumerate(new_gm_list):
                for how_data in d_how_list:
                    if how_data in v_state:
                        if i == counter_dict[k_state]:
                            counter_dict[k_state] += 1
                            n_game_data_exist = True
                        if i not in list(counter_dict.values()):
                            break_flag = True
                            break
                if break_flag:
                    break
            if break_flag:
                break

        if n_game_data_exist:
            for count_key, count_value in counter_dict.items():
                if count_value > 1:
                    set_dict = data_dict.copy()
                    set_dict['RESULT'] = count_value
                    set_dict['STATE'] = count_key
                    set_dict['STATE_SPLIT'] = 'NGAME'
                    result.append(set_dict)
        # endregion

        # region N타석 데이터
        for k_state, v_state in state_dict.items():
            how_counter = 0
            for i, d in enumerate(hitter_gm_list):
                d_how = d['HOW']
                if d_how in v_state:
                    how_counter += 1
                elif i > 0:
                    counter_dict[k_state] = how_counter
                    n_pa_data_exist = True
                    break
                else:
                    break
            if how_counter > 0:
                break

        for rbi_state in state_dict['RBI']:
            rbi_counter = 0
            for i, d in enumerate(hitter_gm_list):
                d_place = d['PLACE']
                if d_place in rbi_state:
                    rbi_counter += 1
                elif i > 0:
                    counter_dict['RBI'] = rbi_counter
                    n_pa_data_exist = True
                    break
                else:
                    break
            if rbi_counter == 0:
                break

        if n_pa_data_exist:
            for count_key, count_value in counter_dict.items():
                if count_value > 1:
                    set_dict = data_dict.copy()
                    set_dict['RESULT'] = count_value
                    set_dict['STATE'] = count_key
                    set_dict['STATE_SPLIT'] = 'NPA'
                    result.append(set_dict)
        # endregion

        if result:
            self.n_continue_record = result
            return self.n_continue_record
        else:
            return None

    @classmethod
    def get_nine_record(cls, record_dict_list):
        """
        9단위 기록을 생성한다.
        :param record_dict_list: 받아온 list 에 생성한 기록을 담아서 return 한다 .
        :return:
        """
        categories = ['HIT', 'HR', 'RBI', 'BB']
        for data_dict in record_dict_list:
            if data_dict['STATE'] in categories and data_dict['STATE_SPLIT'] == 'BASIC':
                result_record = data_dict['RESULT']
                league = data_dict['LEAGUE']

                if league == 'SEASON':
                    if result_record % 10 == 9:
                        copy_dict = data_dict.copy()
                        copy_dict['STATE_SPLIT'] = 'UNIT9'
                        record_dict_list.append(copy_dict)
                else:
                    if result_record % 100 == 99:
                        copy_dict = data_dict.copy()
                        copy_dict['STATE_SPLIT'] = 'UNIT99'
                        record_dict_list.append(copy_dict)

    @classmethod
    def get_ten_record(cls, record_dict_list):
        """
        10단위 기록을 생성한다.
        :param record_dict_list: 생성된 기록은 받아온 list 에 더해진다 .
        :return:
        """
        categories = ['HIT', 'HR', 'RBI', 'BB']
        for data_dict in record_dict_list:
            if data_dict['STATE'] in categories and data_dict['STATE_SPLIT'] == 'BASIC':
                result_record = data_dict['RESULT']
                league = data_dict['LEAGUE']

                if league == 'SEASON' and result_record != 0:
                    if result_record % 10 == 0:
                        copy_dict = data_dict.copy()
                        copy_dict['STATE_SPLIT'] = 'UNIT10'
                        record_dict_list.append(copy_dict)
                else:
                    if result_record % 100 == 0:
                        copy_dict = data_dict.copy()
                        copy_dict['STATE_SPLIT'] = 'UNIT100'
                        record_dict_list.append(copy_dict)

    @classmethod
    def get_point_record(cls, record_dict_list, prev_record_list):
        """
        이전에 기록했던 데이터와 비교해서 소수점이 바뀌는지 보고 바뀌면 가져온 list 에 추가 저장
        :param record_dict_list:
        :param prev_record_list:
        :return:
        """
        categories = ['HRA', 'OBA', 'SLG']
        for data_dict in record_dict_list:
            state = data_dict['STATE']
            if state in categories and data_dict['STATE_SPLIT'] == 'BASIC':
                basic_record_dict = prev_record_list
                result_record = data_dict['RESULT']
                league = data_dict['LEAGUE']

                prev_result_record = int(basic_record_dict[league][state][0] * 10)
                result_record = int(result_record * 10)

                if result_record > prev_result_record:
                    copy_dict = data_dict.copy()
                    copy_dict['STATE_SPLIT'] = 'POINT1'
                    record_dict_list.append(copy_dict)
    # endregion

    # region 기록 Update
    def update_hitter_record(self, how_event, live_dict):
        """
        타자 기록 update
        :param how_event:
        :param live_dict:
        :return:
        """
        pitcher = live_dict['pitcher']
        hitter = live_dict['hitter']
        year = datetime.now().year
        count_record_lists = [
            {'hitter': hitter, 'state': how_event, 'state_split': 'BASIC', 'opponent': 'ALL', 'gyear': year,
             'pitcher': 'NA', 'pitteam': 'NA'},  # 시즌 통산 기록
            {'hitter': hitter, 'state': how_event, 'state_split': 'VERSUS', 'opponent': 'PITCHER', 'gyear': year,
             'pitcher': pitcher, 'pitteam': 'NA'},  # 선수 대결 통산 기록
            {'hitter': hitter, 'state': how_event, 'state_split': 'VERSUS', 'opponent': 'TEAM', 'gyear': year,
             'pitcher': 'NA', 'pitteam': live_dict['pitteam']},  # 팀 대결 시즌 통산 기록
            {'hitter': hitter, 'state': how_event, 'state_split': live_dict['score'], 'opponent': 'ALL', 'gyear': year,
             'pitcher': 'NA', 'pitteam': 'NA'},  # 점수차 시즌 통산 기록
            {'hitter': hitter, 'state': how_event, 'state_split': live_dict['base'], 'opponent': 'ALL', 'gyear': year,
             'pitcher': 'NA', 'pitteam': 'NA'},  # 주자 상황 시즌 통산 기록
        ]

        for count_record_dict in count_record_lists:
            self.recorder.update_hitter_count_record(count_record_dict)

        param_dict = {'state': how_event, 'splits': "'{0}', '{1}', '{2}', '{3}'".format(
            'BASIC', 'VERSUS', live_dict['score'], live_dict['base'])}
        # self.recorder.call_update_state_rank(param_dict)
    # endregion

    # region Hitter 정보 변수 셋팅
    def set_today_hitter_dict(self, record_dict):
        self.today_record_dict.update(record_dict)

    def set_total_hitter_basic_dict(self):
        # {'SEASON': {'KK': 115.0, 'HR': 35.0, 'H2': 34.0, ...}, 'ALL': {'KK': 286.0,...}
        record_dict = self.total_record
        if record_dict:
            for r in record_dict:
                if r['LEAGUE'] in self.total_basic_record_dict:
                    self.total_basic_record_dict[r['LEAGUE']].update({r['STATE']: [r['RESULT'], r['RANK']]})
                else:
                    self.total_basic_record_dict.update({r['LEAGUE']: {r['STATE']: [r['RESULT'], r['RANK']]}})
    # endregion


class Pitcher(Player):

    # region Pitcher 경기기록
    def get_today_pitcher_data(self, game_id):
        result = []
        today_result = record.Record().get_hitter_today_record(game_id, self.player_code)

        if today_result:
            today = {}
            for k, v in today_result[0].items():
                if type(v) == str:
                    today[k] = v
                else:
                    today[k] = int(v)

            data_dict = {'SUBJECT': 'HITTER', 'OPPONENT': 'NA', 'LEAGUE': 'NA', 'PITCHER': 'NA', 'PITNAME': 'NA',
                         'GYEAR': 'NA', 'PITTEAM': 'NA', 'STATE_SPLIT': 'TODAY',
                         'RANK': 1, 'HITTER': self.player_code, 'HITNAME': today['HITNAME'], 'PA': today['PA']}

            for k, v in today.items():
                if k == 'PA' or k == 'HITNAME':
                    continue
                set_dict = data_dict.copy()
                set_dict['STATE'] = k
                set_dict['RESULT'] = v
                result.append(set_dict)

            self.set_today_hitter_dict(today)

        if result:
            self.today_record = result
        return self.today_record

    def get_pitcher_basic_data(self, pitcher_code):
        result = self.recorder.get_pitcher_basic_record(pitcher_code)
        if result:
            return result
        else:
            return None

    def get_pitcher_vs_team_data(self, pitcher, hit_team, state=None):
        result = self.recorder.get_pitcher_vs_team_record(pitcher, hit_team, state)
        if result:
            return result
        else:
            return None

    def get_pitcher_vs_hitter_data(self, pitcher, hitter, state=None):
        result = self.recorder.get_pitcher_vs_hitter_record(pitcher, hitter, state)
        if result:
            return result
        else:
            return None
    # endregion

    # region 기록 Update

    # endregion

    pass
