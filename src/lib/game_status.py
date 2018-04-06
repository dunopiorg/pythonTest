from lib import record
import re


class GameStatus(object):

    def __init__(self, game_key):
        self.TEAM_KOR = {"WO": "넥센", "SS": "삼성", "SK": "SK", "OB": "두산",
                         "NC": "NC", "LT": "롯데", "LG": "LG", "KT ": "kt", "HT": "기아", "HH": "한화"}
        self.game_key = game_key
        self.game_score = None
        self.gamecontapp_serno = 0
        self.last_how_seq_no = 0
        self.tscore = 0
        self.bscore = 0
        self.inning = 1
        self.base_player = []

        self.team_info = {}
        self.stadium_info_dict = {}
        self.starting_line_up = {}
        self.whole_selection_player = {}
        self.initialize_game_info(game_key)

    def initialize_game_info(self, game_key):
        self.set_starting_line_up(game_key)
        self.set_stadium_info(game_key)
        self.set_team_info_record(game_key)

    def set_stadium_info(self, game_key):
        stadium_info_list = record.Record().get_gameinfo_data(game_key)
        if stadium_info_list:
            stadium_info = stadium_info_list[0]
            self.stadium_info_dict = stadium_info

    def set_starting_line_up(self, game_key):
        line_up = record.Record().get_starting_line_up(game_key)

        if line_up:
            self.starting_line_up['T'] = [x for x in line_up if int(x['turn']) < 20 and x['posi'][0] == '1' and x['tb'] == 'T']
            self.starting_line_up['B'] = [x for x in line_up if int(x['turn']) < 20 and x['posi'][0] == '1' and x['tb'] == 'B']
            self.whole_selection_player['T'] = [x for x in line_up if x['tb'] == 'T']
            self.whole_selection_player['B'] = [x for x in line_up if x['tb'] == 'B']

    def is_starting_pitcher(self, tb, player_code):
        line_up = self.starting_line_up['T' if tb == 'B' else 'B']
        for line in line_up:
            if line['pcode'] == player_code:
                return True
        return False

    def get_live_text_info(self, live_data):
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

        hitter = live_data['batter']
        pitcher = live_data['pitcher']
        out_count = live_data['out']
        full_count = [live_data['ball'], live_data['strike'], live_data['out']]
        bat_order = live_data['batorder']
        ball_count = live_data['ballcount']
        text_style = live_data['textStyle']
        ball_type = live_data['ball_type']
        home_score = live_data['H_Run']
        away_score = live_data['A_Run']
        seq_no = live_data['seqNO']
        how = live_data['HOW']
        inning = live_data['inning']
        year = live_data['GYEAR']
        tb = 'T' if live_data['bTop'] == 1 else 'B'

        if bat_order > 0:
            hitname = record.Record().get_player_info(hitter)[0]['NAME']
            pitname = record.Record().get_player_info(pitcher)[0]['NAME']
            # hitname = [player['name'] for player in self.whole_selection_player['T' if live_data['bTop'] == 1 else 'B'] if player['pcode'] == hitter][0]
            # pitname = [player['name'] for player in self.whole_selection_player['B' if live_data['bTop'] == 1 else 'T'] if player['pcode'] == pitcher][0]
        else:
            pitname = ''
            hitname = ''

        result_dict = {'hitter': hitter, 'hitteam': hit_team, 'pitcher': pitcher, 'pitteam': pit_team,
                       'score': score, 'base': base, 'game_id': game_id, 'out_count': out_count,
                       'full_count': full_count, 'base_detail': base_detail, 'score_detail': score_detail,
                       'batorder': bat_order, 'ballcount': ball_count, 'textStyle': text_style,
                       'pitname': pitname, 'hitname': hitname, 'home_score': home_score,
                       'away_score': away_score, 'tb': tb, 'seq_no': seq_no, 'how': how,
                       'inning': inning, 'ball_type': ball_type, 'gyear':year}
        return result_dict

    def set_gamecontapp_info(self, hitter, pitcher, inn, how):
        gamecontapp_data = record.Record().get_gamecontapp(self.game_key, hitter, pitcher, inn, how)

        if gamecontapp_data and self.gamecontapp_serno != gamecontapp_data[0]['serno']:
            # region 주루 상황 관련
            gamecontapp = gamecontapp_data[0]
            self.gamecontapp_serno = gamecontapp['serno']
            tb = gamecontapp['tb']
            base1 = int(gamecontapp['base1a']) if len(gamecontapp['base1a']) > 0 else 0
            base2 = int(gamecontapp['base2a']) if len(gamecontapp['base2a']) > 0 else 0
            base3 = int(gamecontapp['base3a']) if len(gamecontapp['base3a']) > 0 else 0
            base_state = [base1, base2, base3]
            self.base_player = ['', '', '']

            for i, b in enumerate(base_state):
                if b > 0:
                    for player in self.whole_selection_player[tb]:
                        if b == player['turn']:
                            self.base_player.append(player['name'])
                else:
                    self.base_player.append('')
            # endregion

            # region 점수 상황 관련
            self.tscore = gamecontapp['tscore']
            self.bscore = gamecontapp['bscore']
            # endregion

    def get_explain_how_event(self, hitter, pitcher, inn, how):
        result_list = []
        data_dict = {'LEAGUE': 'SEASON', 'STATE': 'CURRENT_INFO'}
        defender_dict = {'1': "투수", '2': "포수", '3': "1루수", '4': "2루수", '5': "3루수", '6': "유격수", '7': "좌익수",
                         '8': "중견수", '9': "우익수", '78': "좌중간", '89': "우중간", '67': "좌전", '77': "좌전", '88': "중전", '99': "우전"}
        base_dict = {'A': '1루', 'B': '2루', 'C': '3루'}
        out_count = ['0', '1', '2', '3']
        how_kor = {"HR": "홈런", "GR": "땅볼", "FL": "플라이", "ER": "실책", "H1": "1루타", "H2": "2루타", "H3": "3루타"}
        basic_how_list = ["H1", "H2", "H3", "HR"]

        gamecontapp_data = record.Record().get_gamecontapp(self.game_key, hitter, pitcher, inn, how)
        if not gamecontapp_data:
            return None

        gamecontapp = gamecontapp_data[0]
        if self.last_how_seq_no != gamecontapp['serno']:
            self.last_how_seq_no = gamecontapp['serno']

            how = gamecontapp['how']
            place = gamecontapp['place']
            runner = gamecontapp['rturn']
            field_list = list(filter(None, re.split('(\d+)', gamecontapp['field'])))

            how_event = data_dict.copy()

            if how == "FL":
                field = field_list[0]
                how_event['POS'] = defender_dict[field]
                if field_list[1] == 'E':
                    how_event['STATE_SPLIT'] = 'HOW_FL_ER'
                else:
                    how_event['STATE_SPLIT'] = 'HOW_FL'

                if place in base_dict:
                    how_event['BASE'] = base_dict[place]

            elif how == "BB":
                how_event['STATE_SPLIT'] = 'HOW_BB'
                if len(gamecontapp['base1a']) > 0 and len(gamecontapp['base2a']) > 0 and len(gamecontapp['base3a']) > 0:
                    how_event['BASE'] = '만'
                elif len(gamecontapp['base1a']) > 0 and len(gamecontapp['base2a']) > 0:
                    how_event['BASE'] = '1, 2'
                else:
                    how_event['BASE'] = '1'

            elif how == "KK":
                how_event['STATE_SPLIT'] = 'HOW_KK'
            elif how == "GR":
                field = field_list[0]
                how_event['POS'] = defender_dict[field]
                if place in out_count:
                    how_event['STATE_SPLIT'] = 'HOW_GR'
                else:
                    how_event['STATE_SPLIT'] = 'HOW_GR_ER'

                if place in base_dict:
                    how_event['BASE'] = base_dict[place]

            elif how in basic_how_list:
                how_event['STATE_SPLIT'] = 'HOW_HIT'
                how_event['POS'] = defender_dict[field_list[1]]
                how_event['HIT'] = how_kor[how]

            if "STATE_SPLIT" in how_event:
                result_list.append(how_event)
                return result_list
            else:
                return None

    def set_team_info_record(self, game_key):
        game_date = game_key[:4]
        tteam = self.TEAM_KOR[game_key[8:10]]
        bteam = self.TEAM_KOR[game_key[10:12]]
        line_up = record.Record().get_teamrank(game_date, tteam, bteam)
        self.team_info['tteam'] = [team for team in line_up if team['TEAM'] == tteam][0]
        self.team_info['bteam'] = [team for team in line_up if team['TEAM'] == bteam][0]
