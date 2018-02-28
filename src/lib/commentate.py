from lib import record
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
        self.continue_ball_stuff = {}
        self.continue_ball_count_b = 0
        self.continue_ball_count_f = 0

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
    def get_game_info(cls, game_info_dict):
        info_dict = game_info_dict
        if game_info_dict:
            temp = int(info_dict['Temp']) * 0.1
            result = [{'STADIUM': info_dict['Stadium'], 'VTEAM': info_dict['Vteam'], 'HTEAM': info_dict['Hteam'],
                       'UMPC': info_dict['Umpc'], 'UMP1': info_dict['Ump1'], 'UMP2': info_dict['Ump2'],
                       'UMP3': info_dict['Ump3'], 'MOIS': info_dict['Mois'], 'CHAJUN': info_dict['Chajun'],
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
        home_team = live_dict['gameID'][10:12]
        away_team = live_dict['gameID'][8:10]

        # region 팀 시즌 정보
        if seq_no == 0:
            home_team_info = record.Record().get_teamrank_daily(home_team)
            away_team_info = record.Record().get_teamrank_daily(away_team)
            home_team_dict = data_dict.copy()
            home_team_dict['LEAGEU'] = 'SEASON'
            home_team_dict['TEAM_NAME'] = self.TEAM_KOR[home_team_info['TEAM']]
            home_team_dict['STATE_SPLIT'] = 'SEASON_TEAM_INFO'
            home_team_dict.update(home_team_info)
            result_list.append(home_team_dict)

            away_team_dict = data_dict.copy()
            away_team_dict['LEAGEU'] = 'SEASON'
            away_team_dict['TEAM_NAME'] = self.TEAM_KOR[away_team_info['TEAM']]
            away_team_dict['STATE_SPLIT'] = 'SEASON_TEAM_INFO'
            away_team_dict.update(away_team_info)
            result_list.append(away_team_dict)
        # endregion 팀 시즌 정보

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
