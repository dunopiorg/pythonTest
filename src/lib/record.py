from datetime import datetime
from lib import query_loader
import pandas as pd
import pymysql.cursors
import config
import time


class Record(object):

    _HOST = config.DB_HOST
    _USER = config.DB_USER
    _PASSWORD = config.DB_PASSWORD
    _DB = config.DB_NAME
    _PORT = config.DB_PORT
    if config.RUN_PATH is None:
        ql = query_loader.QueryLoader()
    else:
        ql = query_loader.QueryLoader('../query_xml')


    def __init__(self):
        self._HOST = config.DB_HOST
        self._USER = config.DB_USER
        self._PASSWORD = config.DB_PASSWORD
        self._DB = config.DB_NAME
        self._PORT = config.DB_PORT

    # region 조건표에 따른 타자기록을 가져온다.
    @classmethod
    def get_season_hitters_total_df(cls):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_hitter", "get_season_hitters_total_record")
        query = query_format.format()

        df = pd.read_sql(query, conn)
        conn.close()
        return df

    @classmethod
    def get_total_hitters_df(cls):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_hitter", "get_total_hitters_record")
        query = query_format.format()

        df = pd.read_sql(query, conn)
        conn.close()
        return df

    @classmethod
    def get_hitter_total_df(cls, hitter_code):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_hitter", "get_hitter_total_record")
        query = query_format.format(PCODE=hitter_code)

        df = pd.read_sql(query, conn)
        conn.close()
        return df

    @classmethod
    def get_all_hitters_season_realtime_record(cls, game_key):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')
        date = game_key[0:8]
        query_format = cls.ql.get_query("query_hitter", "get_all_hitters_season_realtime_record")
        query = query_format.format(DATE=date)

        df = pd.read_sql(query, conn)
        conn.close()
        return df

    @classmethod
    def get_hitter_season_realtime_record(cls, game_key, hitter_code):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')
        date = game_key[0:8]
        query_format = cls.ql.get_query("query_hitter", "get_hitter_season_realtime_record")
        query = query_format.format(DATE=date, PCODE=hitter_code)

        df = pd.read_sql(query, conn)
        conn.close()
        return df

    @classmethod
    def get_hitter_season_record(cls, hitter_code):
        # todo 180416 조건표가 정해지면 생각해 볼 것
        pass

    @classmethod
    def get_hitter_today_record(cls, game_key, hitter_code):
        """
        hitter의 오늘 경기 기록을 가져온다.
        :param game_key:
        :param hitter_code:
        :return:
        """
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_hitter", "get_hitter_today_record")
        query = query_format.format(game_key, hitter_code)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        return result

    @classmethod
    def get_hitter_basic_record(cls, hitter_code, state=None):
        """
        시즌기록, 통산기록을 가져온다.
        :param hitter_code:
        :param state: "'HR', 'HIT', 'RBI'...", 없으면 전체를 가져온다.
        :return:
        """
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        if state is None:
            add_state = ' '
        else:
            add_state = " AND STATE = '{0}' ".format(state)

        query_format = cls.ql.get_query("query_hitter", "get_hitter_basic_record")
        query = query_format.format(hitter_code, add_state)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        conn.close()
        return result

    @classmethod
    def get_hitter_vs_pitcher_record(cls, hitter_code, pitcher_code, state=None):
        """
        상대-선수에 대한 통산기록을 가져온다.
        :param hitter_code:
        :param pitcher_code:
        :param state: 'HR', 'HIT', 'RBI'...", 없으면 전체를 가져온다.
        :return:
        """
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')
        if state is None:
            add_state = ' '
        else:
            add_state = " AND STATE = '{0}' ".format(state)

        query_format = cls.ql.get_query("query_hitter", "get_hitter_vs_pitcher_record")
        query = query_format.format(pitcher_code, hitter_code, add_state)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        conn.close()
        return result

    @classmethod
    def get_hitter_vs_team_record(cls, hitter_code, pitcher_team, state=None):
        """
        상대-팀에 대한 정보를 가져온다.
        :param hitter_code:
        :param pitcher_team: 'HR', 'HIT', 'RBI'...", 없으면 전체를 가져온다.
        :param state:
        :return:
        """
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')
        if state is None:
            add_state = ' '
        else:
            add_state = " AND STATE = '{0}' ".format(state)

        query_format = cls.ql.get_query("query_hitter", "get_hitter_vs_team_record")
        query = query_format.format(pitcher_team, hitter_code, add_state)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        conn.close()
        return result

    @classmethod
    def get_hitter_score_record(cls, hitter_code, score_split, state=None):
        """
        점수차에 대한 데이터를 가져온다.
        :param hitter_code:
        :param score_split:  'HR', 'HIT', 'RBI'...", 없으면 전체를 가져온다.
        :param state:
        :return:
        """
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')
        if state is None:
            add_state = ' '
        else:
            add_state = " AND STATE = '{0}' ".format(state)

        query_format = cls.ql.get_query("query_hitter", "get_hitter_score_record")
        query = query_format.format(score_split, hitter_code, add_state)

        """
        query = "SELECT RANK, SUBJECT, OPPONENT, LEAGUE, GYEAR, HITTER, HITNAME " \
                "							    , PITCHER, PITNAME, PITTEAM, PITTEAM_NAME  " \
                "								, PA, STATE, STATE_SPLIT, RESULT " \
                "FROM  " \
                "( " \
                "	SELECT DENSE_RANK() OVER(PARTITION BY STATE ORDER BY RESULT DESC) AS RANK " \
                "						, SUBJECT, OPPONENT, LEAGUE, GYEAR, HITTER, HITNAME, PITCHER, PITNAME, PITTEAM " \
                "						, PITTEAM_NAME, PA, STATE, STATE_SPLIT, RESULT " \
                "	FROM baseball.accum_record_hitter " \
                "	WHERE GYEAR IN ('NA', 2017)  " + add_state + \
                "	AND PITCHER = 'NA'  " \
                "	AND PITTEAM = 'NA'  " \
                "  AND OPPONENT = 'ALL' " \
                "	AND STATE_SPLIT = '{0}' " \
                " ) AAA " \
                "WHERE HITTER = '{1}'  ".format(score_split, hitter_code)
        """

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        conn.close()
        return result

    @classmethod
    def get_hitter_base_record(cls, hitter_code, base_split, state=None):
        """
        주자상황 데이터를 가져온다.
        :param hitter_code:
        :param base_split:
        :param state: 'HR', 'HIT', 'RBI'...", 없으면 전체를 가져온다.
        :return:
        """
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')
        if state is None:
            add_state = ' '
        else:
            add_state = " AND STATE = '{0}' ".format(state)

        query_format = cls.ql.get_query("query_hitter", "get_hitter_base_record")
        query = query_format.format(base_split, hitter_code, add_state)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        conn.close()
        return result

    @classmethod
    def get_hitter_continuous_record(cls, game_id, hitter_code):
        """
        연속 경기를 가져온다.
        :param hitter_code:
        :return:
        """
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_hitter", "get_hitter_continuous_record")
        query = query_format.format(hitter_code, game_id[0:8])  # datetime.now().year

        result_list = []

        df = pd.read_sql(query, conn)
        df_to_dict = df.to_dict('records')
        if df_to_dict:
            result_list.extend(df_to_dict)

        conn.close()
        return result_list

    @classmethod
    def get_hitter_first_ball(cls, hitter_code):
        """
        hitter의 초구 정보를 가져온다.
        :param hitter_code:
        :return:
        """
        result_list = []
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_hitter", "get_hitter_first_ball")
        query = query_format.format(hitter_code)

        df = pd.read_sql(query, conn)
        df_to_dict = df.to_dict('records')
        if df_to_dict:
            result_list.extend(df_to_dict)

        conn.close()
        return result_list

    @classmethod
    def get_hitter_gamenum(cls, hitter_code):
        """
        타자의 출장기록
        :param hitter_code:
        :return:
        """
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_hitter", "get_hitter_gamenum")
        query = query_format.format(hitter_code)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        conn.close()
        return result

    @classmethod
    def get_hitter_vs_pitcher_df(cls, hitter_code, pitcher_code):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_hitter", "get_hitter_vs_pitcher_how_record")
        query = query_format.format(HITTER=hitter_code, PITCHER=pitcher_code)

        df = pd.read_sql(query, conn)
        conn.close()
        return df

    @classmethod
    def get_hitter_vs_team_df(cls, hitter_code, pitcher_team):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_hitter", "get_hitter_vs_team_how_record")
        query = query_format.format(HITTER=hitter_code, TEAM=pitcher_team)

        df = pd.read_sql(query, conn)
        conn.close()
        return df

    @classmethod
    def get_hitter_today_game_df(cls, game_key, hitter_code):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_hitter", "get_hitter_today_game_record")
        query = query_format.format(GAMEID=game_key, PLAYERID=hitter_code)

        df = pd.read_sql(query, conn)
        conn.close()
        return df
    # endregion

    # region 타자기록 Update
    @classmethod
    def update_hitter_count_record(cls, data_dict):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER, password=cls._PASSWORD, db=cls._DB,
                               charset='utf8mb4')

        query_format = cls.ql.get_query("query_hitter", "update_hitter_count_record")
        query = query_format.format(**data_dict)

        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            conn.commit()
        return result

    @classmethod
    def update_hitter_pa(cls, data_dict):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER, password=cls._PASSWORD, db=cls._DB,
                               charset='utf8mb4')

        query_format = cls.ql.get_query("query_hitter", "update_hitter_pa")
        query = query_format.format(**data_dict)

        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
        return result
    # endregion

    # region 조건표에 따른 투수기록을 가져온다.
    @classmethod
    def get_pitcher_df(cls, pitcher_code):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_pitcher", "get_pitcher_record")
        query = query_format.format(PCODE=pitcher_code)

        df = pd.read_sql(query, conn)
        conn.close()
        return df

    @classmethod
    def get_pitcher_continuous_record(cls, game_id, pitcher_code):
        """
        연속 경기를 가져온다.
        :param hitter_code:
        :return:
        """
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_pitcher", "get_pitcher_continue_record")
        query = query_format.format(PCODE=pitcher_code, DATE=game_id[0:8])  # datetime.now().year

        result_list = []

        df = pd.read_sql(query, conn)
        df_to_dict = df.to_dict('records')
        if df_to_dict:
            result_list.extend(df_to_dict)

        conn.close()
        return result_list

    @classmethod
    def get_pitcher_continuous_record_v0(cls, game_id, pitcher_code):
        """
        연속 경기를 가져온다.
        :param hitter_code:
        :return:
        """
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_pitcher", "get_pitcher_continue_record")
        query = query_format.format(PCODE=pitcher_code, DATE=game_id[0:8])  # datetime.now().year

        df = pd.read_sql(query, conn)

        conn.close()
        return df

    @classmethod
    def get_total_pitchers_detail_df(cls):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_pitcher", "get_total_pitchers_detail_record")
        query = query_format.format()

        df = pd.read_sql(query, conn)
        conn.close()
        return df

    @classmethod
    def get_total_pitchers_df(cls):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_pitcher", "get_total_pitchers_record")
        query = query_format.format()

        df = pd.read_sql(query, conn)
        conn.close()
        return df

    @classmethod
    def get_pitcher_season_realtime_record(cls, game_key):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')
        date = game_key[0:8]
        query_format = cls.ql.get_query("query_pitcher", "get_pitcher_season_realtime_record")
        query = query_format.format(DATE=date)

        df = pd.read_sql(query, conn)
        conn.close()
        return df

    @classmethod
    def get_pitcher_total_df(cls, hitter_code):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_pitcher", "get_pitcher_total_record")
        query = query_format.format(PCODE=hitter_code)

        df = pd.read_sql(query, conn)
        conn.close()
        return df

    @classmethod
    def get_pitcher_today_record(cls, game_key, pitcher_code):
        """
        pitcher 의 오늘 경기 기록을 가져온다.
        :param game_key:
        :param pitcher_code:
        :return:
        """
        result = None
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query = "SELECT PA, HIT, H1, H2, H3, HR, RBI, BB, IB, HBP, SO, (SO + SH + GR + FL) AS PB  " \
                "FROM " \
                "( " \
                "	SELECT SUM(CASE WHEN HOW IN ('H1','H2','H3','HR','HI','HB','BB','IB','HP','KK','KN','KB' " \
                "						,'KW','KP','IN','OB','IP','XX','SH','SF','FC','GD','TP','GR','BN','FL','LL','IF','FF') THEN 1 " \
                "			ELSE 0 END) AS PA " \
                "			, SUM(CASE WHEN HOW IN ('H1','H2','H3','HR','HI','HB') THEN 1 " \
                "								ELSE 0 END) AS HIT " \
                "			, SUM(CASE WHEN HOW = 'H1' THEN 1 ELSE 0 END) AS H1 " \
                "			, SUM(CASE WHEN HOW = 'H2' THEN 1 ELSE 0 END) AS H2 " \
                "			, SUM(CASE WHEN HOW = 'H3' THEN 1 ELSE 0 END) AS H3 " \
                "			, SUM(CASE WHEN HOW = 'HR' THEN 1 ELSE 0 END) AS HR " \
                "			, SUM(CASE WHEN PLACE IN ('E','R','H')  THEN 1 ELSE 0 END) AS RBI " \
                "			, SUM(CASE WHEN HOW IN ('BB', 'IB') THEN 1 ELSE 0 END) AS BB " \
                "			, SUM(CASE WHEN HOW = 'IB' THEN 1 ELSE 0 END) AS IB  -- 고의 사구 " \
                "			, SUM(CASE WHEN HOW = 'HP' THEN 1 ELSE 0 END) AS HBP " \
                "			, SUM(CASE WHEN HOW IN ('KK','KN','KB','KW','KP') THEN 1 " \
                "							ELSE 0 END) AS SO  -- 삼진 " \
                "			, SUM(CASE WHEN HOW = 'SH' THEN 1 ELSE 0 END) AS SH -- 희생 번트 " \
                "			, SUM(CASE WHEN HOW = 'GR' AND PLACE IN ('0', '1', '2', '3') THEN 1 ELSE 0 END) AS GR " \
                "			, SUM(CASE WHEN HOW = 'FL' AND PLACE IN ('0', '1', '2', '3') THEN 1 ELSE 0 END) AS FL " \
                "	FROM baseball.gamecontapp " \
                "	  WHERE 1 = 1  " \
                "    AND GMKEY = '{1}'" \
                "	  AND pitcher = '{0}' " \
                "	GROUP BY pitcher " \
                ") AAA ".format(game_key, pitcher_code)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        return result

    @classmethod
    def get_pitcher_basic_record(cls, pitcher_code, state=None):
        """
        PITCHER 의 기본(시즌, 통산) 기록을 가져온다.
        :param pitcher_code:
        :param state:
        :return:
        """
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        if state is None:
            add_state = ' '
        else:
            add_state = " AND STATE = '{0}' ".format(state)

        query_format = cls.ql.get_query("query_pitcher", "get_pitcher_basic_record")
        query = query_format.format(pitcher_code, add_state)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        conn.close()
        return result

    @classmethod
    def get_pitcher_vs_team_record(cls, pitcher_code, hit_team=None, state=None):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        if state is None:
            add_state = ' '
        else:
            add_state = " AND STATE = '{0}' ".format(state)

        if hit_team is None:
            add_team = ' '
        else:
            add_team = " AND HITTEAM = '{0}' ".format(hit_team)

        query_format = cls.ql.get_query("query_pitcher", "get_pitcher_vs_team_record")
        query = query_format.format(pitcher_code, add_state, add_team)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        conn.close()
        return result

    @classmethod
    def get_pitcher_vs_hitter_record(cls, pitcher_code, hitter_code, state=None):
        """
        선수와의 대결 정보
        :param pitcher_code:
        :param hitter_code:
        :param state:
        :return:
        """
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        if state is None:
            add_state = ' '
        else:
            add_state = " AND STATE = '{0}' ".format(state)

        query_format = cls.ql.get_query("query_pitcher", "get_pitcher_vs_hitter_record")
        query = query_format.format(pitcher_code, hitter_code,  add_state)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        conn.close()
        return result

    @classmethod
    def get_pitcher_basic_total_record(cls, pitcher_code):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_pitcher", "get_pitcher_basic_total_record")
        query = query_format.format(pitcher_code)

        result_list = []

        df = pd.read_sql(query, conn)
        conn.close()

        pitcher_season_dict = df[df['GYEAR'] == '2017'].to_dict('record')[0]
        if pitcher_season_dict:
            result_list.append(pitcher_season_dict)
        count_record = df[['GAMENUM', 'CG', 'SHO', 'W', 'L', 'SV', 'HOLD', 'BF', 'HIT', 'HR', 'BB', 'HP', 'KK', 'R', 'ER', 'SCORE', 'QS', 'STARTING_NUM']].sum().astype(int)
        rate_record = df[['ERA', 'INNG', 'INNK', 'OPS', 'WHIP', 'INNB', 'KK_BB_RT', 'PA_BB_RT', 'PA_KK_RT', 'WRA']].mean().round(3)

        total_record = count_record.add(rate_record, fill_value=0)
        total_record['PITCHER'] = df.iloc[-1:, 0].values[0]
        total_record['PITNAME'] = df.iloc[-1:, 1].values[0]
        total_record['GYEAR'] = 'NA'
        total_record['STATE'] = 'STARTING'
        total_record['STATE_SPLIT'] = 'STARTING_TOTAL'
        total_record['LEAGUE'] = 'ALL'
        total_record['TEAM'] = df.iloc[-1:, 3].values[0]
        pitcher_all_dict = dict(total_record)
        if pitcher_all_dict:
            result_list.append(pitcher_all_dict)

        return result_list

    @classmethod
    def get_previous_game_pitcher_record(cls, game_date, pitcher_code):
        """
        투수의 이전 게임 기록
        :param game_date:
        :param pitcher_code:
        :return:
        """
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_pitcher", "get_previous_game_pitcher_record")
        query = query_format.format(game_date, pitcher_code)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        conn.close()
        return result

    @classmethod
    def get_pitcher_gamenum(cls, pitcher_code):
        """
        투수의 출장기록
        :param pitcher_code:
        :return:
        """
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_pitcher", "get_pitcher_gamenum")
        query = query_format.format(pitcher_code)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        conn.close()
        return result

    @classmethod
    def get_pitcher_gamenum_cnt(cls, counter):
        """
        역대 couter 이상 출장기록 개수
        :param counter:
        :return:
        """
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_pitcher", "get_pitcher_gamenum_cnt")
        query = query_format.format(counter)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        conn.close()
        return result
    # endregion 조건표에 따른 투수기록을 가져온다.

    # region 투수기록 Update

    # endregion

    # region 기타 Functions
    @classmethod
    def get_pitzone_info(cls, game_key, bat_order, ball_count, hitter, pitcher):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_common", "get_pitzone_info")
        query = query_format.format(game_key, bat_order, ball_count, hitter, pitcher)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        return result

    @classmethod
    def get_gameinfo_data(cls, game_key):
        """
        게임 환경 정보
        :param game_key:
        :return:
        """
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_common", "get_gameinfo_data")
        query = query_format.format(game_key)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        return result

    @classmethod
    def get_starting_line_up(cls, game_key):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_common", "get_starting_line_up")
        query = query_format.format(game_key)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        return result

    @classmethod
    def get_gamecontapp(cls, game_key, hitter, pitcher, inn, how):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_common", "get_gamecontapp")
        query = query_format.format(game_key, hitter, pitcher, inn, how)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        return result

    @classmethod
    def get_player_info(cls, player_code):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_common", "get_player_info")
        query = query_format.format(player_code)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        return result

    @classmethod
    def get_team_vs_team(cls, home_team, away_team, game_year):
        '''
        Home Team 기준으로 데이터를 뽑는다. 통산 기록은 game_year를 %로 하면 된다.
        :param home_team:
        :param away_team:
        :param game_year:
        :return:
        '''
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_common", "get_team_vs_team")
        query = query_format.format(game_year, home_team+away_team, away_team+home_team, home_team)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        return result

    @classmethod
    def get_teamrank_daily(cls, team):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_common", "get_teamrank_daily")
        query = query_format.format(team)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        return result

    @classmethod
    def get_teamrank(cls, year, tteam, bteam):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_common", "get_teamrank")
        query = query_format.format(year, tteam, bteam)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        return result

    @classmethod
    def get_li_rate(cls, year, inn_no, tb, out_cn, runner_sc, score_gap):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        runner = runner_sc[:-1]
        if score_gap[-1] == 'L':
            score = int(score_gap[:-1]) * -1
        else:
            score = int(score_gap[:-1])

        query_format = cls.ql.get_query("query_common", "get_li_rate")
        query = query_format.format(year, inn_no, tb, out_cn, runner, score)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        return result

    @classmethod
    def get_max_li_rate(cls, game_id, seq_no):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_common", "get_max_li_rate")
        query = query_format.format(game_id, seq_no)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        return result

    @classmethod
    def get_record_matrix_mix(cls, game_id, year, seq_no):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_common", "get_record_matrix_mix")
        query = query_format.format(game_id, year, seq_no)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        return result

    @classmethod
    def get_team_korean_names(cls):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_common", "get_team_kor_names")
        query = query_format.format()

        df = pd.read_sql(query, conn)
        conn.close()

        if df.empty:
            return None
        else:
            return df.set_index('team').transpose().to_dict('records')[0]

    @classmethod
    def get_category_score(cls):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_common", "get_category_score")
        query = query_format.format()

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        return result
    # endregion 기타 Functions

    @classmethod
    def test_get_gamecontapp(cls):
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_common", "test_get_gamecontapp")
        query = query_format.format()  # datetime.now().year

        df = pd.read_sql(query, conn)

        conn.close()
        return df


if __name__ == "__main__":
    record = Record()
    record.get_hitter_total_record(76249)
    # record.get_pitcher_basic_total_record(60263)

    # start_time = time.time()
    # record.test_get_gamecontapp()
    # print("--- %s Seconds --- " % (time.time() - start_time))
    #
    # start_time = time.time()
    # record.get_hitter_basic_record('76249')
    # print("--- %s Seconds --- " % (time.time() - start_time))
    # hitter,hitteam,pitcher,pitteam,state,score,base
    # data = {'hitter': 78224, 'hitteam': 'OB', 'pitcher': 79140, 'pitteam': 'LG', 'state': 'HR', 'score': '0D', 'base': '1B'}
    # record_df = record.get_total_hitter_record(data)
    # print(record_df)
    # hitter = '78224'
    # print(record.get_hitter_basic_record(hitter))
