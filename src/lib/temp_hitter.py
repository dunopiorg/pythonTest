from lib import player


class Hitter(player.Player):

    # region Return Hitter 경기기록
    def get_today_hitter_data(self, game_id):
        result = []
        hitter = self.player_code
        today = self.recorder.get_hitter_today_record(game_id, hitter)
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

            self.set_today_hitter_dict(today)

        if result:
            self.today_record = result
        return self.today_record

    def get_total_hitter_basic_data(self):
        self.total_record = self.recorder.get_hitter_basic_record(self.player_code)
        self.set_total_hitter_basic_dict(self.total_record)
        return self.total_record

    def get_total_hitter_split_data(self, live_dict):
        result = self.recorder.get_total_hitter_split_record(live_dict)
        if result:
            return result
        else:
            return None

    def get_n_game_data(self):
        state_dict = {'HIT': ['H1', 'H2', 'H3', 'HR', 'HI', 'HB'], 'HR': ['HR'],
                      'RBI': ['E', 'R', 'H'], 'BB': ['BB', 'IB'], 'KK': ['KK']}
        data_dict = {'SUBJECT': 'HITTER', 'OPPONENT': 'ALL', 'LEAGUE': 'SEASON',
                     'PITCHER': 'NA', 'PITNAME': 'NA', 'PITTEAM': 'NA'}

        hitter_gm_list = self.recorder.get_hitter_continuous_record(self.player_code)
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
                            set_dict = data_dict.copy()
                            set_dict['RESULT'] = counter
                            set_dict['STATE'] = state_k
                            set_dict['STATE_SPLIT'] = 'NGAME'
                            result.append(set_dict)
                        break
        if result:
            self.n_game_record = result
            self.set_n_game_hitter_dict(result)
            return self.n_game_record
        else:
            return None

    def get_n_pa_data(self):
        state_dict = {'HIT': ['H1', 'H2', 'H3', 'HR', 'HI', 'HB'], 'HR': ['HR'], 'RBI': ['E', 'R', 'H'],
                      'BB': ['BB', 'IB'], 'KK': ['KK']}
        data_dict = {'SUBJECT': 'HITTER', 'OPPONENT': 'ALL', 'LEAGUE': 'SEASON', 'PITCHER': 'NA', 'PITNAME': 'NA',
                     'PITTEAM': 'NA'}

        hitter_gm_list = self.recorder.get_hitter_continuous_record(self.player_code)
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
                        set_dict = data_dict.copy()
                        set_dict['RESULT'] = counter
                        set_dict['STATE'] = state_k
                        set_dict['STATE_SPLIT'] = 'NPA'
                        result.append(set_dict)
                    break

        if result:
            self.n_pa_record = result
            self.set_n_pa_hitter_dict(result)
            return self.n_pa_record
        else:
            return None

    # endregion

    # region Hitter 정보 변수 셋팅
    def set_today_hitter_dict(self, record_dict):
        self.today_record_dict.update(record_dict)

    def set_total_hitter_basic_dict(self, record_dict):
        # {'SEASON': {'KK': 115.0, 'HR': 35.0, 'H2': 34.0, ...}, 'ALL': {'KK': 286.0,...}
        for r in record_dict:
            if r['LEAGUE'] in self.total_basic_record_dict:
                self.total_basic_record_dict[r['LEAGUE']].update({r['STATE']: [r['RESULT'], r['RNK']]})
            else:
                self.total_basic_record_dict.update({r['LEAGUE']: {r['STATE']: [r['RESULT'], r['RNK']]}})

    def set_n_game_hitter_dict(self, record_dict):
        for r in record_dict:
            self.n_game_record_dict[r['STATE']] = r['RESULT']

    def set_n_pa_hitter_dict(self, record_dict):
        for r in record_dict:
            self.n_pa_record_dict[r['STATE']] = r['RESULT']
    # endregion


if __name__ == "__main__":
    h = Hitter('78224')
    data = {'hitter': 78224, 'hitteam': 'OB', 'pitcher': 79140, 'pitteam': 'LG', 'state': 'HR', 'score': '0D',
            'base': '1B'}
    h.get_total_hitter_split_data(data)
