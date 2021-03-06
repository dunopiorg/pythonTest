from enum import Enum
from korean import Noun, l10n
from lib import query_loader
from lib import record
from lib import connect_gsheet
from collections import defaultdict
import pymysql.cursors
import random
import re
import config


class HitterRecord(Enum):
    HITTER = 1
    SEASON = 2
    SEASON_RESULT = 3
    TOTAL = 4
    TOTAL_RESULT = 5
    VERSUS_PITCHER = 7
    VERSUS_TEAM = 8
    BASE = 9
    SCORE = 10


class MessageMaker(object):

    def __init__(self):
        self.personal_dict = {}
        self.season_dict = {}
        self.total_dict = {}
        self.today_dict = {}
        self.TEAM_KOR = record.Record().get_team_korean_names()
        self.SCORE_KR = {"0D": "동점", "1W": "1점차 이기고 있을 때", "1L": "1점차 지고 있을 때"
            , "WW": "이기고 있을 때", "LL": "지고 있을 때"}
        self.FLOAT_STATE = ['HRA', 'OBA', 'SLG']
        self.HITTER_STATE_KOR = {"HR": "홈런", "HIT": "안타", "H2": "2루타", "H3": "3루타", "BB": "볼넷", "SO": "삼진", "RBI": "타점"
            , "HRA": "타율", "OBA": "출루율", "SLG": "장타율", "AB": "타수", "PA": "타석"}
        self.PITCHER_STATE = {"NO_HIT": "노히트로런", "SHO": "완봉승", "CG_W": "완투승", "CG_L": "완투패", "WINS": "승", "LOSSES": "패", "QS": "퀄리티스타트",
                                  "HOLDS": "홀드", "SAVES": "세이브", "HIT": "피안타", "HR": "피홈런", "HP": "사구", "PB": "범타", "SO": "삼진", "BB": "볼넷"}
        self.PITCHER_STATE_KOR = {"NO_HIT": "노히트로런 {}번", "SHO": "완봉승 {}번", "CG_W": "완투승 {}번", "CG_L": "완투패 {}번", "WINS": "{}승",
                                  "LOSSES": "{}패", "QS": "퀄리티스타트 {}개", "HOLDS": "홀드 {}개", "SAVES": "세이브 {}개",
                                  "HIT": "피안타 {}개", "HR": "피홈런 {}개", "PB": "범타 {}개", "HP": "사구 {}개", "SO": "삼진 {}개", "BB": "볼넷 {}개"}
        self.PITCHER_STATE_ORDER = ["NO_HIT", "SHO", "CG_W", "CG_L", "WINS", "LOSSES", "QS", "HOLDS", "SAVES",
                                    "HIT", "HR", "HP", "PB", "SO", "BB"]
        self.df_template = connect_gsheet.Gspread().get_df_template()


    def set_player_info(self, personal_dict, today_record_list, total_record_list):
        self.personal_dict = personal_dict

        if today_record_list:
            for today in today_record_list:
                today_state = today['STATE']
                today_result = today['RESULT']
                self.today_dict[today_state] = today_result

        if total_record_list:
            for total in total_record_list:
                total_state = total['STATE']
                total_result = total['RESULT']
                self.total_dict[total_state] = total_result

    def get_pitcher_message(self, event, parameters):
        group_id = event
        sentence = []
        for param in parameters:
            state_split = param[2]
            param_dict = param[4]
            if param_dict['STATE'] not in self.FLOAT_STATE:
                param_dict['RESULT'] = int(param_dict['RESULT'])
            template_dict = MessageUnit.get_template_dict(group_id, 1)

            if state_split in template_dict:
                template = template_dict[state_split]

                if state_split == 'BASIC':
                    param_dict['LEAGUE'] = template_dict[param_dict['LEAGUE']]
                elif state_split == 'VERSUS_TEAM':
                    param_dict['HITTEAM'] = self.TEAM_KOR[param_dict['HITTEAM']]
                param_dict['STATE'] = self.PITCHER_STATE[param_dict['STATE']]
                text = template.format(**param_dict)

                if text:
                    sentence.append(text)
        return '\n'.join(sentence)

    def get_pitcher_starting_message(self, event, parameters):
        group_id = event
        versus_team_list = []
        sentence = []
        args_dict = {}
        record_dict = {}
        template_dict = MessageUnit.get_template_dict(group_id, 1)

        for param in parameters:
            state_split = param[2]
            param_dict = param[4]

            if state_split in template_dict:
                template = template_dict[state_split]

            if state_split == "VERSUS_TEAM":
                if "HITTEAM" not in args_dict and "HITTEAM" in param_dict:
                    args_dict['HITTEAM'] = self.TEAM_KOR[param_dict["HITTEAM"]]

                if "PITNAME" not in args_dict and "PITNAME" in param_dict:
                    args_dict['PITNAME'] = param_dict["PITNAME"]

                if "LEAGUE" not in args_dict and "LEAGUE" in param_dict:
                    common_dict = MessageUnit.get_template_dict('COMMON_EVENT')
                    args_dict['LEAGUE'] = common_dict['LEAGUE' + '_' + param_dict["LEAGUE"]]

                if "GAME_NUM" not in args_dict and "GAME_NUM" in param_dict and param_dict["GAME_NUM"] > 0:
                    args_dict['GAME_NUM'] = int(param_dict["GAME_NUM"])

                record_dict[param_dict["STATE"]] = param_dict["RESULT"]
            else:
                if 'STARTING_NUM' in param_dict:
                    param_dict['STARTING_NUM'] = int(param_dict['STARTING_NUM'])
                text = template.format(**param_dict)
                if text:
                    sentence.append(text)

        if len(record_dict) > 0:
            for key in list(self.PITCHER_STATE_ORDER):
                if key in record_dict:
                    if type(record_dict[key]) is float:
                        record_val = int(record_dict[key])
                    else:
                        record_val = record_dict[key]
                    text = self.PITCHER_STATE_KOR[key].format(record_val)
                    versus_team_list.append(text)

        if versus_team_list:
            args_dict["COMMENT"] = ",".join(versus_team_list)
            if state_split in template_dict:
                template = template_dict[state_split]
                if args_dict:
                    text = template.format(**args_dict)
                    if text:
                        sentence.append(text)

        return '\n'.join(sentence)

    def get_pitcher_on_mound_message(self, event, parameters):
        group_id = event
        versus_team_list = []
        sentence = []
        args_dict = {}
        record_dict = {}
        text = ''
        template_dict = MessageUnit.get_template_dict(group_id, 1)

        for param in parameters:
            state_split = param[2]
            param_dict = param[4]

            if state_split in template_dict:
                template = template_dict[state_split]

                if state_split == "VERSUS_TEAM":
                    if "HITTEAM" not in args_dict and "HITTEAM" in param_dict:
                        args_dict['HITTEAM'] = self.TEAM_KOR[param_dict["HITTEAM"]]

                    if "PITNAME" not in args_dict and "PITNAME" in param_dict:
                        args_dict['PITNAME'] = param_dict["PITNAME"]

                    if "LEAGUE" not in args_dict and "LEAGUE" in param_dict:
                        common_dict = MessageUnit.get_template_dict('COMMON_EVENT')
                        args_dict['LEAGUE'] = common_dict['LEAGUE' + '_' + param_dict["LEAGUE"]]

                    if "GAME_NUM" not in args_dict and "GAME_NUM" in param_dict and param_dict["GAME_NUM"] > 0:
                        args_dict['GAME_NUM'] = int(param_dict["GAME_NUM"])

                    record_dict[param_dict["STATE"]] = param_dict["RESULT"]
                else:
                    text = template.format(**param_dict)
        if text:
            sentence.append(text)

        if len(record_dict) > 0:
            for key in list(self.PITCHER_STATE_ORDER):
                if key in record_dict:
                    if type(record_dict[key]) is float:
                        record_val = int(record_dict[key])
                    else:
                        record_val = record_dict[key]
                    text = self.PITCHER_STATE_KOR[key].format(record_val)
                    versus_team_list.append(text)

        if versus_team_list:
            args_dict["COMMENT"] = ",".join(versus_team_list)
            if state_split in template_dict:
                template = template_dict[state_split]
                if args_dict:
                    text = template.format(**args_dict)
                    if text:
                        sentence.append(text)

        return '\n'.join(sentence)

    def get_hit_event_message_new(self, event, parameters):
        group_id = event
        selected_param_list = []
        usable_list = []
        sentence = ''
        state_split_list = ["UNIT10", "UNIT100", "NGAME", "NPA", "RANK_UP"]
        score_split_dict = {"0D": "동점인 상황", "1W": "1점차로 이기고 있는 상황", "1L": "1점차로 지고 있는 상황",
                            "WW": "이기고 있는 상황", "LL": "지고 있는 상황"}
        base_split_dict = {"ONB": "주자가 나가 있는 상황", "NOB": "주자가 없는 상황", "SCORE_B": "득점권 상황"}
        # for param in parameters:
        #     param_data = param[4]
        #     # rank = param_data['RANK']
        #     s_split = param_data['STATE_SPLIT']
        #     if s_split in state_split_list or param[0] > 50:
        #         selected_param_list.append(param)

        for param in parameters:
            param_dict = param[4]
            state_split = param_dict['STATE_SPLIT']
            state = param_dict['STATE']
            league_data = param_dict['LEAGUE']
            state_result = param_dict['RESULT']
            rate_score = param_dict['RATE_SCORE']
            hitname = param_dict['HITNAME']

            # region Ngame, Npa, Unit10, Unit100, Rank up
            if state_split == "BASIC":
                usable_list.append({league_data: {'league_data': league_data}})
                if state in self.FLOAT_STATE:
                    state_word = "{0} {1} 기록합니다. ".format(state_result, self.HITTER_STATE_KOR[state])
                else:
                    state_word = "{0} {1}개 기록합니다. ".format(self.HITTER_STATE_KOR[state], int(state_result))
                usable_list.append({'STATE': {'state': state_word}})
            elif state_split == "NGAME" or state_split == "NPA":
                usable_list.append({state_split: {'result': int(state_result), 'state': self.HITTER_STATE_KOR[state]}})
            elif state_split == "UNIT10" or state_split == "UNIT100":
                usable_list.append({'HITNAME': {'hitname': hitname}})
                usable_list.append({league_data: {'league_data': league_data}})
                usable_list.append({state_split: {'result': int(state_result), 'state': self.HITTER_STATE_KOR[state]}})
            elif state_split == "RANK_UP":
                usable_list.append({league_data: {'league_data': league_data}})
                usable_list.append({state_split: {'result': int(state_result), 'state': self.HITTER_STATE_KOR[state]},
                                    'pre_result': param_dict['PREV_RANK']})
            elif state_split == "1UNIT":
                usable_list.append({'HITNAME': {'hitname': hitname}})
                usable_list.append({league_data: {'league_data': league_data}})
                usable_list.append({state_split: {'result': int(state_result), 'state': self.HITTER_STATE_KOR[state]}})
            # endregion
            # region Versus Pitcher and Team
            elif state_split == "VERSUS_PITCHER" or state_split == "VERSUS_TEAM":
                pos_neg = param_dict['POS_NEG']
                if state_split == "VERSUS_PITCHER":
                    usable_list.append({state_split: {'pitname': param_dict['PITNAME']}})
                else:
                    usable_list.append({state_split: {'pitteam': param_dict['PITTEAM']}})

                if pos_neg == "POS":
                    record_good_bad = '높은'
                    usable_list.append({'STYLE_POS': {'state': self.HITTER_STATE_KOR[state]}})
                else:
                    record_good_bad = '낮은'
                    usable_list.append({'STYLE_NEG': {'state': self.HITTER_STATE_KOR[state]}})

                # usable_list.append({league_data: {'league_data': league_data}})
                state_word = "{0} {1}번째 ".format(self.HITTER_STATE_KOR[state], int(state_result))
                # usable_list.append({'STATE': {'state': state_word}})

                if league_data == "ALL":
                    usable_list.append({'COMPARE_ALL': {'percent': rate_score,
                                                        'result': state_word, 'state': self.HITTER_STATE_KOR[state]}})
                else:
                    usable_list.append({'COMPARE_SEASON': {'percent': rate_score,
                                                           'result': state_word, 'state': self.HITTER_STATE_KOR[state]}})
            # endregion
            # region 점수차, 주자상황 Split
            elif state_split in score_split_dict or state_split in base_split_dict:
                pos_neg = param_dict['POS_NEG']
                usable_list.append({state_split: {'dummy': 'dummy'}})
                if pos_neg == "POS":
                    record_good_bad = '높은'
                    usable_list.append({'GOOD_RECORD': {'state': self.HITTER_STATE_KOR[state]}})
                else:
                    record_good_bad = '낮은'
                    usable_list.append({'BAD_RECORD': {'state': self.HITTER_STATE_KOR[state]}})
                if state in self.FLOAT_STATE:
                    state_word = "{state} {rate:로} ".format(state=self.HITTER_STATE_KOR[state], rate=Noun(str(state_result)))
                else:
                    state_word = "{0} {1}개로 ".format(self.HITTER_STATE_KOR[state], int(state_result))
                usable_list.append({'STATE': {'state': state_word}})

                if league_data == "ALL":
                    usable_list.append({'COMPARE_ALL': {'percent': rate_score, 'result': record_good_bad,
                                                        'state': '{state:을}'.format(state=Noun(self.HITTER_STATE_KOR[state]))}})
                else:
                    usable_list.append({'COMPARE_SEASON': {'percent': rate_score, 'result': record_good_bad,
                                                           'state': '{state:을}'.format(state=Noun(self.HITTER_STATE_KOR[state]))}})
            # endregion

            if usable_list:
                sentence += re.sub("\s\s+", " ", self.get_template_sentence(group_id, usable_list))
                sentence += '\n'
                usable_list = []
        return sentence

    def get_hit_event_message(self, parameters):
        usable_param_dict = {}
        group_id = ''
        positive_count = 0
        for param in parameters:
            group_id = param[1]
            data_dict = param[4]
            hitter_name = data_dict['HITNAME']
            league = data_dict['LEAGUE']
            state = data_dict['STATE']
            split = data_dict['STATE_SPLIT']
            if state in self.FLOAT_STATE:
                state_result = data_dict['RESULT']
            else:
                state_result = int(data_dict['RESULT'])
            pa = data_dict['PA']
            rate_score = data_dict['RATE_SCORE']
            pos_neg = data_dict['POS_NEG']

            key_param = state + '_' + split + '_' + league
            usable_param_dict[key_param] = state_result

            pa_param = key_param + '_' + 'PA'
            usable_param_dict[pa_param] = pa

            rate_score_param = key_param + '_' + 'RATE_SCORE'
            if pos_neg == "POS":
                usable_param_dict[rate_score_param] = "{}% 높은".format(int(rate_score))
            else:
                usable_param_dict[rate_score_param] = "{}% 낮은".format(int(rate_score))

            if 'HITNAME' not in usable_param_dict:
                usable_param_dict['HITNAME'] = hitter_name
            if 'LEAGUE' not in usable_param_dict:
                if league == "TODAY":
                    usable_param_dict['LEAGUE'] = "오늘 경기"
                elif league == "SEASON":
                    usable_param_dict['LEAGUE'] = "이번 시즌"
                elif league == "ALL":
                    usable_param_dict['LEAGUE'] = "통산"

            # SPLIT 상황 설명
            if split == "VERSUS_TEAM":
                usable_param_dict['TEAM'] = MessageMaker.get_post(self.TEAM_KOR[data_dict['PITTEAM']], '을/를')
            elif split == "VERSUS_PITCHER":
                usable_param_dict['PITCHER'] = data_dict['PITNAME']
            elif split in self.SCORE_KR:
                usable_param_dict[split] = self.SCORE_KR[split]

            if pos_neg == "POS":
                positive_count += 1
            else:
                positive_count -= 1

        if positive_count == len(parameters):
            usable_param_dict['POS_NEG'] = "굉장히 좋습니다."
        elif positive_count >= 0:
            usable_param_dict['POS_NEG'] = "좋은데요"
        else:
            usable_param_dict['POS_NEG'] = "좋지 않은데요"

        sentence = self.get_sentence(group_id, usable_param_dict)

        if sentence:
            sentence = '[HIT_EVENT]' + sentence
            return sentence
        else:
            return None

    def get_hitter_split_message(self, event, parameters):
        group_id = event
        positive_count = 0
        league_list = ['SEASON', 'ALL']
        sentence = ''
        hitter = None
        for league in league_list:
            usable_list = []
            state_list = []
            state_name_list = []
            state_pos_list = []
            state_neg_list = []
            split = ''
            split_data = ''
            pos_neg = ''
            hra = 0
            rate_score = 0
            state_result = None
            for param in parameters:
                data_dict = param[4]
                if league == data_dict['LEAGUE']:
                    hitter = data_dict['HITTER']
                    split = data_dict['STATE_SPLIT']
                    pos_neg = data_dict['POS_NEG']
                    if split == "VERSUS_PITCHER":
                        split_data = data_dict['PITNAME']
                    elif split == "VERSUS_TEAM":
                        split_data = data_dict['PITTEAM']

                    state = data_dict['STATE']
                    pa = data_dict['PA']
                    if state in self.FLOAT_STATE:
                        state_result = str(data_dict['RESULT'])
                        if state_result:
                            state_list.append('{0} {1}'.format(self.HITTER_STATE_KOR[state], state_result))
                            if pos_neg == "POS":
                                state_pos_list.append(state)
                            else:
                                state_neg_list.append(state)
                    else:
                        if len(state_list) == 0:
                            state_list.append("{0}타석".format(pa))

                        state_result = int(data_dict['RESULT'])
                        if state_result == 0 and state == "HIT":
                            state_list.append('무{0}'.format(self.HITTER_STATE_KOR[state]))
                        elif state == "RBI":
                            if pos_neg == "POS":
                                state_pos_list.append(state)
                            else:
                                state_neg_list.append(state)
                            state_list.append('{0} {1}'.format(state_result, self.HITTER_STATE_KOR[state]))
                        elif state_result > 0:
                            if pos_neg == "POS":
                                state_pos_list.append(state)
                            else:
                                state_neg_list.append(state)
                            state_list.append('{0} {1}개'.format(self.HITTER_STATE_KOR[state], state_result))

                        if state == "HIT" and hra == 0:
                            hra = round(state_result/pa, 3)

                    rate_score = data_dict['RATE_SCORE']

            state_count = len(state_list)
            if state_count > 0:
                # region Split이 1UNIT 일 경우
                if split == '1UNIT':
                    usable_list.append({league: {'LEAGUE': league}})
                    usable_list.append({split: {'RESULT': state_result}})
                # endregion
                # region Split이 NPA, NGAME
                if split == 'NPA' or split == 'NGAME':
                    usable_list.append({league: {'league': league}})
                    usable_list.append({split: {'result': state_result, 'state': self.HITTER_STATE_KOR[state]}})
                # endregion
                else:
                    #  usable_list.append({'HITNAME': {'hitname': hitname}})
                    usable_list.append({league: {'league': league}})

                    if split == "VERSUS_PITCHER":
                        usable_list.append({split: {'pitname': split_data}})
                    elif split == "VERSUS_TEAM":
                        usable_list.append({split: {'pitteam': self.TEAM_KOR[split_data]}})
                    else:
                        usable_list.append({split: {split: split}})

                    if state_count > 1:
                        if state_pos_list:
                            state_pos_name = ', '.join([self.HITTER_STATE_KOR[x] for x in state_pos_list])
                        if state_neg_list:
                            state_neg_name = ', '.join([self.HITTER_STATE_KOR[x] for x in state_neg_list])

                        if state_pos_list and state_neg_list:
                            usable_list.append({'STYLE_POS_BUT': {'state': state_pos_name}})
                            usable_list.append({'STYLE_NEG': {'state': state_neg_name}})
                        elif state_pos_list:
                            usable_list.append({'STYLE_POS': {'state': state_pos_name}})
                        else:
                            usable_list.append({'STYLE_NEG': {'state': state_neg_name}})

                    if hra > 0:
                        state_name_list.append('HRA')
                        state_list.append('{0} {1}'.format(self.HITTER_STATE_KOR['HRA'], state_result))
                    state_val = ', '.join([x for x in state_list])
                    usable_list.append({'STATE': {'state': state_val}})

                    if state_count < 3:
                        if pos_neg == "POS":
                            if rate_score < 200:
                                pos = "좋은"
                            else:
                                pos = "상당히 좋은"
                        else:
                            if rate_score < 200:
                                pos = "낮은"
                            else:
                                pos = "상당히 낮은"

                        if league == "ALL":
                            usable_list.append({'COMPARE_ALL': {'percent': rate_score, 'result': pos,
                                                                'state': self.HITTER_STATE_KOR[state]}})
                        else:
                            usable_list.append({'COMPARE_SEASON': {'percent': rate_score, 'result': pos,
                                                                   'state': self.HITTER_STATE_KOR[state]}})
                    else:
                        usable_list.append({'STATE_FINISH': {'state_finish': 'dummy'}})

            if usable_list:
                sentence += re.sub("\s\s+", " ", self.get_template_sentence(group_id, usable_list))
                sentence += '\n'

        if sentence:
            return sentence
        else:
            return None

    def get_hitter_split_message_v2(self, event, parameters):
        group_id = event
        sentence = []
        hit_list = ['HIT', 'HR', 'H1', 'H2', 'H3']

        for param in parameters:
            state_split = param[2]
            param_dict = param[4]
            text = ''
            template_dict = MessageUnit.get_template_dict(group_id, 1)
            state = param_dict['STATE']

            if param_dict['STATE'] in hit_list:
                state = 'HIT'
            msg_code = state_split + '_' + param_dict['LEAGUE'] + '_' + state + '_' + param_dict['POS_NEG']

            if param_dict['RATE_SCORE'] > 200:
                msg_code += '_PLUS'

            if msg_code in template_dict:
                template = template_dict[msg_code]

                if state_split == 'VERSUS_TEAM':
                    param_dict['TEAM'] = self.TEAM_KOR[param_dict['PITTEAM']]
                elif state_split == 'VERSUS_PITCHER':
                    param_dict['PITCHER'] = param_dict['PITNAME']

                if state in self.FLOAT_STATE:
                    param_dict['RESULT'] = "{rate:로} ".format(rate=Noun(str(param_dict['RESULT'])))
                else:
                    param_dict['RESULT'] = int(param_dict['RESULT'])

                param_dict['STATE'] = self.HITTER_STATE_KOR[param_dict['STATE']]

            try:
                text = template.format(**param_dict)
            except Exception as ex:
                print(ex)

            if text:
                sentence.append(text)

        return '\n'.join(sentence)

    def get_message_version_v0(self, event, parameters):
        group_id = event
        sentence = []
        one_sentence = None

        for param in parameters:
            state_split = param[2]
            param_dict = param[4]
            text = ''
            # template_dict = MessageUnit.get_template_dict(group_id, config.VERSION_LEVEL)
            # state = param_dict['STATE']
            query_string = "group_id == '%s' and state_split == '%s' and version_level == %s" % (group_id, state_split, config.VERSION_LEVEL)

            if not self.df_template.query(query_string).empty:
                temp_list = self.df_template.query(query_string).template.values[0].split('#')
                template = random.choice(temp_list)
            else:
                continue

            # if state_split in template_dict:
            #     template = template_dict[state_split]

            try:
                # text = template.format(**param_dict)
                text = l10n.Template(template).format(**param_dict)
            except Exception as ex:
                print(ex)

            if text:
                sentence.append(text)

        if config.VERSION_LEVEL == 0 and sentence:
            one_sentence = MessageUnit.get_make_one_sentence(sentence)

        if one_sentence:
            return one_sentence
        else:
            return '\n'.join(sentence)

    def get_today_event_message(self, event, parameters):
        group_id = event
        state_dict = {}
        usable_list = []
        hitter_name = ''
        league = ''
        sentence = ''
        state_result = ''
        state_name_list = ['PA', 'AB', 'HIT', 'HR', 'SO', 'HRA']
        event_split = parameters[0][3].split('_')[-1]
        for param in parameters:
            state_split = param[2]
            data_dict = param[4]
            hitter_name = data_dict['HITNAME']
            league = data_dict['LEAGUE']
            state = data_dict['STATE']
            pa = data_dict['PA']
            state_result = data_dict['RESULT']

            # region TODAY SPLIT
            if event_split == "TODAY":
                if 'PA' not in state_dict:
                    state_dict['PA'] = "{0} {1}".format(pa, self.HITTER_STATE_KOR['PA'])
                if state in self.FLOAT_STATE:
                    if state_result:
                        state_dict[state] = "이번 시즌 타율" + str(state_result)
                else:
                    state_val = int(state_result)
                    if state_val == 0 and state == "HIT":
                        state_dict[state] = '무안타'
                    elif state_val > 0:
                        state_dict[state] = "{0} {1}".format(state_val, self.HITTER_STATE_KOR[state])
            # endregion TODAY SPLIT
            # region FIRST SPLIT
            elif event_split == "FIRST":
                if state in self.FLOAT_STATE:
                    state_result = str(data_dict['RESULT'])
                    state_dict[state] = state_result
            elif event_split == "RANKER":
                state_dict = data_dict
                state_dict['STATE'] = self.HITTER_STATE_KOR[state]
                if state not in self.FLOAT_STATE:
                    state_dict['RESULT'] = int(state_dict['RESULT'])
                template_dict = MessageUnit.get_template_dict(group_id, 1)
                state_dict['LEAGUE'] = template_dict['LEAGUE' + '_' + state_dict['LEAGUE']]
            elif event_split == "1UNIT":
                state_dict = data_dict
                # state_dict['STATE'] = "{state:을}".format(state=Noun(self.HITTER_STATE_KOR[state]))
                state_dict['STATE'] = Noun(self.HITTER_STATE_KOR[state])
                template_dict = MessageUnit.get_template_dict(group_id, 1)
                state_dict['LEAGUE'] = template_dict['LEAGUE' + '_' + state_dict['LEAGUE']]
            # endregion FIRST SPLIT

        state_count = len(state_dict)
        if state_count > 0:
            if event_split == "FIRST":
                # usable_list.append({'HITNAME': {'hitname': hitter_name}})
                usable_list.append({'TODAY': {'league': league}})
                usable_list.append({'FIRST': {'HRA': state_result}})
            elif event_split == "TODAY":
                # usable_list.append({'HITNAME': {'hitname': hitter_name}})
                usable_list.append({'TODAY': {'league': league}})
                state_list = []
                for state_name in state_name_list:
                    if state_name in state_dict:
                        state_list.append(state_dict[state_name])
                usable_list.append({'STATE': {'state': ','.join(state_list)}})
            elif event_split == "RANKER":
                template_dict = MessageUnit.get_template_dict(group_id, 1)
                if state_split in template_dict:
                    template = template_dict[state_split]
                    text = template.format(**state_dict)
                    if text:
                        return text
            elif event_split == "1UNIT":
                template_dict = MessageUnit.get_template_dict(group_id, 1)
                if state_split in template_dict:
                    template = template_dict[state_split]
                    text = template.format(**state_dict)
                    if text:
                        return text
            sentence = self.get_template_sentence(group_id, usable_list)

        if sentence:
            return sentence
        else:
            return None

    def get_today_basic_event_message(self, event, parameters):
        group_id = event
        state_dict = {}
        usable_list = []
        hitter_name = ''
        sentence = ''
        state_list = []
        state_text_dict = {}
        state_sort_list = ['HRA', 'OBA', 'SLG', 'HIT', 'HR', 'RBI', 'KK', 'H2', 'H3', 'BB']  #, 'SO'
        state_text = ''
        hitter = None
        for param in parameters:
            data_dict = param[4]
            league = data_dict['LEAGUE']
            hitter_name = data_dict['HITNAME']
            hitter = data_dict['HITTER']
            state = data_dict['STATE']
            pa = data_dict['PA']
            state_result = data_dict['RESULT']

            if 'PA' not in state_dict:
                state_dict['PA'] = pa

            rank = data_dict['RANK']
            if state in state_sort_list:
                if state in self.FLOAT_STATE:
                    if state_result:
                        state_text = "{0} {1}".format( self.HITTER_STATE_KOR[state], state_result)
                        state_text_dict[state_sort_list.index(state)] = state_text
                else:
                    state_val = int(state_result)
                    state_text = "{0} {1}개".format(self.HITTER_STATE_KOR[state], state_val)
                    state_text_dict[state_sort_list.index(state)] = state_text

        state_count = len(state_dict)
        if state_count > 0:
            # usable_list.append({'HITNAME': {'hitname': hitter_name}})
            usable_list.append({'LEAGUE_' + league: {'league': league}})
            usable_list.append({'BASIC': {'state': ' '.join(state_text_dict.values())}})
            usable_list.append({'BASIC_FINISH': {'league': league}})

        if usable_list:
            sentence += re.sub("\s\s+", " ", self.get_template_sentence(group_id, usable_list))

        if sentence:
            return sentence
        else:
            return None

    def get_common_message(self, event, parameters):
        group_id = event
        sentence = []
        for param in parameters:
            state_split = param[2]
            param_dict = param[4]
            text = ''
            # template_dict = MessageUnit.get_template_dict(group_id, 1)

            query_string = "group_id == '%s' and state_split == '%s' and version_level == %s" % (group_id, state_split, config.VERSION_LEVEL)

            if not self.df_template.query(query_string).empty:
                temp_list = self.df_template.query(query_string).template.values[0].split('#')
                template = random.choice(temp_list)

                if state_split == "GAMEINFO":
                    hteam = MessageMaker.get_post(self.TEAM_KOR[param_dict['HTEAM']], '와/과')
                    vteam = self.TEAM_KOR[param_dict['VTEAM']]
                    text = template.format(stadium=param_dict['STADIUM'], hteam=hteam, vteam=vteam,
                                           chajun=param_dict['CHAJUN'], umpc=param_dict['UMPC'],
                                           ump1=param_dict['UMP1'],
                                           temp=param_dict['TEMP'],
                                           ump2=param_dict['UMP2'], ump3=param_dict['UMP3'],
                                           mois=param_dict['MOIS'])
                else:
                    try:
                        # text = template.format(**param_dict)
                        text = l10n.Template(template).format(**param_dict)
                    except Exception as ex:
                        print(ex)
                if text:
                    sentence.append(text)
            else:
                continue
            # if state_split in template_dict:
            #     template = template_dict[state_split]
            #
            #     if state_split == "GAMEINFO":
            #         hteam = MessageMaker.get_post(self.TEAM_KOR[param_dict['HTEAM']], '와/과')
            #         vteam = self.TEAM_KOR[param_dict['VTEAM']]
            #         text = template.format(stadium=param_dict['STADIUM'], hteam=hteam, vteam=vteam,
            #                                chajun=param_dict['CHAJUN'], umpc=param_dict['UMPC'], ump1=param_dict['UMP1'],
            #                                temp=param_dict['TEMP'],
            #                                ump2=param_dict['UMP2'], ump3=param_dict['UMP3'], mois=param_dict['MOIS'])
            #     else:
            #
            #         try:
            #             # text = template.format(**param_dict)
            #             text = l10n.Template(template).format(**param_dict)
            #         except Exception as ex:
            #             print(ex)
            #
            #     if text:
            #         sentence.append(text)
        return '\n'.join(sentence)

    def get_sentence(self, group_id, sentence_dict):
        node_list = MessageUnit.get_node_list(group_id)
        sentence = ''
        sentence_end_flag = False
        for node in node_list:
            if node.key in sentence_dict:

                param_text = sentence_dict[node.key]
                sentence += node.msg.format(param_text)
                sentence += ' '
                if node.complete_flag is True:
                    sentence_end_flag = node.complete_flag

        if sentence_end_flag and sentence:
            return sentence
        else:
            return None

    def get_template_sentence(self, group_id, param_list):
        template_dict = MessageUnit.get_template_dict(group_id, 1)

        sentence = ''
        try:
            for param in param_list:
                param_k = list(param.keys())[0]
                if param_k in template_dict:
                    template = template_dict[param_k]
                    data = param.get(param_k)
                    if type(data) is list:
                        for i, d in enumerate(data):
                            sentence += template.format(**d)
                            if i != len(data) - 1:
                                sentence += ' '
                    else:
                        sentence += template.format(**data)
                        sentence += ' '
        except Exception as ex:
            print(ex)
        return sentence

    # region 자연어 처리 function
    @classmethod
    def get_post(cls, word, post):
        """
        단어에 맞는 조사 선택
        :param word:
        :param post:  '을/를', '와/과', '이/가', '은/는'
        :return:
        """

        result_word = ''
        post_list = [p for p in post.split('/') if p != '/']

        if cls.is_korean(word):
            result_word = l10n.proofread(word+"{0}({1})".format(post_list[0], post_list[1]))
        else:
            last_word = word[len(word) - 1:]

            if post_list == ['을', '를']:
                if last_word in ['M', 'N']:
                    result_word = word + '을'
                else:
                    result_word = word + '를'
            else:
                if last_word in ['L', 'R', 'M', 'N']:
                    for p in post_list:
                        if p in ['은', '과', '이']:
                            result_word = word + p
                            break
                else:
                    for p in post_list:
                        if p in ['는', '와', '가']:
                            result_word = word + p
                            break
        return result_word

    @classmethod
    def is_korean(cls, word):
        """
        단어가 한글인지 아닌지 판단
        :param word:
        :return:
        """
        for c in range(len(word)):
            if word[c] < u"\uac00" or word[c] > u"\ud7a3":
                return False
        return True

    def get_halpunli(self, float_record):
        hal_pun_li = ''
        state_result_integer = int(float_record * 1000)
        hal_integer = int(state_result_integer / 100)
        pun_integer = int((state_result_integer % 100) / 10)
        li_integer = int(state_result_integer % 10)
        if hal_integer > 0:
            hal_pun_li = str(hal_integer) + "할"
        if pun_integer > 0:
            hal_pun_li += str(pun_integer) + "푼"
        if li_integer > 0:
            hal_pun_li += str(li_integer) + "리"

        return hal_pun_li
    # endregion 자연어 처리 function


