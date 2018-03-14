from lib import record
from korean import Noun
from lib import game_status


class Commentate(object):

    def __init__(self):
        self.BALL_STUFF = {'FAST': '패스트볼', 'CUTT': '커터', 'SLID': '슬라이더', 'CURV': '커브',
                       'CHUP': '체인지업', 'SPLI': '스플리터', 'SINK': '싱커볼', 'TWOS': '투심패스트볼',
                       'FORK': '포크볼', 'KNUC': '너클볼'}
        self.TEAM_KOR = {"WO": "넥센", "SS": "삼성", "SK": "SK", "OB": "두산",
                         "NC": "NC", "LT": "롯데", "LG": "LG", "KT ": "kt", "HT": "기아", "HH": "한화"}
        self.POSITION_WORD = {"1": "P", "2": "C", "3": "1B", "4": "2B", "5": "3B", "6": "SS"
                              , "7": "LF", "8": "CF", "9": "RF", "D": "DH"}
        self.WPA_HOW_KOR = {'BB': '볼넷', 'BN': '번트', 'H1': '1루타', 'H2': '2루타', 'H3': '3루타',
                        'HB': '번트안타', 'HI': '내야안타', 'HP': '사구', 'HR': '홈런', 'IB': '고의4구', 'KP': '포일',
                        'KW': '폭투', 'SF': '희생플라이', 'SH': '희생번트', 'B2': '보크', 'PB': '패스트볼',
                        'P2': '포일', 'SB': '도루', 'SD': '더블스틸', 'ST': '트리플스틸', 'WP': '폭투', 'W2': '폭투'}

        self.continue_ball_stuff = {}
        self.continue_ball_count_b = 0
        self.continue_ball_count_f = 0
        self.max_li = 0

    @classmethod
    def get_first_ball_info(cls, hitter, ball_type):
        data_dict = {'HITTER': hitter, 'OPPONENT': 'NA', 'LEAGUE': 'NA', 'PITCHER': 'NA', 'PITNAME': 'NA',
                     'GYEAR': 'NA', 'PITTEAM': 'NA', 'STATE': 'FIRSTBALL'}

        result = []
        first_ball_data = record.Record().get_hitter_first_ball(hitter)

        if first_ball_data:
            first_ball_info = first_ball_data[0]

            if ball_type == 'S':
                if first_ball_info['T_CNT_RNK'] < 30:
                    first_ball_dict = data_dict.copy()
                    first_ball_dict['HITNAME'] = first_ball_info['HITNAME']
                    first_ball_dict['RANK'] = 1
                    first_ball_dict['STATE_SPLIT'] = '0S'
                    first_ball_dict['PA'] = first_ball_info['PA']
                    first_ball_dict['RESULT'] = first_ball_info['T_CNT_RNK']  # 아무데이터
                    result.append(first_ball_dict)

            elif ball_type == 'T':
                if first_ball_info['S_CNT_RNK'] < 30:
                    first_ball_dict = data_dict.copy()
                    first_ball_dict['HITNAME'] = first_ball_info['HITNAME']
                    first_ball_dict['RANK'] = 1
                    first_ball_dict['STATE_SPLIT'] = '0T'
                    first_ball_dict['PA'] = first_ball_info['PA']
                    first_ball_dict['RESULT'] = first_ball_info['S_CNT_RNK']  # 아무데이터
                    result.append(first_ball_dict)

        return result

    @classmethod
    def get_game_info(cls, game_key):
        stadium_info_list = record.Record().get_gameinfo_data(game_key)
        if stadium_info_list:
            stadium_info = stadium_info_list[0]

        if stadium_info:
            temp = int(stadium_info['Temp']) * 0.1
            result = [{'STADIUM': stadium_info['Stadium'], 'VTEAM': stadium_info['Vteam'], 'HTEAM': stadium_info['Hteam'],
                       'UMPC': stadium_info['Umpc'], 'UMP1': stadium_info['Ump1'], 'UMP2': stadium_info['Ump2'],
                       'UMP3': stadium_info['Ump3'], 'MOIS': stadium_info['Mois'], 'CHAJUN': stadium_info['Chajun'],
                       'TEMP': temp,
                       'STATE': 'GAMEINFO', 'STATE_SPLIT': 'GAMEINFO', 'RANK': 1}]
            return result
        else:
            return None

    def get_ball_style_data(self, game_key, bat_order, ball_count, pitcher, hitter, hit_type, pitname):
        result_list = []
        data_dict = {'SUBJECT': 'PITCHER', 'OPPONENT': 'NA', 'LEAGUE': 'NA', 'PITNAME': 'NA',
                       'GYEAR': 'NA', 'PITTEAM': 'NA', 'STATE': 'BALLINFO',
                       'RANK': 1}

        data_list = record.Record().get_pitzone_info(game_key, bat_order, ball_count, hitter, pitcher)

        if data_list:
            pitch_data = data_list[0]
            ball_style_dict = data_dict.copy()
            ball_dict = data_dict.copy()

            if pitch_data['stuff'] in self.BALL_STUFF:
                pitch_type = self.BALL_STUFF[pitch_data['stuff']]
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

            ball_style_dict['PITNAME'] = pitcher
            ball_style_dict['COMMENT'] = comment
            ball_style_dict['HITTER'] = hitter
            ball_style_dict['STUFF'] = pitch_type
            ball_style_dict['SPEED'] = pitch_data['speed']
            ball_style_dict['STATE_SPLIT'] = 'BALLINFO'
            result_list.append(ball_style_dict)

            if ball_type == 'B':
                ball_dict['PITNAME'] = pitname
                ball_dict['COMMENT'] = comment
                ball_dict['STUFF'] = pitch_type
                ball_dict['STATE_SPLIT'] = 'BALLINFO_BALL'
                result_list.append(ball_dict)

            return result_list
        else:
            return None

    def get_current_game_info(self, live_dict):
        result_list = []
        data_dict = {'OPPONENT': 'NA', 'LEAGUE': 'NA', 'PITCHER': 'NA', 'PITNAME': 'NA',
                     'GYEAR': 'NA', 'PITTEAM': 'NA', 'STATE': 'CURRENT_INFO'}
        game_id = live_dict['game_id']
        score_detail = live_dict['score_detail']
        score_simple = live_dict['score']
        seq_no = live_dict['seq_no']
        base_detail = live_dict['base_detail']
        out_count = live_dict['out_count']
        bat_order = live_dict['batorder']
        ball_count = live_dict['ballcount']
        text_style = live_dict['textStyle']
        full_count = live_dict['full_count']
        ball_type = live_dict['ball_type']
        how = live_dict['how']
        inning = live_dict['inning']
        tb = live_dict['tb']
        hit_team = live_dict['hitteam']
        year = live_dict['gyear']
        home_team = game_id[10:12]
        away_team = game_id[8:10]

        # region 팀 시즌 정보
        if seq_no == 0:
            home_team_info = record.Record().get_teamrank_daily(self.TEAM_KOR[home_team])
            away_team_info = record.Record().get_teamrank_daily(self.TEAM_KOR[away_team])
            if home_team_info:
                home_team_info = home_team_info[0]
                if home_team_info['GAME'] > 0:
                    home_team_dict = data_dict.copy()
                    home_team_dict['LEAGEU'] = 'SEASON'
                    home_team_dict['TEAM_NAME'] = home_team_info['TEAM']
                    home_team_dict['STATE_SPLIT'] = 'SEASON_TEAM_INFO'
                    home_team_dict.update(home_team_info)
                    result_list.append(home_team_dict)
            if away_team_info:
                away_team_info = away_team_info[0]
                if away_team_info['GAME'] > 0:
                    away_team_dict = data_dict.copy()
                    away_team_dict['LEAGEU'] = 'SEASON'
                    away_team_dict['TEAM_NAME'] = away_team_info['TEAM']
                    away_team_dict['STATE_SPLIT'] = 'SEASON_TEAM_INFO'
                    away_team_dict.update(away_team_info)
                    result_list.append(away_team_dict)
        # endregion 팀 시즌 정보

        # region 팀 대결 정보
        if seq_no == 0:
            team_vs_team_info = record.Record().get_team_vs_team(home_team, away_team, 2017)
            if team_vs_team_info:
                versus_info = team_vs_team_info[0]
                versus_dict = data_dict.copy()
                versus_dict['HOME_TEAM'] = self.TEAM_KOR[home_team]
                versus_dict['AWAY_TEAM'] = self.TEAM_KOR[away_team]
                versus_dict['STATE_SPLIT'] = 'VERSUS_TEAM'
                versus_dict['TEAM_NAME'] = '{name:는}'.format(name=Noun(self.TEAM_KOR[home_team]))
                versus_dict.update(versus_info)
                if versus_info['LOSS'] > versus_info['WIN']:
                    versus_dict['TEAM_NAME'] = '{name:는}'.format(name=Noun(self.TEAM_KOR[away_team]))
                    versus_dict['WIN'] = versus_info['LOSS']
                    versus_dict['LOSS'] = versus_info['WIN']
                elif versus_info['WIN'] == versus_info['LOSS']:
                    versus_dict['STATE_SPLIT'] = 'VERSUS_TEAM_SAME'
                result_list.append(versus_dict)
        # endregion 팀 대결 정보

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
                    score_temp = " 지고 있는 상황"
                else:
                    score_temp = " 이기고 있는 상황"
                score = "{0}점차로 {1}".format(score_detail[0], score_temp)

            current_game = data_dict.copy()
            current_game['LEAGUE'] = 'SEASON'
            current_game['STATE_SPLIT'] = 'CURRENT_INFO'
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
            full_count_dict['STATE_SPLIT'] = 'FULL_COUNT'
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

        if 2 < self.continue_ball_count_b < 4:
            continue_ball_dict = data_dict.copy()
            continue_ball_dict['LEAGUE'] = 'SEASON'
            continue_ball_dict['STATE_SPLIT'] = 'CONTINUE_BALL'
            continue_ball_dict['type'] = '볼'
            continue_ball_dict['count'] = self.continue_ball_count_b
            result_list.append(continue_ball_dict)
        elif self.continue_ball_count_f > 2:
            continue_ball_dict = data_dict.copy()
            continue_ball_dict['LEAGUE'] = 'SEASON'
            continue_ball_dict['STATE_SPLIT'] = 'CONTINUE_BALL'
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
                ball_stuff_dict['STATE_SPLIT'] = 'BALL_STUFF_COUNT'
                ball_stuff_dict['count'] = ball_stuff_value_list[0]
                ball_stuff_dict['ball_type'] = self.BALL_STUFF[ball_stuff_key_list[0]]
                result_list.append(ball_stuff_dict)
        # endregion

        # region 사구일 경우
        if how == 'HP':
            how_hp = data_dict.copy()
            how_hp['LEAGUE'] = 'SEASON'
            how_hp['STATE_SPLIT'] = 'HOW_HP'
            result_list.append(how_hp)
        # endregion

        # region 공수 교체시
        if bat_order == 0 and seq_no > 0:
            if score_detail[1] == 'L':
                when_loss = data_dict.copy()
                when_loss['LEAGUE'] = 'SEASON'
                when_loss['STATE_SPLIT'] = 'WHEN_LOSS'
                result_list.append(when_loss)
        # endregion

        # region 매 이닝 시작시 어디 공격 점수는 몇점
        if bat_order == 0:
            inning_start_dict = data_dict.copy()
            inning_start_dict['LEAGUE'] = 'SEASON'
            inning_start_dict['STATE_SPLIT'] = 'START_INNING'
            inning_start_dict['INNING'] = inning
            inning_start_dict['TB'] = '회초' if tb == 'T' else '회말'
            inning_start_dict['TEAM'] = self.TEAM_KOR[hit_team]
            inning_start_dict['WHAT'] = '반격' if score_simple[1] == 'L' else '공격'
            result_list.append(inning_start_dict)
        # endregion

        # region Max LI
        if inning > 5:
            max_li_rt = record.Record().get_max_li_rate(game_id, seq_no)[0]['VALUE']
            curr_li_rt = record.Record().get_li_rate(year, inning, tb, out_count, base_detail, score_detail)[0]['VALUE']

            if self.max_li < max_li_rt:
                self.max_li = max_li_rt

            if self.max_li < curr_li_rt:
                self.max_li = curr_li_rt
                if self.max_li < 3:
                    state_split = 'MAX_LI_MIDDLE'
                elif 3 <= self.max_li < 6:
                    state_split = 'MAX_LI_PEAK'
                elif 6 <= self.max_li:
                    state_split = 'MAX_LI_DONE'
                max_li = data_dict.copy()
                max_li['LEAGUE'] = 'SEASON'
                max_li['STATE_SPLIT'] = state_split
                result_list.append(max_li)
        # endregion Max LI

        # region WPA 변화량에 따른 승리 확률
        if inning > 3 and how in self.WPA_HOW_KOR:
            record_matrix_dict = None
            record_matrix = record.Record().get_record_matrix_mix(game_id, year, seq_no)
            if record_matrix:
                record_matrix_dict = record_matrix[0]

            if record_matrix_dict and record_matrix_dict['WPA_RT'] > 0.1:
                wpa_rt = record_matrix_dict['WPA_RT']
                after_we_rt = record_matrix_dict['AFTER_WE_RT']
                before_we_rt = record_matrix_dict['BEFORE_WE_RT']

                home_after_we_rt = round(after_we_rt * 100)
                away_after_we_rt = round((1 - after_we_rt) * 100)
                wpa_rt = round(wpa_rt * 100)

                if (tb == 'T' and after_we_rt - before_we_rt < 0) or (tb == 'B' and after_we_rt - before_we_rt > 0):
                    wpa_rate = data_dict.copy()
                    wpa_rate['LEAGUE'] = 'SEASON'
                    wpa_rate['STATE_SPLIT'] = 'WPA_RATE'
                    wpa_rate['HOW'] = "{state:이}".format(state=Noun(self.WPA_HOW_KOR[how]))
                    if tb == 'T':
                        wpa_rate['TEAM'] = self.TEAM_KOR[away_team]
                    else:
                        wpa_rate['TEAM'] = self.TEAM_KOR[home_team]
                    wpa_rate['WPA_RT'] = wpa_rt
                    wpa_rate['HOME_TEAM'] = self.TEAM_KOR[home_team]
                    wpa_rate['AWAY_TEAM'] = self.TEAM_KOR[away_team]
                    wpa_rate['HOME_WE_RT'] = home_after_we_rt
                    wpa_rate['AWAY_WE_RT'] = away_after_we_rt
                    result_list.append(wpa_rate)
        # endregion WPA 변화량에 따른 승리 확률
        return result_list

    def get_starting_line_info(self, tb, starting_line_dict):
        data_dict = {'LEAGUE': 'SEASON'}
        result_list = []

        for tb_key, starting_line in starting_line_dict.items():
            starting_dict = data_dict.copy()
            if tb_key == tb:  # 공격
                starting_dict['TEAM'] = self.TEAM_KOR[starting_line[0]['team']]
                starting_dict['STATE_SPLIT'] = 'LINE_UP_BATTING'
                starting_dict['STATE'] = 'LINE_UP_INFO'
                for starting in starting_line:
                    num = "num_{}".format(starting['turn'][1])
                    starting_dict[num] = starting['name']
            else:  # 수비
                starting_dict['TEAM'] = self.TEAM_KOR[starting_line[0]['team']]
                starting_dict['STATE_SPLIT'] = 'LINE_UP_FIELD'
                starting_dict['STATE'] = 'LINE_UP_INFO'
                for starting in starting_line:
                    position = self.POSITION_WORD[starting['posi'][1]]
                    starting_dict[position] = starting['name']
            result_list.append(starting_dict)

        return result_list

    def get_team_info(self, team_info):
        result_list = []

        for tb_key, team in team_info.items():
            if tb_key == "tteam":
                team['STATE_SPLIT'] = 'TEAM_INFO'
                team['STATE'] = 'TEAM_INFO'
            else:
                team['STATE_SPLIT'] = 'TEAM_INFO'
                team['STATE'] = 'TEAM_INFO'
            result_list.append(team)

        return result_list
