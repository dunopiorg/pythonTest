from lib import record
from datetime import datetime


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
        self.prev_total_record = None

        self.n_continue_record = None

    def set_player_info(self):
        self.player_info = self.recorder.get_personal_info(self.player_code)[0]

    def set_prev_total_record(self):
        self.prev_total_record = self.total_record

    def get_total_record(self):
        if self.total_record:
            return self.total_record
        else:
            return None

    def get_today_record(self):
        if self.today_record:
            return self.today_record
        else:
            return None


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
        data_dict = {'SUBJECT': 'HITTER', 'OPPONENT': 'NA', 'LEAGUE': 'TODAY', 'PITCHER': 'NA', 'PITNAME': 'NA',
                     'GYEAR': 'NA', 'PITTEAM': 'NA', 'STATE_SPLIT': 'TODAY', 'RANK': 1}
        result = []
        today_result = record.Record().get_hitter_today_record(game_id, self.player_code)

        if today_result:
            today = {}
            for k, v in today_result[0].items():
                if type(v) == str:
                    today[k] = v
                else:
                    today[k] = int(v)

            data_dict['HITTER'] = self.player_code
            data_dict['HITNAME'] = today['HITNAME']
            data_dict['PA'] = today['PA']

            for k, v in today.items():
                if k == 'PA' or k == 'HITNAME':
                    continue
                set_dict = data_dict.copy()
                set_dict['STATE'] = k
                set_dict['RESULT'] = v
                result.append(set_dict)
            self.set_today_hitter_dict(today)
        else:
            if self.total_record:
                for record_dict in self.total_record:
                    if record_dict['LEAGUE'] == 'SEASON' and record_dict['STATE'] == 'HRA':
                        data_dict = {'SUBJECT': 'HITTER', 'OPPONENT': 'NA', 'LEAGUE': 'TODAY', 'PITCHER': 'NA',
                                     'PITNAME': 'NA', 'GYEAR': record_dict['GYEAR'], 'PITTEAM': 'NA',
                                     'STATE': record_dict['STATE'], 'STATE_SPLIT': 'FIRST', 'RANK': 1,
                                     'HITTER': self.player_code, 'HITNAME': record_dict['HITNAME'], 'RESULT': record_dict['RESULT']}
                        result.append(data_dict)
                        return result

        hra_list = record.Record().get_hitter_basic_record(self.player_code, 'HRA')
        if hra_list:
            for hra in hra_list:
                if hra['LEAGUE'] == 'SEASON':
                    if today_result:
                        hra['STATE_SPLIT'] = 'TODAY'
                    else:
                        hra['STATE_SPLIT'] = 'FIRST'
                    hra['LEAGUE'] = 'TODAY'
                    result.append(hra)

        if result:
            self.today_record = result
        return self.today_record

    def get_hitter_basic_data(self, hitter_code, state=None):
        result_record = self.recorder.get_hitter_basic_record(hitter_code, state)
        if state is None:
            self.total_record = result_record
        return result_record

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

    def get_hitter_n_continue_data(self, state):
        """
        N게임 연속 기록 데이터를 생성한다.
        :return:
        """
        state_dict = {'HIT': ['H1', 'H2', 'H3', 'HR', 'HI', 'HB'], 'HR': ['HR'], 'H2': ['H2'], 'H3': ['H3'],
                      'RBI': ['E', 'R', 'H']}
        data_dict = {'HITTER': self.player_code, 'HITNAME':self.player_info['NAME'], 'OPPONENT': 'ALL',
                     'LEAGUE': 'SEASON', 'PITCHER': 'NA', 'PITNAME': 'NA', 'PITTEAM': 'NA', 'RANK': 1}
        counter_dict = {'HIT': 0, 'HR': 0, 'RBI': 0, 'BB': 0, 'SO': 0}

        all_game_list = self.recorder.get_hitter_continuous_record(self.player_code)
        result = []
        n_game_data_exist = False
        n_pa_data_exist = False
        game_data_list = []
        how_list = []
        if all_game_list:
            prev_game_key = ''
            for i, d in enumerate(all_game_list):
                if i == 0:
                    prev_game_key = d['GMKEY']
                    how_list.append(d['PLACE'])
                    how_list.append(d['HOW'])
                else:
                    if prev_game_key == d['GMKEY']:
                        how_list.append(d['PLACE'])
                        how_list.append(d['HOW'])
                    else:
                        game_data_list.append(list(set(how_list)))
                        del how_list[:]
                        how_list.append(d['PLACE'])
                        how_list.append(d['HOW'])
                        prev_game_key = d['GMKEY']

        # # region N경기 데이터
        # break_flag = False
        # for k_state, v_state in state_dict.items():
        #     for i, d_how_list in enumerate(game_data_list):
        #         for how_data in d_how_list:
        #             if how_data in v_state:
        #                 if i == counter_dict[k_state]:
        #                     counter_dict[k_state] += 1
        #                     n_game_data_exist = True
        #                 if i not in list(counter_dict.values()):
        #                     break_flag = True
        #                     break
        #         if break_flag:
        #             break
        #     if break_flag:
        #         break
        #
        # if n_game_data_exist:
        #     for count_key, count_value in counter_dict.items():
        #         if count_value > 1:
        #             set_dict = data_dict.copy()
        #             set_dict['RESULT'] = count_value
        #             set_dict['STATE'] = count_key
        #             set_dict['STATE_SPLIT'] = 'NGAME'
        #             set_dict['PA'] = len(all_game_list)
        #             set_dict['RATE'] = count_value / len(all_game_list)
        #             result.append(set_dict)
        # # endregion
        #
        # # region N타석 데이터
        # for k_state, v_state in state_dict.items():
        #     how_counter = 0
        #     for i, d in enumerate(all_game_list):
        #         d_how = d['HOW']
        #         if d_how in v_state:
        #             how_counter += 1
        #         elif i > 0:
        #             counter_dict[k_state] = how_counter
        #             n_pa_data_exist = True
        #             break
        #         else:
        #             break
        #     if how_counter > 0:
        #         break
        #
        # for rbi_state in state_dict['RBI']:
        #     rbi_counter = 0
        #     for i, d in enumerate(all_game_list):
        #         d_place = d['PLACE']
        #         if d_place in rbi_state:
        #             rbi_counter += 1
        #         elif i > 0:
        #             counter_dict['RBI'] = rbi_counter
        #             n_pa_data_exist = True
        #             break
        #         else:
        #             break
        #     if rbi_counter == 0:
        #         break
        #
        # if n_pa_data_exist:
        #     for count_key, count_value in counter_dict.items():
        #         if count_value > 1:
        #             set_dict = data_dict.copy()
        #             set_dict['RESULT'] = count_value
        #             set_dict['STATE'] = count_key
        #             set_dict['STATE_SPLIT'] = 'NPA'
        #             set_dict['PA'] = len(all_game_list)
        #             set_dict['RATE'] = count_value/len(all_game_list)
        #             result.append(set_dict)
        # # endregion

        # region NGAME 구하기
        n_game_counter = 0
        for i, d_how_list in enumerate(game_data_list):
            if i == n_game_counter and any(item in d_how_list for item in state_dict[state]):
                n_game_counter += 1
            else:
                break

        if n_game_counter > 1:
            set_dict = data_dict.copy()
            set_dict['RESULT'] = n_game_counter
            set_dict['STATE'] = state
            set_dict['STATE_SPLIT'] = 'NGAME'
            set_dict['PA'] = len(all_game_list)
            set_dict['RATE'] = n_game_counter / len(all_game_list)  # todo rate 값이 필요한가?
            result.append(set_dict)
        # endregion

        # region NPA 구하기
        if state == 'RBI':
            col_name = 'PLACE'
        else:
            col_name = 'HOW'

        n_pa_counter = 0
        for i, pa_info in enumerate(all_game_list):
            if i == n_pa_counter and pa_info[col_name] in state_dict[state]:
                n_pa_counter += 1
            else:
                break

        if n_pa_counter > 1:
            set_dict = data_dict.copy()
            set_dict['RESULT'] = n_pa_counter
            set_dict['STATE'] = state
            set_dict['STATE_SPLIT'] = 'NPA'
            set_dict['PA'] = len(all_game_list)
            set_dict['RATE'] = n_pa_counter / len(all_game_list)  # todo rate 값이 필요한가?
            result.append(set_dict)
            # endregion NPA 구하기

        if result:
            self.n_continue_record = result
            return self.n_continue_record
        else:
            return None

    @classmethod
    def get_ranker_record(cls, record_dict_list):
        result_list = []
        data_dict = {'SUBJECT': 'HITTER', 'OPPONENT': 'NA', 'PITCHER': 'NA', 'PITNAME': 'NA',
                     'GYEAR': 'NA', 'PITTEAM': 'NA'}

        for record_dict in record_dict_list:
            rank = record_dict['RANK']
            if rank < 11:
                result_record = record_dict['RESULT']
                league = record_dict['LEAGUE']
                hitter_name = record_dict['HITNAME']
                hitter = record_dict['HITTER']
                state = record_dict['STATE']
                rate = record_dict['RATE']
                pa = record_dict['PA']

                copy_dict = data_dict.copy()
                copy_dict['STATE_SPLIT'] = 'RANKER'
                copy_dict['STATE'] = state
                copy_dict['RESULT'] = result_record
                copy_dict['LEAGUE'] = league
                copy_dict['HITNAME'] = hitter_name
                copy_dict['HITTER'] = hitter
                copy_dict['RATE'] = rate
                copy_dict['PA'] = pa
                copy_dict['RANK'] = int(rank)
                result_list.append(copy_dict)

        if result_list:
            return result_list
        else:
            return None

    @classmethod
    def get_nine_record(cls, record_dict_list):
        """
        9단위 기록을 생성한다.
        :param record_dict_list: 받아온 list 에 생성한 기록을 담아서 return 한다 .
        :return:
        """
        result_list = []
        data_dict = {'SUBJECT': 'HITTER', 'OPPONENT': 'NA', 'PITCHER': 'NA', 'PITNAME': 'NA',
                     'GYEAR': 'NA', 'PITTEAM': 'NA', 'RANK': 1}
        categories = ['HIT', 'HR', 'RBI']
        for record_dict in record_dict_list:
            if record_dict['STATE'] in categories:
                result_record = int(record_dict['RESULT'])
                league = record_dict['LEAGUE']
                hitter_name = record_dict['HITNAME']
                hitter = record_dict['HITTER']
                state = record_dict['STATE']
                pa = record_dict['PA']
                rate = record_dict['RATE']
                state_result = record_dict['RESULT']

                if league == 'SEASON':
                    quotient = 10
                    remainder = 9
                else:
                    quotient = 100
                    remainder = 99

                if result_record % quotient == remainder:
                    copy_dict = data_dict.copy()
                    copy_dict['STATE_SPLIT'] = '1UNIT'
                    copy_dict['LEAGUE'] = league
                    copy_dict['STATE'] = state
                    copy_dict['PA'] = pa
                    copy_dict['RATE'] = rate
                    copy_dict['RESULT'] = int(state_result) + 1
                    copy_dict['HITNAME'] = hitter_name
                    copy_dict['HITTER'] = hitter
                    result_list.append(copy_dict)

        if result_list:
            return result_list
        else:
            return None

    @classmethod
    def get_ten_record(cls, record_dict_list):
        """
        10단위 기록을 생성한다.
        :param record_dict_list: 생성된 기록은 받아온 list 에 더해진다 .
        :return:
        """
        result_list = []
        categories = ['HIT', 'HR', 'RBI', 'BB']
        for data_dict in record_dict_list:
            if data_dict['STATE'] in categories and data_dict['STATE_SPLIT'] == 'BASIC':
                result_record = data_dict['RESULT']
                league = data_dict['LEAGUE']

                if league == 'SEASON' and result_record != 0:
                    if result_record % 10 == 0:
                        copy_dict = data_dict.copy()
                        copy_dict['STATE_SPLIT'] = 'UNIT10'
                        result_list.append(copy_dict)
                else:
                    if result_record % 100 == 0:
                        copy_dict = data_dict.copy()
                        copy_dict['STATE_SPLIT'] = 'UNIT100'
                        result_list.append(copy_dict)
        return result_list

    @classmethod
    def get_point_record(cls, record_dict_list, prev_record_list):
        """
        이전에 기록했던 데이터와 비교해서 소수점이 바뀌는지 보고 바뀌면 가져온 list 에 추가 저장
        :param record_dict_list:
        :param prev_record_list:
        :return:
        """
        result_list = []
        categories = ['HRA', 'OBA', 'SLG']
        for data_dict in record_dict_list:
            state = data_dict['STATE']
            if state in categories and data_dict['STATE_SPLIT'] == 'BASIC':
                basic_record_dict = prev_record_list
                result_record = data_dict['RESULT']
                league = data_dict['LEAGUE']
                prev_result = basic_record_dict[league][state][0]
                prev_result_record = int(prev_result * 10)
                result_record = int(result_record * 10)

                if result_record > prev_result_record:
                    copy_dict = data_dict.copy()
                    copy_dict['STATE_SPLIT'] = 'POINT_UP'
                    copy_dict['PREV_RESULT'] = prev_result
                    result_list.append(copy_dict)
        return result_list

    @classmethod
    def get_change_rank_record(cls, record_dict_list, prev_record_list):
        result_list = []
        for data_dict in record_dict_list:
            state = data_dict['STATE']
            league = data_dict['LEAGUE']
            if data_dict['STATE_SPLIT'] == 'BASIC':
                prev_record_dict = [x for x in prev_record_list if x['STATE'] == state and league == x['LEAGUE']][0]
                prev_rank = prev_record_dict['RANK']
                now_rank = data_dict['RANK']

                if now_rank > prev_rank and now_rank > 6:
                    copy_dict = data_dict.copy()
                    copy_dict['STATE_SPLIT'] = 'RANK_UP'
                    copy_dict['PREV_RANK'] = prev_rank
                    result_list.append(copy_dict)
        return result_list
        pass
    # endregion

    # region 기록 Update
    def update_hitter_record(self, how_event, live_dict):
        """
        타자 기록 update
        :param how_event:
        :param live_dict:
        :return:
        """
        hit_list = ['H1', 'H2', 'H3', 'HR', 'HI', 'HB']
        pitcher = live_dict['pitcher']
        pitteam = live_dict['pitteam']
        hitter = live_dict['hitter']
        base = live_dict['base']
        score = live_dict['score']
        year = datetime.now().year
        if how_event in hit_list:
            state = "AND state IN ('{0}', 'HIT')".format(how_event)
        else:
            state = "AND state = 'HIT'"
        countable_record_dict = {'hitter': hitter, 'state': state, 'pitcher': pitcher, 'pitteam': pitteam,
                                 'base': base, 'score': score, 'gyear': year}

        #  self.recorder.update_hitter_count_record(countable_record_dict)


        """
        count_record_lists = [
            {'hitter': hitter, 'state': how_event, 'state_split': 'BASIC', 'opponent': 'ALL', 'gyear': year,
             'pitcher': 'NA', 'pitteam': 'NA'},  # 시즌 통산 기록
            {'hitter': hitter, 'state': how_event, 'state_split': 'VERSUS_PITCHER', 'opponent': 'PITCHER', 'gyear': year,
             'pitcher': pitcher, 'pitteam': 'NA'},  # 선수 대결 통산 기록
            {'hitter': hitter, 'state': how_event, 'state_split': 'VERSUS_TEAM', 'opponent': 'TEAM', 'gyear': year,
             'pitcher': 'NA', 'pitteam': live_dict['pitteam']},  # 팀 대결 시즌 통산 기록
            {'hitter': hitter, 'state': how_event, 'state_split': live_dict['score'], 'opponent': 'ALL', 'gyear': year,
             'pitcher': 'NA', 'pitteam': 'NA'},  # 점수차 시즌 통산 기록
            {'hitter': hitter, 'state': how_event, 'state_split': live_dict['base'], 'opponent': 'ALL', 'gyear': year,
             'pitcher': 'NA', 'pitteam': 'NA'},  # 주자 상황 시즌 통산 기록
        ]
        """
        #for count_record_dict in count_record_lists:
        # todo 테스트 시 Update 임시 주석처리
        #  self.recorder.update_hitter_count_record(count_record_dict)

        param_dict = {'state': how_event, 'splits': "'{0}', '{1}', '{2}', '{3}'".format(
            'BASIC', 'VERSUS', live_dict['score'], live_dict['base'])}
        # self.recorder.call_update_state_rank(param_dict)

    def update_hitter_pa_record(self, live_dict):
        pitcher = live_dict['pitcher']
        pitteam = live_dict['pitteam']
        hitter = live_dict['hitter']
        base = live_dict['base']
        score = live_dict['score']
        year = datetime.now().year
        pa_param_dict = {'hitter': hitter, 'pitcher': pitcher, 'pitteam': pitteam,
                                 'base': base, 'score': score, 'gyear': year}
        # todo : 나중에 주석 풀 것.
        # self.recorder.update_hitter_pa(pa_param_dict)
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
                set_dict['RATE'] = v / today['PA']
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