class Node(object):
    def __init__(self, message_unit):
        self.msg = ''
        self.key = ''
        self.group = ''
        self.complete_flag = False
        self.prev_node = None
        self.next_node = None
        self.set_values(message_unit)

    def set_values(self, unit_dict):
        # self.prev_id = [int(v) for v in unit_dict['prev_node'].split(',')]
        # self.current_id = [int(v) for v in unit_dict['curr_node'].split(',')]
        # self.next_id = [int(v) for v in unit_dict['next_node'].split(',')]
        msg_list = unit_dict['message_string'].split('#')
        self.msg = random.choice(msg_list)
        self.group = unit_dict['group_id']
        self.key = unit_dict['parameter_key']
        if unit_dict['complete_flag'] == 1:
            self.complete_flag = True


class MessageUnit(object):
    _HOST = config.DB_HOST
    _USER = config.DB_USER
    _PASSWORD = config.DB_PASSWORD
    _DB = config.DB_NAME
    _PORT = config.DB_PORT
    ql = query_loader.QueryLoader()

    @classmethod
    def get_unit(cls, group_id):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_message", "get_unit")
        query = query_format.format(group_id)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        return result

    @classmethod
    def get_template(cls, group_id, version_level=None):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        if version_level is None:
            version_level = 0

        query_format = cls.ql.get_query("query_message", "get_template")
        query = query_format.format(group_id, version_level)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        return result

    @classmethod
    def get_node_list(cls, group_id):
        units = cls.get_unit(group_id)
        unit_list = []
        for unit in units:
            node = Node(unit)
            unit_list.append(node)

        return unit_list

    @classmethod
    def get_template_dict(cls, group_id, version_level=None):
        templates = cls.get_template(group_id, version_level)
        template_dict = {}
        for temp in templates:
            temp_list = temp['template'].split('#')
            template_dict[temp['state_split']] = random.choice(temp_list)

        return template_dict

    @classmethod
    def get_make_one_sentence(cls, data_list):
        tree = lambda: defaultdict(tree)
        data = tree()

        for s in data_list:
            cls.adder(data, s.split('|'))

        t = cls.get_msg(data)
        t = l10n.proofread(t)
        return t

    @classmethod
    def adder(cls, data_dict, source_list):
        for source in source_list:
            data_dict = data_dict[source]

    @classmethod
    def get_msg(cls, d):
        temp_list = []
        join_flag = False
        for k, v in d.items():
            if len(v) == 0:
                temp_list.append(k)
                join_flag = True
            else:
                temp_list.append(k.format(cls.get_msg(v)))
                join_flag = False
        if join_flag:
            temp = ', '.join(temp_list)
        else:
            if temp_list[-1][-1] == ',':
                temp_list[-1] = temp_list[-1][:-1]
            temp = ' '.join(temp_list)
        return temp


# if __name__ == "__main__":
#     templates = MessageUnit.get_template("HITTER_SPLIT")
#     template_dict = {}
#     for temp in templates:
#         temp_list = temp['template'].split('#')
#         template_dict[temp['category']] = random.choice(temp_list)
#     print(template_dict)
