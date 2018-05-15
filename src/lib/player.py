from lib import record
from datetime import datetime
from korean import Noun


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
        self.TEAM_KOR_DICT = record.Record().get_team_korean_names()

        self.today_record = None
        self.total_record = None
        self.prev_total_record = None
        self.n_continue_record = None

    def set_player_info(self):
        self.player_info = self.recorder.get_player_info(self.player_code)[0]

    def set_prev_total_record(self):
        self.prev_total_record = self.total_record

    def get_today_record(self):
        if self.today_record:
            return self.today_record
        else:
            return None


class Hitter(Player):
    KOREAN_DICT = {'H1': '1루타', 'H2': '2루타', 'H3': '3루타', 'HR': '홈런', 'RUN': '득점', 'RBI': '타점', 'HRA': '타율',
                   'HIT': '안타', 'OB': '출장'}
    def __init__(self, player_code):
        Player.__init__(self, player_code)
        if self.player_info:
            self.hit_type = self.player_info['HITTYPE'][2:]

        self.df_hitter_all_season = record.Record().get_hitter_total_df(player_code)
        self.KOREAN_DICT = {'H1': '1루타', 'H2': '2루타', 'H3': '3루타', 'HR': '홈런', 'RUN': '득점', 'RBI': '타점', 'HRA': '타율', 'HIT': '안타', 'OB': '출장'}

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

        # hra_list = record.Record().get_hitter_basic_record(self.player_code, 'HRA')
        # if hra_list:
        #     for hra in hra_list:
        #         if hra['LEAGUE'] == 'SEASON':
        #             if today_result:
        #                 hra['STATE_SPLIT'] = 'TODAY'
        #             else:
        #                 hra['STATE_SPLIT'] = 'FIRST'
        #             hra['LEAGUE'] = 'TODAY'
        #             result.append(hra)

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

    def get_hitter_n_continue_data(self, game_id, state):
        """
        N게임, 타석, 시즌 연속 기록 데이터를 생성한다.
        :return:
        """
        # HIT 안타, HR 홈런, H2 2루타, H3 3루타, RBI 타점 OB 출루, SB 도루
        state_dict = {'HIT': ['H1', 'HI', 'HB'], 'HR': ['HR'], 'H2': ['H2'], 'H3': ['H3'],
                      'RBI': ['E', 'R', 'H'], 'OB': ['H1', 'H2', 'H3', 'HR', 'HI', 'HB', 'BB'], 'SB': ['SB']}
        n_pa_count_dict = {'HIT': 3, 'HR': 2, 'H2': 2, 'H3': 2, 'RBI': 2, 'OB': 4, 'SB': 1}
        n_game_count_dict = {'HIT': 3, 'HR': 2, 'H2': 2, 'H3': 2, 'RBI': 4, 'OB': 100, 'SB': 1}
        how_many_season_dict = {'HIT': 2, 'RBI': 2, 'HR': 2, 'OB': 3, 'H2': 2, 'H3': 2, 'SB': 2}
        n_season_dict = {'HIT': [150, 100], 'RBI': [100], 'HR': [30, 20, 10], 'OB': [200, 100], 'H2': [30, 20, 10], 'H3': [30, 20, 10], 'SB': [600, 500, 400, 300, 200]}

        data_dict = {'HITTER': self.player_code, 'HITNAME': self.player_info['NAME'], 'OPPONENT': 'ALL',
                     'LEAGUE': 'SEASON', 'PITCHER': 'NA', 'PITNAME': 'NA', 'PITTEAM': 'NA', 'RANK': 1}

        all_game_list = self.recorder.get_hitter_continuous_record(game_id, self.player_code)
        df_hitter_total_realtime = self.recorder.get_hitter_season_realtime_record(game_id, self.player_code)

        if df_hitter_total_realtime.empty:
            return None
        else:
            df_hitter_total_realtime = df_hitter_total_realtime.astype(int)

        result = []
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
        else:
            return None

        # region NGAME 구하기
        n_game_counter = 0
        for i, d_how_list in enumerate(game_data_list):
            if i == n_game_counter and any(item in d_how_list for item in state_dict[state]):
                n_game_counter += 1
            else:
                break

        if n_game_counter >= n_game_count_dict[state]:
            set_dict = data_dict.copy()
            set_dict['RESULT'] = n_game_counter
            set_dict['STATE'] = state
            set_dict['STATE_KOR'] = self.KOREAN_DICT[state]
            set_dict['STATE_SPLIT'] = "NGAME_CONTINUE"
            set_dict['SEASON_COUNT'] = df_hitter_total_realtime.iloc[0][state]
            set_dict['PA'] = len(all_game_list)
            result.append(set_dict)
        # endregion NGAME 구하기

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

        if state == 'OB':
            state_col = 'GAMENUM'
        else:
            state_col = state

        if n_pa_counter > n_pa_count_dict[state]:
            set_dict = data_dict.copy()
            set_dict['RESULT'] = n_pa_counter
            set_dict['STATE'] = state
            set_dict['STATE_KOR'] = self.KOREAN_DICT[state]
            set_dict['STATE_SPLIT'] = "NPA_CONTINUE"
            set_dict['SEASON_COUNT'] = df_hitter_total_realtime.iloc[0][state_col]
            set_dict['PA'] = len(all_game_list)
            result.append(set_dict)
        # endregion NPA 구하기

        # region NSEASON 구하기
        if state == 'OB':
            state_col = 'GAMENUM'
        else:
            state_col = state
        state_record_list = self.df_hitter_all_season[state_col].tolist()
        n_season_counter = 0
        for state_count in n_season_dict[state]:
            for state_record in state_record_list:
                if state_record > state_count:
                    n_season_counter += 1
                else:
                    break
            if n_season_counter >= how_many_season_dict[state]:
                set_season_dict = data_dict.copy()
                set_season_dict['RESULT'] = n_season_counter
                set_season_dict['COUNT'] = state_count
                set_season_dict['STATE'] = state
                if state in ['H2', 'H3']:
                    set_season_dict['STATE_KOR'] = "{} {}개".format(self.KOREAN_DICT[state], state_count)
                else:
                    set_season_dict['STATE_KOR'] = "{}{}".format(state_count, self.KOREAN_DICT[state])
                set_season_dict['SEASON_COUNT'] = df_hitter_total_realtime.iloc[0][state_col]
                set_season_dict['STATE_SPLIT'] = "NSEASON_CONTINUE"
                result.append(set_season_dict)
                break
            else:
                n_season_counter = 0
        # endregion NSEASON 구하기

        if result:
            self.n_continue_record = result
            return self.n_continue_record
        else:
            return None

    def get_hitter_vs_pitcher_data_v2(self, pitcher_code, pitcher_team, how):
        data_dict = {'HITTER': self.player_code, 'HITNAME': self.player_info['NAME'], 'OPPONENT': 'ALL',
                     'LEAGUE': 'SEASON', 'PITCHER': pitcher_code, 'PITNAME': 'NA', 'PITTEAM': pitcher_team, 'RANK': 1}
        how_dict = {'HIT': ['H1', 'H2', 'H3', 'HR', 'HI', 'HB'], 'HR': ['HR']}

        result_list = []

        df_how = self.recorder.get_hitter_vs_pitcher_df(self.player_code, pitcher_code)

        if how == 'HRA':
            hit_count = df_how[df_how['HOW'].isin(how_dict['HIT'])].shape[0]
            pa_count = df_how.shape[0]

            vs_hra = round(hit_count / pa_count, 3)

            season_hra = 0
            if self.df_hitter_all_season:
                season_hra = round(self.df_hitter_all_season['HRA'][0], 3)

            if season_hra == vs_hra:
                return

            if season_hra > vs_hra:
                vs_result = '약한'
            else:
                vs_result = '강한'

            set_hra_dict = data_dict.copy()
            set_hra_dict['RESULT'] = vs_result
            set_hra_dict['SEASON_HRA'] = season_hra
            set_hra_dict['VERSUS_HRA'] = vs_hra
            set_hra_dict['STATE'] = how
            set_hra_dict['STATE_SPLIT'] = "VS_PITCHER_HRA"
            set_hra_dict['PA'] = pa_count
            result_list.append(set_hra_dict)

        elif how == 'HR':
            hr_count = df_how[df_how['HOW'].isin(how_dict['HR'])].shape[0]
            pa_count = df_how.shape[0]

            if hr_count == 0:
                return

            if hr_count > 3:
                set_hr_dict = data_dict.copy()
                set_hr_dict['RESULT'] = hr_count
                set_hr_dict['STATE'] = how
                set_hr_dict['STATE_SPLIT'] = "VS_PITCHER_HR"
                set_hr_dict['PA'] = pa_count
                result_list.append(set_hr_dict)

        return result_list

    def get_hitter_vs_team_data_v2(self, pitcher_team, how):
        data_dict = {'HITTER': self.player_code, 'HITNAME': self.player_info['NAME'], 'OPPONENT': 'ALL',
                     'LEAGUE': 'SEASON', 'PITCHER': 'NA', 'PITNAME': 'NA', 'PITTEAM': self.TEAM_KOR_DICT[pitcher_team], 'RANK': 1}
        how_dict = {'HIT': ['H1', 'H2', 'H3', 'HR', 'HI', 'HB'], 'HR': ['HR']}

        result_list = []

        df_how = self.recorder.get_hitter_vs_team_df(self.player_code, pitcher_team)

        if how == 'HRA':
            vs_hra = df_how['HRA_RT'][0]
            pa_count = df_how['PA_CN'][0]

            season_hra = 0
            if self.df_hitter_all_season:
                season_hra = round(self.df_hitter_all_season['HRA'][0], 3)

            if season_hra == vs_hra:
                return

            if vs_hra > season_hra:
                pos_neg = 'POS'
            else:
                pos_neg = 'NEG'

            set_hra_dict = data_dict.copy()
            set_hra_dict['SEASON_HRA'] = season_hra
            set_hra_dict['VERSUS_HRA'] = vs_hra
            set_hra_dict['STATE'] = how
            set_hra_dict['STATE_SPLIT'] = "VS_TEAM_HRA_%s" % pos_neg
            set_hra_dict['PA'] = pa_count
            result_list.append(set_hra_dict)

        elif how == 'HR':
            season_hr = self.df_hitter_all_season['HR'][0]

            hr_count = df_how['HR_CN'][0]
            pa_count = df_how['PA_CN'][0]

            if hr_count == 0:
                set_first_hr_dict = data_dict.copy()
                set_first_hr_dict['STATE'] = how
                set_first_hr_dict['STATE_SPLIT'] = "VS_TEAM_FIRST_HR"
                set_first_hr_dict['PA'] = pa_count
                result_list.append(set_first_hr_dict)

            if hr_count > round(season_hr/4):
                set_hr_dict = data_dict.copy()
                set_hr_dict['SEASON_HR'] = season_hr
                set_hr_dict['VERSUS_HR'] = hr_count
                set_hr_dict['STATE'] = how
                set_hr_dict['STATE_SPLIT'] = "VS_TEAM_HR"
                set_hr_dict['PA'] = pa_count
                result_list.append(set_hr_dict)

        return result_list

    def get_hitter_cyclinghit(self, game_key):
        data_dict = {'HITTER': self.player_code, 'HITNAME': self.player_info['NAME'], 'OPPONENT': 'ALL',
                     'LEAGUE': 'SEASON', 'PITCHER': 'NA', 'PITNAME': 'NA', 'PITTEAM': 'NA', 'RANK': 1}

        result_list = []

        df_today = self.recorder.get_hitter_today_game_df(game_key, self.player_code)

        if df_today.empty:
            return None

        df_hit = df_today.loc[:, 'H1':'HR']
        hit_count_list = df_hit[df_hit > 0].fillna(0).iloc[0].tolist()
        hit_count = 0
        for hit in hit_count_list:
            if hit > 0:
                hit_count += 1

        if hit_count == 4:
            #todo later
            pass
        elif hit_count == 3:
            hit_left_name = df_hit.columns[(df_hit == 0).iloc[0]].tolist()[0]
            hit_name_list = df_hit.columns[(df_hit > 0).iloc[0]].tolist()

            set_cyclinghit_dict = data_dict.copy()
            set_cyclinghit_dict['LEFT'] = self.KOREAN_DICT[hit_left_name]
            set_cyclinghit_dict['HIT1'] = self.KOREAN_DICT[hit_name_list[0]]
            set_cyclinghit_dict['HIT2'] = self.KOREAN_DICT[hit_name_list[1]]
            set_cyclinghit_dict['HIT3'] = self.KOREAN_DICT[hit_name_list[2]]
            set_cyclinghit_dict['STATE'] = 'CYCLINGHIT'
            set_cyclinghit_dict['STATE_SPLIT'] = 'CYCLINGHIT_ONE'
            result_list.append(set_cyclinghit_dict)
        elif hit_count == 2:
            hit_left_name_list = df_hit.columns[(df_hit == 0).iloc[0]].tolist()
            hit_name_list = df_hit.columns[(df_hit == 1).iloc[0]].tolist()

            if 'H3' in hit_name_list:
                set_cyclinghit_dict = data_dict.copy()
                set_cyclinghit_dict['LEFT1'] = self.KOREAN_DICT[hit_left_name_list[0]]
                set_cyclinghit_dict['LEFT2'] = self.KOREAN_DICT[hit_left_name_list[1]]
                set_cyclinghit_dict['HIT1'] = self.KOREAN_DICT[hit_name_list[0]]
                set_cyclinghit_dict['HIT2'] = self.KOREAN_DICT[hit_name_list[1]]
                set_cyclinghit_dict['STATE'] = 'CYCLINGHIT'
                set_cyclinghit_dict['STATE_SPLIT'] = 'CYCLINGHIT_TWO'
                result_list.append(set_cyclinghit_dict)

        return result_list

    def get_season_hitter_ranker_data(self):
        data_dict = {'HITTER': self.player_code, 'HITNAME': self.player_info['NAME'], 'OPPONENT': 'ALL',
                     'LEAGUE': 'SEASON', 'PITCHER': 'NA', 'PITNAME': 'NA', 'PITTEAM': 'NA', 'RANK': 1}
        state_list = ['HIT', 'H2', 'H3', 'RUN', 'RBI', 'HR', 'HRA']

        result_list = []

        df_hitter_total = self.recorder.get_season_hitters_total_df()

        for state in state_list:
            df_hitters = df_hitter_total.sort_values(by=state, ascending=False).reset_index()
            hitter_rank = df_hitters[df_hitters['PCODE'] == str(self.player_code)].index[0] + 1
            hitter_record = df_hitters.iloc[hitter_rank - 1][state]
            if state == 'HRA':
                hitter_record = round(hitter_record, 3)

            if hitter_rank <= 10:
                set_ranker_dict = data_dict.copy()
                set_ranker_dict['RESULT'] = hitter_record
                set_ranker_dict['RANK'] = hitter_rank
                if state == 'RUN' or state == 'RBI':
                    set_ranker_dict['STATE_KOR'] = "{0}{1}"  .format(hitter_record, self.KOREAN_DICT[state])
                elif state == 'HRA':
                    set_ranker_dict['STATE_KOR'] = "타율 {0}".format(str(hitter_record))
                else:
                    set_ranker_dict['STATE_KOR'] = "{0} {1}개" .format(self.KOREAN_DICT[state], hitter_record)
                set_ranker_dict['STATE'] = state
                set_ranker_dict['STATE_SPLIT'] = 'RANKER_SEASON'
                result_list.append(set_ranker_dict)

        return result_list

    def get_season_hitter_one_left_data(self, how):
        data_dict = {'HITTER': self.player_code, 'HITNAME': self.player_info['NAME'], 'OPPONENT': 'ALL',
                     'LEAGUE': 'SEASON', 'PITCHER': 'NA', 'PITNAME': 'NA', 'PITTEAM': 'NA', 'RANK': 1}
        if how in ['H1', 'H2', 'H3', 'HR', 'HI', 'HB']:
            state_list = [how, 'RUN', 'RBI']
        else:
            state_list = [how]

        result_list = []

        df_hitter_total = self.recorder.get_hitter_total_df(self.player_code)

        if df_hitter_total.empty:
            return None
        else:
            df_hitter_total = df_hitter_total.loc[[0]]

        df_state = df_hitter_total[state_list]
        nine_record_dict = df_state[df_state % 10 == 9].dropna(axis=1).to_dict('records')[0]

        for state, state_value in nine_record_dict.items():
            set_nine_dict = data_dict.copy()
            set_nine_dict['RESULT'] = state_value + 1
            if state == 'RUN' or state == 'RBI':
                set_nine_dict['STATE_KOR'] = "{0}{1}"  .format(state_value, self.KOREAN_DICT[state])
            else:
                set_nine_dict['STATE_KOR'] = "{0} {1}개" .format(self.KOREAN_DICT[state], state_value)
            if state == 'H2' or state == 'H3':
                set_nine_dict['STATE_KOR2'] = "{0} {1}".format(state_value + 1, self.KOREAN_DICT[state])
            else:
                set_nine_dict['STATE_KOR2'] = "{0}{1}".format(state_value + 1, self.KOREAN_DICT[state])
            if state == 'RUN':
                set_nine_dict['LEFT'] = "한 점"
            elif state == 'RBI':
                set_nine_dict['LEFT'] = "한 타점"
            else:
                set_nine_dict['LEFT'] = "한 개"
            set_nine_dict['STATE'] = state
            set_nine_dict['STATE_SPLIT'] = 'SEASON_ONE_LEFT'
            result_list.append(set_nine_dict)

        return result_list

    def get_total_hitter_one_left_data(self, how):
        data_dict = {'HITTER': self.player_code, 'HITNAME': self.player_info['NAME'], 'OPPONENT': 'ALL',
                     'LEAGUE': 'SEASON', 'PITCHER': 'NA', 'PITNAME': 'NA', 'PITTEAM': 'NA', 'RANK': 1}

        if how in ['H1', 'H2', 'H3', 'HR', 'HI', 'HB']:
            state_list = [how, 'RUN', 'RBI']
        else:
            state_list = [how]

        result_list = []
        df_hitter_total = self.recorder.get_hitter_total_df(self.player_code)
        if df_hitter_total.empty:
            return None

        df_state = df_hitter_total[state_list]
        df_state = df_state.sum().to_frame().transpose()
        nine_record_dict = df_state[df_state % 10 == 99].dropna(axis=1).to_dict('records')[0]

        for state, state_value in nine_record_dict.items():
            set_nine_dict = data_dict.copy()
            set_nine_dict['RESULT'] = state_value + 1
            if state == 'RUN' or state == 'RBI':
                set_nine_dict['STATE_KOR'] = "{0}{1}"  .format(state_value, self.KOREAN_DICT[state])
            else:
                set_nine_dict['STATE_KOR'] = "{0} {1}개" .format(self.KOREAN_DICT[state], state_value)
            if state == 'H2' or state == 'H3':
                set_nine_dict['STATE_KOR2'] = "{0} {1}".format(state_value + 1, self.KOREAN_DICT[state])
            else:
                set_nine_dict['STATE_KOR2'] = "{0}{1}".format(state_value + 1, self.KOREAN_DICT[state])
            if state == 'RUN':
                set_nine_dict['LEFT'] = "한 점"
            elif state == 'RBI':
                set_nine_dict['LEFT'] = "한 타점"
            else:
                set_nine_dict['LEFT'] = "한 개"
            set_nine_dict['STATE'] = state
            set_nine_dict['STATE_SPLIT'] = 'TOTAL_ONE_LEFT'
            result_list.append(set_nine_dict)

        return result_list

    def get_season_hitter_event_10_units(self, game_key, how):
        data_dict = {'HITTER': self.player_code, 'HITNAME': self.player_info['NAME'], 'OPPONENT': 'ALL',
                     'LEAGUE': 'SEASON', 'PITCHER': 'NA', 'PITNAME': 'NA', 'PITTEAM': 'NA', 'RANK': 1}
        state_dict = {'HIT': 50, 'H2': 10, 'H3': 10, 'HR': 10, 'RUN': 30, 'RBI': 30}
        if how in ['H1', 'H2', 'H3', 'HR', 'HI', 'HB']:
            state_list = [how, 'RUN', 'RBI']
        else:
            state_list = [how]

        result_list = []

        df_hitter_total = self.recorder.get_hitter_season_realtime_record(game_key, self.player_code)

        if df_hitter_total.empty:
            return None
        else:
            df_hitter_total = df_hitter_total.astype(int)

        df_state = df_hitter_total[state_list]
        nine_record_dict = df_state[df_state % 10 == 0].dropna(axis=1).to_dict('records')[0]

        for state, state_value in nine_record_dict.items():
            if state_value >= state_dict[state]:
                set_nine_dict = data_dict.copy()
                set_nine_dict['RESULT'] = state_value
                if state == 'RUN' or state == 'RBI':
                    set_nine_dict['STATE_KOR'] = "{0}{1}"  .format(state_value, self.KOREAN_DICT[state])
                else:
                    set_nine_dict['STATE_KOR'] = "{0}개의 {1}" .format(state_value, self.KOREAN_DICT[state])
                set_nine_dict['STATE_KOR2'] = self.KOREAN_DICT[state]
                set_nine_dict['STATE'] = state
                set_nine_dict['STATE_SPLIT'] = 'SEASON_10_UNITS'
                result_list.append(set_nine_dict)

        return result_list

    def get_total_hitter_100_units_data(self, game_key, how):
        data_dict = {'HITTER': self.player_code, 'HITNAME': self.player_info['NAME'], 'OPPONENT': 'ALL',
                     'LEAGUE': 'SEASON', 'PITCHER': 'NA', 'PITNAME': 'NA', 'PITTEAM': 'NA', 'RANK': 1}
        state_dict = {'HIT': 300, 'H2': 100, 'H3': 100, 'RUN': 30, 'RBI': 100, 'HR': 100}
        if how in ['H1', 'H2', 'H3', 'HR', 'HI', 'HB']:
            state_list = [how, 'RUN', 'RBI']
        else:
            state_list = [how]
        result_list = []

        df_hitter_total = self.recorder.get_all_hitters_season_realtime_record(game_key)

        if df_hitter_total.empty:
            return None
        else:
            df_hitter_total = df_hitter_total.astype(int)

        df_state = df_hitter_total[state_list]
        nine_record_dict = df_state[df_state % 100 == 0].dropna(axis=1).to_dict('records')[0]

        for state, state_value in nine_record_dict.items():
            if state_value >= state_dict[state]:
                set_nine_dict = data_dict.copy()
                set_nine_dict['RESULT'] = state_value
                if state == 'RUN' or state == 'RBI':
                    set_nine_dict['STATE_KOR'] = "{0}{1}"  .format(state_value, self.KOREAN_DICT[state])
                else:
                    set_nine_dict['STATE_KOR'] = "{0}개의 {1}" .format(state_value, self.KOREAN_DICT[state])
                set_nine_dict['STATE_KOR2'] = self.KOREAN_DICT[state]
                set_nine_dict['STATE'] = state
                set_nine_dict['STATE_SPLIT'] = 'TOTAL_100_UNITS'
                result_list.append(set_nine_dict)

        return result_list

    def get_total_hitters_ranker_data(self):
        """
        타자들의 통산기록 순위
        :return:
        """
        data_dict = {'HITTER': self.player_code, 'HITNAME': self.player_info['NAME'], 'OPPONENT': 'ALL',
                     'LEAGUE': 'SEASON', 'PITCHER': 'NA', 'PITNAME': 'NA', 'PITTEAM': 'NA', 'RANK': 1}
        state_list = ['HIT', 'H2', 'H3', 'RUN', 'RBI', 'HR', 'HRA']

        result_list = []

        df_total_hitters = self.recorder.get_total_hitters_df()

        for state in state_list:
            df_hitters = df_total_hitters.sort_values(by=state, ascending=False).reset_index()
            hitter_rank = df_hitters[df_hitters['PCODE'] == str(self.player_code)].index[0] + 1
            if state == 'HRA':
                hitter_record = df_hitters.iloc[hitter_rank - 1][state]
            else:
                hitter_record = df_hitters.iloc[hitter_rank - 1][state].astype(int)

            if hitter_rank <= 30:
                set_ranker_dict = data_dict.copy()
                set_ranker_dict['RESULT'] = hitter_record
                set_ranker_dict['RANK'] = hitter_rank
                if state == 'RUN' or state == 'RBI':
                    set_ranker_dict['STATE_KOR'] = "{0}{1}"  .format(hitter_record, self.KOREAN_DICT[state])
                elif state == 'HRA':
                    set_ranker_dict['STATE_KOR'] = "타율 {0}".format(str(hitter_record))
                else:
                    set_ranker_dict['STATE_KOR'] = "{0} {1}개" .format(self.KOREAN_DICT[state], hitter_record)
                set_ranker_dict['STATE'] = state
                set_ranker_dict['STATE_SPLIT'] = 'RANKER_TOTAL'
                result_list.append(set_ranker_dict)

        return result_list

    def get_hitter_vs_team_how_event_data(self, pitcher_team, how):
        """
        타자가 팀 상대로 만들어낸 기록
        {민병헌}이 올해 떄려낸 {14}개의 2루타 중 {4}개가 {NC}를 상대로 만들어낸 기록입니다.
        :param pitcher_team:
        :param how:
        :return:
        """
        data_dict = {'HITTER': self.player_code, 'HITNAME': self.player_info['NAME'], 'OPPONENT': 'ALL',
                     'LEAGUE': 'SEASON', 'PITCHER': 'NA', 'PITNAME': 'NA', 'PITTEAM': self.TEAM_KOR_DICT[pitcher_team],
                     'RANK': 1}
        how_dict = {'HIT': ['H1', 'H2', 'H3', 'HR', 'HI', 'HB'], 'HR': ['HR'], 'H2': ['H2'], 'H3': ['H3']}

        result_list = []

        for how_key, how_value in how_dict.items():
            if how in how_value:
                df_vs_team = self.recorder.get_hitter_vs_team_df(self.player_code, pitcher_team)

                how_col = "%s_CN" % how_key
                how_count = df_vs_team[how_col][0]
                pa_count = df_vs_team['PA_CN'][0]

                season_data = 0
                if not self.df_hitter_all_season.empty:
                    season_data = self.df_hitter_all_season[how_key][0]

                if how_count > round(season_data/4):
                    set_vs_team_dict = data_dict.copy()
                    set_vs_team_dict['SEASON_RESULT'] = season_data
                    set_vs_team_dict['VERSUS_RESULT'] = how_count
                    set_vs_team_dict['STATE'] = how_key
                    set_vs_team_dict['STATE_KOR'] = self.KOREAN_DICT[how_key]
                    set_vs_team_dict['STATE_SPLIT'] = "VS_TEAM"
                    set_vs_team_dict['PA'] = pa_count
                    result_list.append(set_vs_team_dict)

        return result_list

    def get_hitter_season_first_data(self, game_id, how):
        data_dict = {'HITTER': self.player_code, 'HITNAME': self.player_info['NAME'], 'OPPONENT': 'ALL',
                     'LEAGUE': 'SEASON', 'PITCHER': 'NA', 'PITNAME': 'NA', 'PITTEAM': 'NA', 'RANK': 1}
        state_list = ['PCODE', 'HIT', 'H2', 'H3', 'RBI', 'RUN', 'HR', 'SB']
        state_count_dict = {'HIT': [100, 150, 200], 'H2': [10, 20, 30], 'H3': [10, 20, 30], 'RBI': [100], 'RUN': [100], 'HR': [10, 20, 30, 40, 50]}
        result_list = []

        if how not in state_count_dict:
            return None

        df_hitter_total = self.recorder.get_all_hitters_season_realtime_record(game_id)

        for state_count in reversed(state_count_dict[how]):
            query_string = "%s > %d" % (how, state_count)
            df_state = df_hitter_total.query(query_string)
            df_state = df_state[state_list].sort_values(by=how, ascending=False).reset_index()
            hitter_rank = df_state.index[df_state['PCODE'] == self.player_code].tolist()
            if hitter_rank:
                hitter_rank = hitter_rank[0]
            else:
                return None

            if hitter_rank == 0:
                set_first_dict = data_dict.copy()
                set_first_dict['RESULT'] = state_count
                set_first_dict['STATE'] = how
                set_first_dict['STATE_KOR'] = self.KOREAN_DICT[how]
                set_first_dict['STATE_SPLIT'] = "SEASON_FIRST_RECORD"
                result_list.append(set_first_dict)
                return result_list

        return result_list

    @classmethod
    def get_ranker_record(cls, record_dict_list):
        result_list = []
        data_dict = {'SUBJECT': 'HITTER', 'OPPONENT': 'NA', 'PITCHER': 'NA', 'PITNAME': 'NA',
                     'GYEAR': 'NA', 'PITTEAM': 'NA'}

        for record_dict in record_dict_list:
            rank = record_dict['RANK']
            if rank < 6 and record_dict['STATE'] != 'SO' and record_dict['PA'] > 100:
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
                    league_kor = '시즌'
                else:
                    quotient = 100
                    remainder = 99
                    league_kor = '통산'

                if result_record % quotient == remainder:
                    copy_dict = data_dict.copy()
                    copy_dict['STATE_SPLIT'] = '1UNIT'
                    copy_dict['LEAGUE'] = league
                    copy_dict['LEAGUE_KOR'] = league_kor
                    copy_dict['STATE'] = state
                    copy_dict['STATE_KOR'] = cls.KOREAN_DICT[state]
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

    @classmethod
    def get_season_hitter_20_20_record(cls, game_key, hitter_code):
        """
        20-20 클럽 달성
        :param game_key:
        :param hitter_code:
        :return:
        """
        hitter_name = record.Record().get_player_info(hitter_code)[0]['NAME']
        data_dict = {'HITTER': hitter_code, 'HITNAME': hitter_name, 'OPPONENT': 'ALL',
                     'LEAGUE': 'SEASON', 'PITCHER': 'NA', 'PITNAME': 'NA', 'PITTEAM': 'NA', 'RANK': 1}
        state_list = ['HR', 'SB']
        result_list = []

        df_hitter_total = record.Record().get_hitter_total_df(hitter_code)
        df_realtime_season_total = record.Record().get_all_hitters_season_realtime_record(game_key)

        if df_hitter_total.empty:
            return None
        else:
            df_season_state = df_realtime_season_total[['PCODE', 'HR', 'SB']]
            df_season_state = df_season_state.sort_values(by=state_list, ascending=False)
            df_realtime_hitter_state = df_season_state[df_season_state['PCODE'] == hitter_code]

            df_hitter_total = df_hitter_total.loc[[0]]
            df_hitter_total = df_hitter_total[state_list]

        # 이미 20-20 달성한 경우 pass
        if df_hitter_total.iloc[0]['HR'] >= 20 and df_hitter_total.iloc[0]['SB'] >= 20:
            return
        elif df_realtime_hitter_state.iloc[0]['HR'] >= 20 and df_realtime_hitter_state.iloc[0]['SB'] == 19:
            set_20_club_dict = data_dict.copy()
            set_20_club_dict['HR'] = df_realtime_hitter_state.iloc[0]['HR']
            set_20_club_dict['SB'] = df_realtime_hitter_state.iloc[0]['SB']
            set_20_club_dict['LEFT'] = '도루'
            set_20_club_dict['STATE'] = 'CLUB20'
            set_20_club_dict['STATE_SPLIT'] = 'CLUB_2020_LEFT'
            result_list.append(set_20_club_dict)
        elif df_realtime_hitter_state.iloc[0]['HR'] == 19 and df_realtime_hitter_state.iloc[0]['SB'] >= 20:
            set_20_club_dict = data_dict.copy()
            set_20_club_dict['HR'] = df_realtime_hitter_state.iloc[0]['HR']
            set_20_club_dict['SB'] = df_realtime_hitter_state.iloc[0]['SB']
            set_20_club_dict['LEFT'] = '홈런'
            set_20_club_dict['STATE'] = 'CLUB20'
            set_20_club_dict['STATE_SPLIT'] = 'CLUB_2020_LEFT'
            result_list.append(set_20_club_dict)
        elif df_realtime_hitter_state.iloc[0]['HR'] >= 20 and df_realtime_hitter_state.iloc[0]['SB'] >= 20:
            df_recorders = df_season_state[df_season_state >= 20].dropna(axis=0, how='any').reset_index()
            hitter_rank = df_recorders[df_recorders['PCODE'] == hitter_code].index[0] + 1
            set_20_club_dict = data_dict.copy()
            set_20_club_dict['RANK'] = hitter_rank
            set_20_club_dict['HR'] = df_realtime_hitter_state.iloc[0]['HR']
            set_20_club_dict['SB'] = df_realtime_hitter_state.iloc[0]['SB']
            set_20_club_dict['STATE'] = 'CLUB20'
            set_20_club_dict['STATE_SPLIT'] = 'CLUB_2020_DONE'
            result_list.append(set_20_club_dict)
        return result_list

    def get_hitter_game_number(self, hitter_code):
        """
        타자의 역대 출장 기록, 역대 몇 번째 기록
        :param hitter_code:
        :return:
        """
        game_number = None
        numbers = [1000, 1500, 2000, 2500]
        data_dict = {'SUBJECT': 'HITTER', 'HITTER': self.player_info['NAME'], 'RANK': 1}
        query_result = self.recorder.get_hitter_gamenum(hitter_code)
        if query_result:
            for num in numbers:
                if (num - query_result[0]['GAMENUM']) == 0:
                    number_cnt = self.recorder.get_pitcher_gamenum_cnt(num)
                    if number_cnt:
                        record_rank = number_cnt[0]['GAMENUM'] + 1
                    else:
                        record_rank = '첫'
                    game_number = data_dict.copy()
                    game_number['LEAGUE'] = 'SEASON'
                    game_number['STATE'] = 'HITTER_STARTING'
                    game_number['STATE_SPLIT'] = 'GAMENUM_RECORD'
                    game_number['RESULT'] = num
                    game_number['RANKER'] = record_rank
                elif 0 < (num - query_result[0]['GAMENUM']) < 4:
                    number_cnt = self.recorder.get_pitcher_gamenum_cnt(num)
                    if number_cnt:
                        record_rank = number_cnt[0]['GAMENUM'] + 1
                    else:
                        record_rank = '첫'
                    game_number = data_dict.copy()
                    game_number['LEAGUE'] = 'SEASON'
                    game_number['STATE'] = 'HITTER_STARTING'
                    game_number['STATE_SPLIT'] = 'GAMENUM_RECORD_LEFT'
                    game_number['RESULT'] = query_result[0]['GAMENUM']
                    game_number['TARGET'] = num
                    game_number['LEFT'] = num - query_result[0]['GAMENUM']
                    game_number['RANKER'] = record_rank

            return game_number
        else:
            return None
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

    def __init__(self, player_code):
        Player.__init__(self, player_code)
        self.df_pitcher_all_season = record.Record().get_pitcher_total_df(player_code)
        self.KOREAN_STATE_DICT = {'CG': '완봉', 'CG_W': '완봉승', 'SHO': '완투', 'SHO_W': '완투승', 'W': '승', 'L': '패', 'SV': '세이브', 'HOLD': '홀드', 'BF': '타자'
            , 'HIT': '피안타', 'HR': '피홈런', 'INN': '이닝', 'BB': '볼넷', 'KK': '탈삼진', 'R': '실점', 'ER': '자책점', 'INNING': '이닝', 'GAMENUM': '출장'}

    # region Pitcher 기록
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

    def get_pitcher_basic_data(self, pitcher_code, state=None):
        result = self.recorder.get_pitcher_basic_record(pitcher_code, state)

        if result:
            return result
        else:
            return None

    def get_pitcher_vs_team_data(self, pitcher_code, hit_team, state=None):
        result = self.recorder.get_pitcher_vs_team_record(pitcher_code, hit_team, state)
        if result:
            return result
        else:
            return None

    def get_pitcher_vs_hitter_data(self, pitcher_code, hitter_code, state=None):
        result = self.recorder.get_pitcher_vs_hitter_record(pitcher_code, hitter_code, state)
        if result:
            return result
        else:
            return None

    def get_pitcher_basic_total_data(self, pitcher_code):
        pitcher_basic_result = self.recorder.get_pitcher_basic_total_record(pitcher_code)
        if pitcher_basic_result:
            return pitcher_basic_result
        else:
            return None

    def get_pitcher_nine_record(self, record_dict_list):
        result_list = []
        data_dict = {'SUBJECT': 'PITCHER', 'RANK': 1}
        for record_dict in record_dict_list:
            if 'KK' in record_dict:
                if record_dict['KK'] % 10 == 9:
                    nine_dict = data_dict.copy()
                    nine_dict['STATE_SPLIT'] = '1UNIT'
                    nine_dict['LEAGUE'] = record_dict['LEAGUE']
                    nine_dict['RESULT'] = int(record_dict['KK']) + 1
                    nine_dict['PITNAME'] = record_dict['PITNAME']
                    nine_dict['STATE'] = record_dict['STATE']
                    nine_dict['TEAM'] = record_dict['TEAM']
                    result_list.append(nine_dict)

        if result_list:
            return result_list
        else:
            return None

    def get_how_event_data(self, how_event, hitter, hit_team):
        result_list = []
        how_dict = {'KK': 'SO', 'KN': 'SO', 'KB': 'SO', 'KW': 'SO', 'KP': 'SO',
                    # 'H1': 'HIT', 'H2': 'HIT', 'H3': 'HIT', 'HR': 'HIT', 'HI': 'HIT', 'HB': 'HIT',
                    # 'HR': 'HR',
                    # 'BB': 'BB', 'IB': 'BB',
                    # 'HP': 'HP'
                    }

        if how_event in how_dict:
            # basic_record = self.get_pitcher_basic_data(self.player_code, how_dict[how_event])
            # if basic_record:
            #     result_list.extend(basic_record)

            pitcher_vs_hitter_record = self.get_pitcher_vs_hitter_data(self.player_code, hitter, how_dict[how_event])
            if pitcher_vs_hitter_record:
                result_list.extend(pitcher_vs_hitter_record)

            pitcher_vs_team_record = self.get_pitcher_vs_team_data(self.player_code, hit_team, how_dict[how_event])
            if pitcher_vs_team_record:
                result_list.extend(pitcher_vs_team_record)

            if result_list:
                return result_list
            else:
                return None

    def get_previous_game_pitcher_data(self, game_key, pitcher_code):
        query_result = self.recorder.get_previous_game_pitcher_record(game_key[:8], pitcher_code)
        if query_result:
            return query_result
        else:
            return None

    def get_pitcher_game_number(self, pitcher_code):
        game_number = None
        numbers = [500, 600, 700, 800, 900, 1000]
        data_dict = {'SUBJECT': 'PITCHER', 'PITCHER': self.player_info['NAME'], 'RANK': 1}
        query_result = self.recorder.get_pitcher_gamenum(pitcher_code)
        if query_result:
            for num in numbers:
                if (num - query_result[0]['GAMENUM']) == 0:
                    number_cnt = self.recorder.get_pitcher_gamenum_cnt(num)
                    if number_cnt:
                        record_rank = number_cnt[0]['GAMENUM'] + 1
                    else:
                        record_rank = '첫'
                    game_number = data_dict.copy()
                    game_number['STATE'] = 'PITCHER_STARTING'
                    game_number['STATE_SPLIT'] = 'GAMENUM_RECORD'
                    game_number['RESULT'] = num
                    game_number['RANKER'] = record_rank
                elif 0 < (num - query_result[0]['GAMENUM']) < 4:
                    number_cnt = self.recorder.get_pitcher_gamenum_cnt(num)
                    if number_cnt:
                        record_rank = number_cnt[0]['GAMENUM'] + 1
                    else:
                        record_rank = '첫'
                    game_number = data_dict.copy()
                    game_number['STATE'] = 'PITCHER_STARTING'
                    game_number['STATE_SPLIT'] = 'GAMENUM_RECORD_LEFT'
                    game_number['RESULT'] = query_result[0]['GAMENUM']
                    game_number['TARGET'] = num
                    game_number['LEFT'] = num - query_result[0]['GAMENUM']
                    game_number['RANKER'] = record_rank

            return game_number
        else:
            return None

    def get_total_pitcher_one_left_data(self, how_state=None):
        data_dict = {'HITTER': 'NA', 'HITNAME': 'NA', 'OPPONENT': 'ALL',
                     'LEAGUE': 'SEASON', 'PITCHER': self.player_code, 'PITNAME': self.player_info['NAME'], 'PITTEAM': 'NA', 'RANK': 1}
        state_list = ['W', 'SV', 'HOLD', 'KK']

        if how_state and how_state in state_list:
            state_list = [how_state]

        result_list = []

        if self.df_pitcher_all_season.empty:
            return None

        df_state = self.df_pitcher_all_season[state_list]
        df_state = df_state.sum().to_frame().transpose()
        nine_record_dict = df_state[df_state % 10 == 99].dropna(axis=1).to_dict('records')[0]

        for state, state_value in nine_record_dict.items():
            set_nine_dict = data_dict.copy()
            set_nine_dict['RESULT'] = state_value + 1
            set_nine_dict['TOTAL_RESULT'] = state_value
            set_nine_dict['STATE_KOR'] = self.KOREAN_STATE_DICT[state]
            set_nine_dict['STATE'] = state
            set_nine_dict['STATE_SPLIT'] = 'TOTAL_ONE_LEFT'
            result_list.append(set_nine_dict)

        return result_list

    def get_season_pitcher_one_left_data(self, how_state):
        data_dict = {'HITTER': 'NA', 'HITNAME': 'NA', 'OPPONENT': 'ALL',
                     'LEAGUE': 'SEASON', 'PITCHER': self.player_code, 'PITNAME': self.player_info['NAME'], 'PITTEAM': 'NA', 'RANK': 1}
        state_list = ['W', 'SV', 'HOLD', 'KK']

        if how_state and how_state in state_list:
            state_list = [how_state]

        result_list = []

        if self.df_pitcher_all_season.empty:
            return None
        else:
            df_pitcher_total = self.df_pitcher_all_season.loc[[0]]

        df_state = df_pitcher_total[state_list]
        nine_record_dict = df_state[df_state % 10 == 9].dropna(axis=1).to_dict('records')[0]

        for state, state_value in nine_record_dict.items():
            set_nine_dict = data_dict.copy()
            set_nine_dict['RESULT'] = state_value + 1
            set_nine_dict['SEASON_RESULT'] = state_value
            set_nine_dict['STATE_KOR'] = self.KOREAN_STATE_DICT[state]
            set_nine_dict['STATE'] = state
            set_nine_dict['STATE_SPLIT'] = 'SEASON_ONE_LEFT'
            result_list.append(set_nine_dict)

        return result_list

    def get_season_pitcher_ranker_data(self, game_key):
        data_dict = {'HITTER': 'NA', 'HITNAME': 'NA', 'OPPONENT': 'ALL',
                     'LEAGUE': 'SEASON', 'PITCHER': self.player_code, 'PITNAME': self.player_info['NAME'],
                     'PITTEAM': 'NA', 'RANK': 1}
        state_list = ['W', 'KK', 'INNING']  #, 'ERA'] 나중에 S2i에서 데이터 들어오면 한다.

        result_list = []

        df_pitcher_total = self.recorder.get_pitcher_season_realtime_record(game_key)

        for state in state_list:
            df_pitcher = df_pitcher_total.sort_values(by=state, ascending=False).reset_index()
            pitcher_rank = df_pitcher[df_pitcher['PCODE'] == str(self.player_code)].index[0] + 1
            pitcher_record = df_pitcher.iloc[pitcher_rank - 1][state]
            if state == 'ERA':
                pitcher_record = round(pitcher_record, 3)
            else:
                pitcher_record = int(pitcher_record)

            if pitcher_rank <= 5:
                set_ranker_dict = data_dict.copy()
                set_ranker_dict['RESULT'] = pitcher_record
                set_ranker_dict['RANK'] = pitcher_rank
                set_ranker_dict['STATE_KOR'] = "{0}{1}" .format(str(pitcher_record), self.KOREAN_STATE_DICT[state])
                set_ranker_dict['STATE'] = state
                set_ranker_dict['STATE_SPLIT'] = 'RANKER_SEASON'
                result_list.append(set_ranker_dict)

        return result_list

    def get_total_pitcher_ranker_data(self, hitter_name, how_state=None):
        """
        투수들의 통산기록 순위
        :return:
        """
        data_dict = {'HITTER': 'NA', 'HITNAME': hitter_name, 'OPPONENT': 'ALL',
                     'LEAGUE': 'SEASON', 'PITCHER': self.player_code, 'PITNAME': self.player_info['NAME'],
                     'PITTEAM': 'NA', 'RANK': 1}
        state_list = ['CG_W', 'SHO_W', 'CG', 'SHO', 'W', 'SV', 'HOLD', 'INNING', 'KK']
        state_ranker_dict = {'CG_W': 30, 'SHO_W': 20, 'CG': 20, 'SHO': 10, 'W': 30, 'SV': 20, 'INNING': 30, 'HOLD': 20, 'KK': 20}
        state_records_dict = {'GAMENUM': [500, 600, 700, 800, 900], 'W': [100, 150, 200], 'SV': [100, 150, 200, 250],
                         'HOLD': [100, 150], 'INNING': [3000], 'KK': [1000, 1500, 2000]}

        result_list = []

        # region 역대 순위 기록
        if how_state is None:
            df_total_pitchers_detail = self.recorder.get_total_pitchers_detail_df()
            df_total_pitchers_detail['INNING'] = round(df_total_pitchers_detail['INNING']).astype(int)

            for state in state_list:
                df_pitchers_detail = df_total_pitchers_detail.sort_values(by=state, ascending=False).reset_index()
                pitcher_rank = df_pitchers_detail[df_pitchers_detail['PCODE'] == str(self.player_code)].index[0] + 1
                pitcher_record = df_pitchers_detail.iloc[pitcher_rank - 1][state].astype(int)

                if pitcher_rank <= state_ranker_dict[state]:
                    set_ranker_dict = data_dict.copy()
                    set_ranker_dict['RESULT'] = pitcher_record
                    set_ranker_dict['RANK'] = pitcher_rank
                    if state == 'HOLD' or state == 'KK':
                        set_ranker_dict['STATE_KOR'] = "{0} {1}개".format(self.KOREAN_STATE_DICT[state], str(pitcher_record))
                    else:
                        set_ranker_dict['STATE_KOR'] = "{0} {1}".format(str(pitcher_record), self.KOREAN_STATE_DICT[state])
                    set_ranker_dict['STATE'] = state
                    set_ranker_dict['STATE_SPLIT'] = 'RANKER_TOTAL'
                    result_list.append(set_ranker_dict)
        # endregion 역대 순위 기록

        # region 역대 기록에 얼마나 남았는지
        df_total_pitchers = self.recorder.get_total_pitchers_df()

        if how_state == 'KK':
            state_record_dict = {'KK': [1000, 1500, 2000]}
        elif how_state is None:
            state_record_dict = state_records_dict
        else:
            return result_list

        for state, state_records_list in state_record_dict.items():
            for state_record_count in reversed(state_records_list):
                df_pitchers = df_total_pitchers.sort_values(by=state, ascending=False).reset_index()
                pitcher_rank = df_pitchers[df_pitchers['PCODE'] == str(self.player_code)].index[0] + 1
                pitcher_record = df_pitchers.iloc[pitcher_rank - 1][state].astype(int)

                if pitcher_record == state_record_count:
                    set_rank_left_dict = data_dict.copy()
                    set_rank_left_dict['RESULT'] = pitcher_record
                    set_rank_left_dict['RANK'] = pitcher_rank
                    if state == 'GAMENUM':
                        set_rank_left_dict['STATE_KOR'] = "{0}경기 {1}".format(str(pitcher_record),
                                                                             self.KOREAN_STATE_DICT[state])
                    else:
                        set_rank_left_dict['STATE_KOR'] = "{0} {1}".format(str(pitcher_record), self.KOREAN_STATE_DICT[state])
                    set_rank_left_dict['STATE'] = state
                    set_rank_left_dict['STATE_SPLIT'] = 'RANKER_TOTAL_NOW'
                    result_list.append(set_rank_left_dict)
                    break
                elif pitcher_record < state_record_count and (state_record_count - pitcher_record) <= 10:
                    query_string = "%s >= %d" % (state, state_record_count)
                    df_state_rank = df_total_pitchers.query(query_string)
                    state_rank = df_state_rank.shape[0]

                    set_rank_left_dict = data_dict.copy()
                    set_rank_left_dict['TOTAL_RESULT'] = pitcher_record
                    set_rank_left_dict['RECORD_RESULT'] = state_record_count
                    set_rank_left_dict['LEFT_RESULT'] = state_record_count - pitcher_record
                    set_rank_left_dict['RANK'] = state_rank + 1
                    if state == 'GAMENUM':
                        set_rank_left_dict['STATE_KOR'] = "경기 {0}".format(self.KOREAN_STATE_DICT[state])
                    else:
                        set_rank_left_dict['STATE_KOR'] = "{0}".format(self.KOREAN_STATE_DICT[state])
                    set_rank_left_dict['STATE'] = state
                    set_rank_left_dict['STATE_SPLIT'] = 'RANKER_TOTAL_LEFT'
                    result_list.append(set_rank_left_dict)
                    break
        # endregion 역대 기록에 얼마나 남았는지

        return result_list

    def get_pitcher_n_continue_data(self, game_id, how_state=None):
        """
        N게임, 타석, 시즌 연속 기록 데이터를 생성한다.
        :return:
        """
        n_game_count_dict = {'CG_W': 1, 'SHO_W': 1, 'W': 2, 'HOLD': 2, 'SV': 4}
        how_many_season_dict = {'W': 2, 'HOLD': 2, 'SV': 2}
        data_dict = {'HITTER': 'NA', 'HITNAME': 'NA', 'OPPONENT': 'ALL',
                     'LEAGUE': 'SEASON', 'PITCHER': self.player_code, 'PITNAME': self.player_info['NAME'],
                     'PITTEAM': 'NA', 'RANK': 1}
        result_list = []

        df_game_list = self.recorder.get_pitcher_continuous_record_v0(game_id, self.player_code)
        df_pitcher_record = self.recorder.get_pitcher_df(self.player_code)

        # region N타석 삼진 기록
        df_game_pa = df_game_list.sort_values(by='GDAY', ascending=False).head(50)
        kk_counter = 0
        for i in range(df_game_pa.shape[0]):
            if i == kk_counter and df_game_pa.iloc[i]['HOW'] == 'KK':
                kk_counter += 1
            else:
                break

        if kk_counter >= 2:
            set_kk_dict = data_dict.copy()
            set_kk_dict['RESULT'] = kk_counter
            set_kk_dict['STATE'] = 'KK'
            set_kk_dict['STATE_KOR'] = self.KOREAN_STATE_DICT['KK']
            set_kk_dict['STATE_SPLIT'] = "NPA_CONTINUE_KK"
            result_list.append(set_kk_dict)
        # endregion N타석 삼진 기록

        if how_state:
            return result_list

        # region N경기 완봉,완투,승,홀드,세이브 기록
        df_pitcher_record = df_pitcher_record.sort_values(by='GDAY', ascending=False).head(50)
        for state_col, state_count in n_game_count_dict.items():
            state_counter = 0
            team_list = []
            date_list = []
            for i in range(df_pitcher_record.shape[0]):
                if i == state_counter and df_pitcher_record.iloc[i][state_col] > 0:
                    state_counter += 1

                    if df_pitcher_record.iloc[i]['TB'] == 'T':
                        team_name = df_pitcher_record.iloc[i]['GMKEY'][8:10]
                    else:
                        team_name = df_pitcher_record.iloc[i]['GMKEY'][10:12]
                    team_list.append(team_name)
                    date_list.append( df_pitcher_record.iloc[i]['GDAY'])
                else:
                    break

            if state_counter >= state_count:
                if state_col == 'CG_W' or state_col == 'SHO_W':
                    if state_counter == 1:
                        set_cg_sho_dict = data_dict.copy()
                        set_cg_sho_dict['TEAM'] = self.TEAM_KOR_DICT[team_list[-1]]
                        set_cg_sho_dict['DATE'] = "%d월 %d일" % (int(date_list[-1][4:6]), int(date_list[-1][6:8]))
                        set_cg_sho_dict['STATE'] = state_col
                        set_cg_sho_dict['STATE_KOR'] = self.KOREAN_STATE_DICT[state_col]
                        set_cg_sho_dict['STATE_SPLIT'] = "LAST_GAME_%s" % state_col
                        result_list.append(set_cg_sho_dict)
                    else:
                        df_total_pitchers = self.recorder.get_total_pitchers_df()
                        df_pitchers = df_total_pitchers.sort_values(by=state_col, ascending=False).reset_index()
                        pitcher_rank = df_pitchers[df_pitchers['PCODE'] == str(self.player_code)].index[0] + 1
                        pitcher_record = df_pitchers.iloc[pitcher_rank - 1][state_col].astype(int)

                        set_cg_sho_dict = data_dict.copy()
                        set_cg_sho_dict['NGAME'] = state_counter
                        set_cg_sho_dict['STATE_RESULT'] = pitcher_record
                        set_cg_sho_dict['RANK'] = pitcher_rank
                        set_cg_sho_dict['STATE'] = state_col
                        set_cg_sho_dict['STATE_KOR'] = self.KOREAN_STATE_DICT[state_col]
                        set_cg_sho_dict['STATE_SPLIT'] = "NGAME_CONTINUE_%s" % state_col
                        result_list.append(set_cg_sho_dict)
                else:
                    df_pitcher_total = self.recorder.get_pitcher_season_realtime_record(game_id)
                    df_pitcher = df_pitcher_total.sort_values(by=state_col, ascending=False).reset_index()
                    pitcher_rank = df_pitcher[df_pitcher['PCODE'] == str(self.player_code)].index[0] + 1
                    pitcher_record = df_pitcher.iloc[pitcher_rank - 1][state_col].astype(int)

                    set_n_game_dict = data_dict.copy()
                    set_n_game_dict['NGAME'] = state_counter
                    set_n_game_dict['TEAM'] = self.TEAM_KOR_DICT[team_list[0]]
                    set_n_game_dict['DATE'] = "%d월 %d일" % (int(date_list[0][4:6]), int(date_list[0][6:8]))
                    set_n_game_dict['RANK'] = pitcher_rank
                    set_n_game_dict['STATE_RESULT'] = pitcher_record
                    set_n_game_dict['STATE'] = state_col
                    set_n_game_dict['STATE_KOR'] = self.KOREAN_STATE_DICT[state_col]
                    set_n_game_dict['STATE_SPLIT'] = "NGAME_CONTINUE"
                    result_list.append(set_n_game_dict)
        # endregion N경기 완봉,완투,승,홀드,세이브 기록

        # region N시즌 승, 홀드, 세이브 기록
        if not self.df_pitcher_all_season.empty:
            df_pitcher_years = self.df_pitcher_all_season
            for state_col, state_count in how_many_season_dict.items():
                state_counter = 0
                state_record_list = []
                state_year_list = []
                for i in range(df_pitcher_years.shape[0]):
                    if i == state_counter and df_pitcher_years.iloc[i][state_col] >= 10:
                        state_counter += 1
                        year_string = "%d" % (df_pitcher_years.iloc[i][state_col])
                        state_record_list.append(year_string)
                        state_year_list.append(df_pitcher_years.iloc[i]['GYEAR'])
                    else:
                        break

                if state_counter >= state_count:
                    # state_result = ', '.join(state_record_list[:-1])
                    state_result = ', '.join(state_record_list)
                    set_n_season_dict = data_dict.copy()
                    set_n_season_dict['NSEASON'] = state_counter
                    set_n_season_dict['YEAR_RESULT'] = '{0}~{1}'.format(state_year_list[-1], state_year_list[0][2:4])
                    # set_n_season_dict['STATE_RESULT'] = "{state_result:와} ".format(state_result=Noun(state_result)) + state_record_list[-1]
                    set_n_season_dict['STATE_RESULT'] = "{0}{1}".format(state_result, self.KOREAN_STATE_DICT[state_col])
                    set_n_season_dict['STATE'] = state_col
                    set_n_season_dict['STATE_KOR'] = self.KOREAN_STATE_DICT[state_col]
                    set_n_season_dict['STATE_SPLIT'] = "NSEASON_CONTINUE"
                    result_list.append(set_n_season_dict)
        # endregion N시즌 승, 홀드, 세이브 기록

        return result_list

    def get_pitcher_vs_team_data_v2(self, hitter_team):
        data_dict = {'HITTER': 'NA', 'HITNAME': 'NA', 'HITTEAM': self.TEAM_KOR_DICT[hitter_team],'OPPONENT': 'ALL',
                     'LEAGUE': 'SEASON', 'PITCHER': self.player_code, 'PITNAME': self.player_info['NAME'],
                     'PITTEAM': 'NA', 'RANK': 1}
        how_dict = {'ERA', 'KK'}

        result_list = []

        df_how = self.recorder.get_hitter_vs_team_df(self.player_code, hitter_team)

        if df_how.empty:
            return None

        return result_list

    def get_pitcher_vs_hitter_data_v2(self, hitter_code, hitter_team):
        data_dict = {'HITTER': hitter_code, 'HITNAME': 'NA', 'HITTEAM': self.TEAM_KOR_DICT[hitter_team], 'OPPONENT': 'ALL',
                     'LEAGUE': 'SEASON', 'PITCHER': self.player_code, 'PITNAME': self.player_info['NAME'],
                     'PITTEAM': 'NA', 'RANK': 1}
        how_dict = {'HIT': ['H1', 'H2', 'H3', 'HR', 'HI', 'HB'], 'KK': ['KK']}
        ab_list = ['H1', 'H2', 'H3', 'HR', 'HI', 'HB', 'GR', 'BN', 'FL', 'LL', 'IF', 'FF', 'KK', 'KN', 'KB', 'KW', 'KP', 'IP',
           'XX', 'FC', 'GD', 'TP']

        result_list = []

        df_how = self.recorder.get_hitter_vs_pitcher_df(hitter_code, self.player_code)

        if df_how.empty:
            return None

        vs_hit_count = df_how[df_how['HOW'].isin(how_dict['HIT'])].shape[0]
        vs_ab_count = df_how[df_how['HOW'].isin(ab_list)].shape[0]
        vs_pa_count = df_how.shape[0]

        vs_oba = round(vs_hit_count / vs_ab_count, 3)  # 피안타율

        df_pitcher_record = self.recorder.get_pitcher_df(self.player_code)
        df_pitcher = df_pitcher_record.drop(['GMKEY', 'GDAY', 'TB', 'START', 'QUIT'], axis=1)
        df_pitcher = df_pitcher.groupby(['PCODE']).sum()

        season_oba = round((df_pitcher.iloc[0]['HIT'] / df_pitcher.iloc[0]['AB']), 3)

        if vs_oba != season_oba:
            if season_oba > vs_oba:
                vs_result = '강한'
            else:
                vs_result = '약한'

            set_oba_dict = data_dict.copy()
            set_oba_dict['RESULT'] = vs_result
            set_oba_dict['SEASON_OBA'] = season_oba
            set_oba_dict['VERSUS_OBA'] = vs_oba
            set_oba_dict['STATE'] = 'OBA'
            set_oba_dict['STATE_SPLIT'] = "VS_HITTER_OBA"
            set_oba_dict['PA'] = vs_pa_count
            result_list.append(set_oba_dict)

        vs_kk_count = df_how[df_how['HOW'].isin(how_dict['KK'])].shape[0]
        vs_kk = round(vs_kk_count / vs_ab_count, 3)  # 삼진율

        if df_pitcher.iloc[0]['INN2'] > 0:
            season_kk = round((df_pitcher.iloc[0]['KK'] / df_pitcher.iloc[0]['AB']), 3)  # 삼진율
            if season_kk > vs_kk:
                vs_result = '약한'
            else:
                vs_result = '강한'

            set_kk_dict = data_dict.copy()
            set_kk_dict['RESULT'] = vs_result
            set_kk_dict['SEASON_OBA'] = season_kk
            set_kk_dict['VERSUS_OBA'] = vs_kk
            set_kk_dict['STATE'] = 'KK'
            set_kk_dict['STATE_SPLIT'] = "VS_HITTER_KK"
            set_kk_dict['PA'] = vs_pa_count
            result_list.append(set_kk_dict)

        return result_list
    # endregion Pitcher 기록

if __name__ == "__main__":
    hitter = Hitter(78224)
    pitcher = Pitcher(60263)
    result_how = hitter.get_season_hitter_event_10_units('20170912OBNC0')
    print(result_how)