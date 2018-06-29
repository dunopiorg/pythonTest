from lib import record
from korean import Noun
import math
import config
import kor_dic


class Commentate(object):

    def __init__(self):
        self.BALL_STUFF = kor_dic.ball_stuff_dict
        self.TEAM_KOR = record.Record().get_team_korean_names()
        self.english_team = ['SK', 'NC', 'LG', 'KT']
        self.POSITION_WORD = kor_dic.position_dict
        self.WPA_HOW_KOR = kor_dic.how_kor_dict

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
                if first_ball_info['T_CNT_RNK'] < 10:
                    first_ball_dict = data_dict.copy()
                    first_ball_dict['HITNAME'] = first_ball_info['HITNAME']
                    first_ball_dict['RANK'] = 1
                    first_ball_dict['STATE_SPLIT'] = '0S'
                    first_ball_dict['PA'] = first_ball_info['PA']
                    first_ball_dict['RESULT'] = first_ball_info['T_CNT_RNK']  # 아무데이터
                    result.append(first_ball_dict)

            elif ball_type == 'T':
                if first_ball_info['S_CNT_RNK'] < 10:
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

    def get_pts_ball_data(self, game_key, bat_order, ball_count, pitcher, hitter, hit_type, pitname):
        result_list = []
        data_dict = {'SUBJECT': 'PITCHER', 'OPPONENT': 'NA', 'LEAGUE': 'NA', 'PITNAME': 'NA',
                       'GYEAR': 'NA', 'PITTEAM': 'NA', 'STATE': 'BALLINFO',
                       'RANK': 1}

        data_list = record.Record().get_pitzone_info(game_key, bat_order, ball_count, hitter, pitcher)

        if not data_list:
            return None

        pitch_data = data_list[0]

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

        if config.VERSION_LEVEL > 0:
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

            ball_style_dict = data_dict.copy()
            ball_style_dict['PITNAME'] = pitcher
            ball_style_dict['COMMENT'] = comment
            ball_style_dict['HITTER'] = hitter
            ball_style_dict['STUFF'] = pitch_type
            ball_style_dict['SPEED'] = pitch_data['speed']
            ball_style_dict['STATE_SPLIT'] = 'BALLINFO'
            result_list.append(ball_style_dict)

            if ball_type == 'B':
                ball_dict = data_dict.copy()
                ball_dict['PITNAME'] = pitname
                ball_dict['COMMENT'] = comment
                ball_dict['STUFF'] = pitch_type
                ball_dict['STATE_SPLIT'] = 'BALLINFO_BALL'
                result_list.append(ball_dict)
        else:
            if ball_type == 'T':
                up_down = ''
                right_left = ''

                if area_y < 64:
                    y_distance = 64 - area_y
                elif area_y > 224:
                    y_distance = area_y - 224
                else:
                    y_distance = 0

                if area_x < 51:
                    x_distance = 51 - area_x
                elif area_x > 176:
                    x_distance = area_x - 176
                else:
                    x_distance = 0

                distance = math.sqrt(y_distance**2 + x_distance**2)

                if distance <= 10:
                    distance_kor = "걸친"
                elif distance <= 20:
                    distance_kor = "많이 빠진"
                else:
                    distance_kor = "굉장히 많이 빠진"

                # 상단
                if 51 < area_x < 176 and area_y < 64:
                    up_down = '위'
                # 하단
                elif 51 < area_x < 176 and area_y > 224:
                    up_down = '아래'

                # 오른쪽으로 많이 빠진 공
                if area_x > 176:
                    if hit_type == '우타':
                        right_left = '몸쪽'
                    else:
                        right_left = '바깥쪽'
                # 왼쪽으로 많이 빠진 공
                elif area_x < 51:
                    if hit_type == '우타':
                        right_left = '바깥쪽'
                    else:
                        right_left = '몸쪽'

                if right_left + up_down:
                    ball_area_dict = data_dict.copy()
                    ball_area_dict['PITNAME'] = pitcher
                    ball_area_dict['STUFF'] = pitch_type
                    ball_area_dict['SPEED'] = pitch_data['speed']
                    ball_area_dict['DISTANCE'] = distance_kor
                    ball_area_dict['BALL_COUNT'] = ball_count
                    if right_left and up_down:
                        ball_area_dict['AREA'] = "{} {}".format(right_left, up_down)
                    elif right_left:
                        ball_area_dict['AREA'] = right_left
                    elif up_down:
                        ball_area_dict['AREA'] = up_down

                    ball_area_dict['STATE_SPLIT'] = 'BALL_AREA'
                    result_list.append(ball_area_dict)
            elif ball_type == 'B':
                if 51 < area_x < 176 and 64 < area_y < 224:
                    up_down = ''
                    right_left = ''

                    if 1 < zone_y < 4:
                        up_down = '위'
                    elif 4 < zone_y < 7:
                        up_down = '아래'

                    if 1 < zone_x < 4:
                        if hit_type == '우타':
                            right_left = '바깥쪽'
                        else:
                            right_left = '몸쪽'
                    elif 4 < zone_x < 7:
                        if hit_type == '우타':
                            right_left = '몸쪽'
                        else:
                            right_left = '바깥쪽'

                    ball_dict = data_dict.copy()
                    ball_dict['PITNAME'] = pitcher
                    ball_dict['STUFF'] = pitch_type
                    ball_dict['SPEED'] = pitch_data['speed']
                    ball_dict['BALL_COUNT'] = ball_count
                    if right_left and up_down:
                        ball_dict['AREA'] = "{} {}".format(right_left, up_down)
                    elif right_left:
                        ball_dict['AREA'] = right_left
                    elif up_down:
                        ball_dict['AREA'] = up_down
                    ball_dict['STATE_SPLIT'] = 'BALL_AREA_BALL'
                    result_list.append(ball_dict)
        return result_list

    def get_current_game_info(self, live_dict):
        result_list = []
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
        curr_li_rt = record.Record().get_li_rate(year, inning, tb, out_count, base_detail, score_detail)[0]['VALUE']
        if self.max_li < curr_li_rt:
            self.max_li = curr_li_rt
        data_dict = {'OPPONENT': 'NA', 'LEAGUE': 'NA', 'PITCHER': 'NA', 'PITNAME': 'NA',
                     'GYEAR': 'NA', 'PITTEAM': 'NA', 'STATE': 'CURRENT_INFO'}

        # region Detail Version
        if config.VERSION_LEVEL > 0:
            # region 팀 시즌 정보
            if seq_no == 0:
                away_team_info = record.Record().get_teamrank_daily(self.TEAM_KOR[away_team])
                if away_team_info:
                    away_team_info = away_team_info[0]
                    if away_team_info['GAME'] > 0:
                        away_team_dict = data_dict.copy()
                        away_team_dict['LEAGEU'] = 'SEASON'
                        away_team_dict['TEAM_NAME'] = away_team_info['TEAM']
                        if int(away_team_info['CONTINUE'][0]) > 1:
                            away_team_dict['STATE_SPLIT'] = 'SEASON_TEAM_INFO_CONTINUE'
                            away_team_dict['CONTINUE'] = '{0}연{1}'.format(away_team_info['CONTINUE'][0], away_team_info['CONTINUE'][1])
                        else:
                            away_team_dict['STATE_SPLIT'] = 'SEASON_TEAM_INFO'
                        away_team_dict.update(away_team_info)
                        result_list.append(away_team_dict)
            elif bat_order == 0 and inning == 1 and tb == 'B':
                home_team_info = record.Record().get_teamrank_daily(self.TEAM_KOR[home_team])
                if home_team_info:
                    home_team_info = home_team_info[0]
                    if home_team_info['GAME'] > 0:
                        home_team_dict = data_dict.copy()
                        home_team_dict['LEAGEU'] = 'SEASON'
                        home_team_dict['TEAM_NAME'] = home_team_info['TEAM']
                        if int(home_team_info['CONTINUE'][0]) > 1:
                            home_team_dict['STATE_SPLIT'] = 'SEASON_TEAM_INFO_CONTINUE'
                            home_team_dict['CONTINUE'] = '{0}연{1}'.format(home_team_info['CONTINUE'][0], home_team_info['CONTINUE'][1])
                        else:
                            home_team_dict['STATE_SPLIT'] = 'SEASON_TEAM_INFO'
                        home_team_dict.update(home_team_info)
                        result_list.append(home_team_dict)
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
                    if home_team in self.english_team:
                        versus_dict['TEAM_NAME'] = '{name}는'.format(name=self.TEAM_KOR[home_team])
                    else:
                        versus_dict['TEAM_NAME'] = '{name:는}'.format(name=Noun(self.TEAM_KOR[home_team]))
                    versus_dict.update(versus_info)
                    if versus_info['LOSS'] > versus_info['WIN']:
                        if home_team in self.english_team:
                            versus_dict['TEAM_NAME'] = '{name}는'.format(name=self.TEAM_KOR[away_team])
                        else:
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
            # endregion 등판시 주루상황, 점수상황, 아웃상황

            # region 선수 정보
            if text_style == 8:
                hitter_info = record.Record().get_player_info(live_dict['hitter'])[0]
                pitcher_info = record.Record().get_player_info(live_dict['pitcher'])[0]

                if hitter_info['CAREER2'] == pitcher_info['CAREER2']:
                    players_dict = data_dict.copy()
                    players_dict['HITTER'] = hitter_info['NAME']
                    players_dict['PITCHER'] = pitcher_info['NAME']
                    players_dict['CAREER'] = pitcher_info['CAREER2']
                    players_dict['STATE_SPLIT'] = 'SAME_CAREER'
                    result_list.append(players_dict)

                if hitter_info['BIRTH'][4:8] == game_id[4:8]:
                    birth_dict = data_dict.copy()
                    birth_dict['PLAYER'] = hitter_info['NAME']
                    birth_dict['STATE_SPLIT'] = 'PLAYER_BIRTHDAY'
                    result_list.append(birth_dict)
                elif pitcher_info['BIRTH'][4:8] == game_id[4:8]:
                    birth_dict = data_dict.copy()
                    birth_dict['PLAYER'] = pitcher_info['NAME']
                    birth_dict['STATE_SPLIT'] = 'PLAYER_BIRTHDAY'
                    result_list.append(birth_dict)
            # endregion 선수 정보

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
                        print("캐스터: 쓰리볼")
            # endregion Ball Count 설명

            # region Full count
            if full_count[0] == 2 and full_count[1] == 3 and text_style == 1:
                full_count_dict = data_dict.copy()
                full_count_dict['LEAGUE'] = 'SEASON'
                full_count_dict['STATE_SPLIT'] = 'FULL_COUNT'
                result_list.append(full_count_dict)
            # endregion Full count

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
            # endregion 연속 볼, 연속 파울 설정

            # region 사구일 경우
            if how == 'HP':
                how_hp = data_dict.copy()
                how_hp['LEAGUE'] = 'SEASON'
                how_hp['STATE_SPLIT'] = 'HOW_HP'
                result_list.append(how_hp)
            # endregion 사구일 경우

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
            # endregion 매 이닝 시작시 어디 공격 점수는 몇점

            # region 공수 교체시
            if bat_order == 0 and seq_no > 0 and curr_li_rt > 1:
                if score_detail[1] == 'L':
                    when_loss = data_dict.copy()
                    when_loss['LEAGUE'] = 'SEASON'
                    if hit_team in self.english_team:
                        when_loss['TEAM'] = '{team}가'.format(team=self.TEAM_KOR[hit_team])
                    else:
                        when_loss['TEAM'] = '{team:이}'.format(team=Noun(self.TEAM_KOR[hit_team]))
                    when_loss['STATE_SPLIT'] = 'WHEN_LOSS'
                    result_list.append(when_loss)
            # endregion 공수 교체시

            # region 연속 같은 볼
            if ball_type == 'H':
                self.continue_ball_stuff.clear()
            else:
                ball_stuff_value_list = list(self.continue_ball_stuff.values())
                ball_stuff_key_list = list(self.continue_ball_stuff.keys())
                if ball_stuff_value_list and ball_stuff_value_list[0] > 2:
                    ball_stuff_dict = data_dict.copy()
                    ball_stuff_dict['LEAGUE'] = 'SEASON'
                    if ball_stuff_value_list[0] > 4:
                        ball_stuff_dict['STATE_SPLIT'] = 'BALL_STUFF_COUNT_MANY'
                    else:
                        ball_stuff_dict['STATE_SPLIT'] = 'BALL_STUFF_COUNT'
                    ball_stuff_dict['count'] = ball_stuff_value_list[0]
                    ball_stuff_dict['ball_type'] = self.BALL_STUFF[ball_stuff_key_list[0]]
                    result_list.append(ball_stuff_dict)
            # endregion 연속 같은 볼
        # endregion Detail Version

        # region LI 관련
        if inning > 5 and text_style == 8:
            if self.max_li == curr_li_rt:
                if self.max_li < 3:
                    state_split = 'MAX_LI_MIDDLE'
                elif 3 <= self.max_li < 6:
                    state_split = 'MAX_LI_PEAK'
                elif 6 <= self.max_li:
                    state_split = 'MAX_LI_DONE'
                else:
                    state_split = 'MAX_LI'
                max_li = data_dict.copy()
                max_li['HITNAME'] = live_dict['hitname']
                max_li['LEAGUE'] = 'SEASON'
                max_li['STATE_SPLIT'] = state_split
                result_list.append(max_li)
            elif curr_li_rt > 1:
                if out_count == 0:
                    out = '무'
                else:
                    out = out_count
                li_dict = data_dict.copy()
                li_dict['HITNAME'] = live_dict['hitname']
                li_dict['LEAGUE'] = 'SEASON'
                li_dict['DIFF_SCORE'] = score_detail[0]
                li_dict['OUTCOUNT'] = out
                if tb == 'T':
                    li_dict['TEAM_NAME'] = self.TEAM_KOR[away_team]
                else:
                    li_dict['TEAM_NAME'] = self.TEAM_KOR[home_team]
                if base_detail == '123B':
                    li_dict['RUNNER'] = '만루에'
                elif base_detail == '0B':
                    li_dict['RUNNER'] = '없이'
                else:
                    li_dict['RUNNER'] = ', '.join(base_detail[:-1]) + '루에'

                state_split = ''
                if base_detail == '0B' and score_detail[1] == 'W':
                    state_split = 'LI_NO_W'
                elif base_detail in ['23B', '123B'] and score_detail == '1L':
                    state_split = 'LI_RUN_B_1L'
                elif base_detail in ['23B', '123B'] and score_detail[1] == 'L':
                    state_split = 'LI_RUN_B_L'
                elif base_detail in ['23B', '123B'] and score_detail == '0D':
                    state_split = 'LI_RUN_B_D'
                elif base_detail in ['23B', '123B']:
                    state_split = 'LI_RUN_B'
                elif base_detail in ['2B', '3B', '13B'] and score_detail == '1L':
                    state_split = 'LI_ON_B_1L'
                elif base_detail in ['2B', '3B', '13B'] and score_detail == '0D':
                    state_split = 'LI_ON_B_D'

                li_dict['STATE_SPLIT'] = state_split
                if state_split:
                    result_list.append(li_dict)
        # endregion LI 관련

        # region WPA 변화량에 따른 승리 확률
        if inning > 3 and how in self.WPA_HOW_KOR:
            record_matrix = record.Record().get_record_matrix_mix_by_seq(game_id, year, seq_no)
            if record_matrix:
                after_we_rt = record_matrix[0]['AFTER_WE_RT']
                before_we_rt = record_matrix[0]['BEFORE_WE_RT']
                after_score_gap = record_matrix[0]['AFTER_SCORE_GAP_CN']
                before_score_gap = record_matrix[0]['BEFORE_SCORE_GAP_CN']
                batter = record_matrix[0]['BAT_P_ID']
                hitter_info = record.Record().get_player_info(batter)[0]
                wpa_rt = after_we_rt - before_we_rt

                if abs(wpa_rt) > 0.1:
                    home_after_we_rt = round(after_we_rt * 100)
                    away_after_we_rt = round((1 - after_we_rt) * 100)
                    wpa_rt_p = abs(round(wpa_rt * 100))
                    wpa_rate = data_dict.copy()
                    wpa_rate['LEAGUE'] = 'SEASON'
                    wpa_rate['STATE_SPLIT'] = ''
                    wpa_rate['HOW'] = self.WPA_HOW_KOR[how]
                    if tb == 'T':
                        wpa_rate['TEAM'] = self.TEAM_KOR[away_team]
                    else:
                        wpa_rate['TEAM'] = self.TEAM_KOR[home_team]
                    wpa_rate['HITNAME'] = hitter_info['NAME']
                    wpa_rate['WPA_RT'] = wpa_rt_p
                    wpa_rate['HOME_TEAM'] = self.TEAM_KOR[home_team]
                    wpa_rate['AWAY_TEAM'] = self.TEAM_KOR[away_team]
                    wpa_rate['HOME_WE_RT'] = home_after_we_rt
                    wpa_rate['AWAY_WE_RT'] = away_after_we_rt
                    if tb == 'T':
                        wpa_rate['TEAM_WE_RT'] = away_after_we_rt
                    else:
                        wpa_rate['TEAM_WE_RT'] = home_after_we_rt

                    if (tb == 'T' and after_score_gap < 0 < before_score_gap) or (tb == 'B' and before_score_gap < 0 < after_score_gap):
                        wpa_rate['STATE_SPLIT'] = 'WPA_RATE_TURNED'
                    elif (tb == 'T' and before_score_gap > 0 and after_score_gap == 0) or (tb == 'B' and before_score_gap < 0 and after_score_gap == 0):
                        wpa_rate['STATE_SPLIT'] = 'WPA_RATE_DRAW'
                    elif (tb == 'T' and wpa_rt < 0 and after_we_rt < 0.5) or (tb == 'B' and wpa_rt > 0 and after_we_rt > 0.5):
                        wpa_rate['STATE_SPLIT'] = 'WPA_RATE'

                    if wpa_rate['STATE_SPLIT']:
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

    def get_end_inn_info(self, live_dict):
        data_dict = {'LEAGUE': 'SEASON', 'PITCHER': 'NA', 'PITNAME': 'NA',
                     'GYEAR': 'NA', 'PITTEAM': 'NA', 'STATE': 'END_INNING'}
        result_list = []
        game_id = live_dict['game_id']
        score_detail = live_dict['score_detail']
        score_simple = live_dict['score']
        seq_no = live_dict['seq_no']
        base_detail = live_dict['base_detail']
        out_count = live_dict['out_count']
        bat_order = live_dict['batorder']
        ball_count = live_dict['ballcount']
        full_count = live_dict['full_count']
        how = live_dict['how']
        inning = live_dict['inning']
        tb = live_dict['tb']
        hit_team = live_dict['hitteam']
        year = live_dict['gyear']
        home_team = game_id[10:12]
        away_team = game_id[8:10]

        df_record_matrix = record.Record().get_record_matrix_mix(game_id, year)
        df_inning_record_matrix = record.Record().get_ie_inningrecord(game_id, year)

        if df_record_matrix.empty or df_inning_record_matrix.empty:
            return None

        if int(inning) > 1and tb == 'T':
            prev_inning = inning - 1
        else:
            prev_inning = inning

        df_inning = df_inning_record_matrix[(df_inning_record_matrix['tb'] == tb) & (df_inning_record_matrix['inning'] == prev_inning)]
        df_pa_record = df_record_matrix[(df_record_matrix['TB_SC'] == tb) & (df_record_matrix['INN_NO'] == prev_inning)]

        # region 타자 시점
        if df_inning['run'].values[0] == 0:
            # 무득점 : LI가 가장 높았을 때 & 득점권 상황 but 점수를 못 냄
            df_max_li = df_pa_record[df_pa_record['AFTER_LI_RT'] == df_pa_record['AFTER_LI_RT'].max()]
            runner_sc = str(df_max_li['AFTER_RUNNER_SC'].values[0])
            if '2' in runner_sc or '3' in runner_sc:
                before_out_cn = df_max_li['BEFORE_OUT_CN'].values[0]
                before_runner_sc = str(df_max_li['BEFORE_RUNNER_SC'].values[0])
                hitter_code = df_max_li['BAT_P_ID'].values[0]
                how_kor = self.WPA_HOW_KOR[df_max_li['HOW_ID'].values[0]]
                hitter_name = record.Record().get_player_info(hitter_code)[0]['NAME']
                no_score_dict = data_dict.copy()
                if before_out_cn == 0:
                    no_score_dict['BEFORE_OUT_CN'] = "무"
                else:
                    no_score_dict['BEFORE_OUT_CN'] = before_out_cn
                if before_runner_sc == '123':
                    no_score_dict['BEFORE_RUNNER_SC'] = "만루"
                elif before_runner_sc == '0':
                    no_score_dict['BEFORE_RUNNER_SC'] = ""
                else:
                    no_score_dict['BEFORE_RUNNER_SC'] = "{0}루".format(','.join(before_runner_sc))

                if runner_sc == '123':
                    no_score_dict['AFTER_RUNNER_SC'] = "만루"
                elif runner_sc == '0':
                    no_score_dict['AFTER_RUNNER_SC'] = ""
                else:
                    no_score_dict['AFTER_RUNNER_SC'] = "{0}루".format(','.join(runner_sc))
                no_score_dict['HOW_KOR'] = how_kor
                no_score_dict['HITNAME'] = hitter_name
                no_score_dict['STATE_SPLIT'] = 'NO_RUN_SCORE_BASE'
                result_list.append(no_score_dict)
        else:
            # 득점 : 시간 순서대로 득점(적시타, 홈런)상황
            for idx, row in df_pa_record.iterrows():
                before_score_gap = row['BEFORE_SCORE_GAP_CN']
                after_score_gap = row['AFTER_SCORE_GAP_CN']
                before_out_cn = row['BEFORE_OUT_CN']
                before_runner_sc = row['BEFORE_OUT_CN']
                how_kor = self.WPA_HOW_KOR[row['HOW_ID']]
                hitter_name = record.Record().get_player_info(row['BAT_P_ID'])[0]['NAME']
                score_dict = data_dict.copy()

                if 'T' == row['TB_SC']:
                    score_cn = before_score_gap - after_score_gap
                else:
                    score_cn = after_score_gap - before_score_gap

                if before_out_cn == 0:
                    score_dict['BEFORE_OUT_CN'] = "무"
                else:
                    score_dict['BEFORE_OUT_CN'] = before_out_cn
                if before_runner_sc == '123':
                    score_dict['BEFORE_RUNNER_SC'] = "만루"
                elif before_runner_sc == '0':
                    score_dict['BEFORE_RUNNER_SC'] = ""
                else:
                    score_dict['BEFORE_RUNNER_SC'] = "{0}루".format(','.join(before_runner_sc))
                score_dict['HOW_KOR'] = how_kor
                score_dict['SCORE_CN'] = score_cn
                score_dict['HITNAME'] = hitter_name

                if before_score_gap == 0 and after_score_gap != 0:
                    score_dict['STATE_SPLIT'] = 'FIRST_GET_SCORE'
                elif before_score_gap != after_score_gap and row['HOW_ID'] != 'HR':
                    score_dict['STATE_SPLIT'] = 'GET_RBI_HIT'
                elif before_score_gap != after_score_gap and row['HOW_ID'] == 'HR':
                    score_dict['STATE_SPLIT'] = 'GET_HR_HIT'

                if 'STATE_SPLIT' in score_dict:
                    result_list.append(score_dict)
        # endregion 타자 시점

        # region 투수 시점
        if df_inning['run'].values[0] == 0:
            # 무실점 방어성공
            df_pitzone = record.Record().get_pitzone_df(game_id, year)
            df_pitzone = df_pitzone[(df_pitzone['tb'] == tb) & (df_pitzone['inning'] == prev_inning)]

            pitcher_count = df_pitzone.groupby(['PIT_P_ID']).count().shape[0]
            pitcher_name = record.Record().get_player_info(df_pitzone.iloc[0]['PIT_P_ID'])[0]['NAME']
            inning_ball_count = df_pitzone.shape[0]

            no_run_dict = data_dict.copy()
            no_run_dict['PITNAME'] = pitcher_name
            no_run_dict['BALL_COUNT'] = inning_ball_count
            # 투수 혼자 던진 공이 9개 이하 일 경우
            if pitcher_count == 1 and inning_ball_count <= 9:
                ball_count_dict = data_dict.copy()
                ball_count_dict['PITNAME'] = pitcher_name
                ball_count_dict['BALL_COUNT'] = inning_ball_count
                ball_count_dict['STATE_SPLIT'] = 'BALL_COUNT_UNDER_9'
                result_list.append(ball_count_dict)

            # 실점 위기
            if '3' in str(df_inning['AFTER_RUNNER_SC']):
                ball_count_dict = data_dict.copy()
                ball_count_dict['PITNAME'] = pitcher_name
                ball_count_dict['BALL_COUNT'] = inning_ball_count
                ball_count_dict['STATE_SPLIT'] = 'BALL_COUNT_UNDER_9'
                result_list.append(ball_count_dict)

            result_list.append(no_run_dict)
        else:
            # 실점
            pass
        # endregion 투수 시점
