import pandas as pd
import pymysql.cursors
from datetime import datetime


class Record(object):

    _HOST = 'localhost'
    _USER = 'root'
    _PASSWORD = 'lab2ai64'
    _DB = 'baseball'
    _PORT = 3307

    def __init__(self):
        self._HOST = 'localhost'
        self._USER = 'root'
        self._PASSWORD = 'lab2ai64'
        self._DB = 'baseball'
        self._PORT = 3307

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
        query = "SELECT GYEAR, HITTER, HITNAME, PA, AB, S_CNT, S_CNT_RNK, B_CNT, B_CNT_RNK, F_CNT, F_CNT_RNK, H_CNT, T_CNT, T_CNT_RNK "\
                    "FROM  "\
                    "( "\
                    "	SELECT GYEAR, HITTER, HITNAME "\
                    "	, PA, AB "\
                    "	, S_CNT  "\
                    "	, DENSE_RANK() OVER (ORDER BY S_CNT DESC) AS S_CNT_RNK "\
                    "	, B_CNT "\
                    "	, DENSE_RANK() OVER (ORDER BY B_CNT DESC) AS B_CNT_RNK "\
                    "	, F_CNT "\
                    "	, DENSE_RANK() OVER (ORDER BY F_CNT DESC) AS F_CNT_RNK "\
                    "	, H_CNT "\
                    "	, DENSE_RANK() OVER (ORDER BY H_CNT DESC) AS H_CNT_RNK "\
                    "	, T_CNT  "\
                    "	, DENSE_RANK() OVER (ORDER BY T_CNT DESC) AS T_CNT_RNK "\
                    "	FROM "\
                    "	(  "\
                    "		select GYEAR, HITTER, HITNAME  "\
                    "		, SUM(CASE WHEN HOW IN ('H1','H2','H3','HR','HI','HB','BB','IB','HP','KK','KN','KB'  "\
                    "							,'KW','KP','IN','OB','IP','XX','SH','SF','FC','GD','TP','GR','BN','FL','LL','IF','FF') THEN 1  "\
                    "				ELSE 0 END) AS PA  "\
                    "		, SUM(CASE WHEN HOW IN ('H1','H2','H3','HR','HI','HB','GR','BN','FL','LL','IF','FF', "\
                    "					'KK','KN','KB','KW','KP','IP','XX','FC','GD','TP') THEN 1 ELSE 0 END) AS AB  "\
                    "		, SUM(CASE WHEN LEFT(BCOUNT, 1) = 'S' THEN 1 ELSE 0 END) AS S_CNT  "\
                    "		, SUM(CASE WHEN LEFT(BCOUNT, 1) = 'B' THEN 1 ELSE 0 END) AS B_CNT  "\
                    "		, SUM(CASE WHEN LEFT(BCOUNT, 1) = 'F' THEN 1 ELSE 0 END) AS F_CNT  "\
                    "		, SUM(CASE WHEN LEFT(BCOUNT, 1) = 'H' THEN 1 ELSE 0 END) AS H_CNT  "\
                    "		, SUM(CASE WHEN LEFT(BCOUNT, 1) = 'T' THEN 1 ELSE 0 END) AS T_CNT	 "\
                    "		from baseball.gamecontapp_all "\
                    "		where 1 = 1  "\
                    "		and bcount != ''  "\
                    "		GROUP BY GYEAR, HITTER, HITNAME  "\
                    "	) A  "\
                    "	WHERE pa > 300 "\
                    "	AND GYEAR = YEAR(CURDATE()) "\
                    ") AAA "\
                    "WHERE HITTER = %s " % hitter_code
        df = pd.read_sql(query, conn)
        df_to_dict = df.to_dict('records')
        if df_to_dict:
            result_list.extend(df_to_dict)

        conn.close()
        return result_list

    # region 조건표에 따른 타자기록을 가져온다.
    @classmethod
    def get_hitter_today_record(cls, game_key, hitter_code):
        """
        hitter의 오늘 경기 기록을 가져온다.
        :param game_key:
        :param hitter_code:
        :return:
        """
        result = None
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query = "SELECT HITNAME, PA, AB, HIT, HR, RBI, BB, KK " \
                "FROM " \
                "( " \
                "	SELECT SUM(CASE WHEN HOW IN ('H1','H2','H3','HR','HI','HB','BB','IB','HP','KK','KN','KB' " \
                "						,'KW','KP','IN','OB','IP','XX','SH','SF','FC','GD','TP','GR','BN','FL','LL','IF','FF') THEN 1 " \
                "											ELSE 0 END) AS PA " \
                "						, SUM(CASE WHEN HOW IN ('H1','H2','H3','HR','HI','HB','GR','BN','FL','LL','IF','FF', " \
                "						'KK','KN','KB','KW','KP','IP','XX','FC','GD','TP') THEN 1 " \
                "										ELSE 0 END) AS AB " \
                "						, SUM(CASE WHEN HOW IN ('H1','H2','H3','HR','HI','HB') THEN 1 ELSE 0 END) AS HIT " \
                "						, SUM(CASE WHEN HOW = 'HR' THEN 1 ELSE 0 END) AS HR " \
                "						, SUM(CASE WHEN PLACE IN ('E','R','H')  THEN 1 ELSE 0 END) AS RBI " \
                "						, SUM(CASE WHEN HOW IN ('BB', 'IB') THEN 1 ELSE 0 END) AS BB " \
                "						, SUM(CASE WHEN HOW = 'KK' THEN 1 ELSE 0 END) AS KK " \
                "						, HITNAME " \
                "	FROM baseball.gamecontapp_all " \
                "	WHERE HITTER = '{1}' " \
                "	AND GMKEY = '{0}' " \
                ") TODAY " \
                "WHERE PA > 0 ".format(game_key, hitter_code)

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

        query = "SELECT RANK, SUBJECT, OPPONENT, LEAGUE, GYEAR, HITTER, HITNAME "\
                "							    , PITCHER, PITNAME, PITTEAM, PITTEAM_NAME  "\
                "								, PA, STATE, STATE_SPLIT, RESULT "\
                "FROM  "\
                "( "\
                "	SELECT DENSE_RANK() OVER(PARTITION BY GYEAR, STATE ORDER BY RESULT DESC) AS RANK "\
                "						, SUBJECT, OPPONENT, LEAGUE, GYEAR, HITTER, HITNAME, PITCHER, PITNAME, PITTEAM "\
                "						, PITTEAM_NAME, PA, STATE, STATE_SPLIT, RESULT "\
                "	FROM baseball.accum_record_hitter "\
                "	WHERE GYEAR IN ('NA', YEAR(CURDATE()))  " + add_state + \
                "	AND PITCHER = 'NA'  "\
                "	AND PITTEAM = 'NA'  "\
                "	AND STATE_SPLIT = 'BASIC' "\
                " ) AAA "\
                "WHERE HITTER = '{0}'  ".format(hitter_code)

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

        query = "SELECT RANK, SUBJECT, OPPONENT, LEAGUE, GYEAR, HITTER, HITNAME " \
                "							    , PITCHER, PITNAME, PITTEAM, PITTEAM_NAME  " \
                "								, PA, STATE, STATE_SPLIT, RESULT " \
                "FROM  " \
                "( " \
                "	SELECT DENSE_RANK() OVER(PARTITION BY STATE ORDER BY RESULT DESC) AS RANK " \
                "						, SUBJECT, OPPONENT, LEAGUE, GYEAR, HITTER, HITNAME, PITCHER, PITNAME, PITTEAM " \
                "						, PITTEAM_NAME, PA, STATE, STATE_SPLIT, RESULT " \
                "	FROM baseball.accum_record_hitter " \
                "	WHERE GYEAR = 'NA'  " + add_state + \
                "	AND PITCHER = '{0}'  " \
                "	AND PITTEAM = 'NA'  " \
                "  AND OPPONENT = 'PITCHER' "\
                "	AND STATE_SPLIT = 'VERSUS' " \
                " ) AAA " \
                "WHERE HITTER = '{1}'  ".format(pitcher_code, hitter_code)

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

        query = "SELECT RANK, SUBJECT, OPPONENT, LEAGUE, GYEAR, HITTER, HITNAME " \
                "							    , PITCHER, PITNAME, PITTEAM, PITTEAM_NAME  " \
                "								, PA, STATE, STATE_SPLIT, RESULT " \
                "FROM  " \
                "( " \
                "	SELECT DENSE_RANK() OVER(PARTITION BY STATE ORDER BY RESULT DESC) AS RANK " \
                "						, SUBJECT, OPPONENT, LEAGUE, GYEAR, HITTER, HITNAME, PITCHER, PITNAME, PITTEAM " \
                "						, PITTEAM_NAME, PA, STATE, STATE_SPLIT, RESULT " \
                "	FROM baseball.accum_record_hitter " \
                "	WHERE GYEAR IN ('NA', YEAR(CURDATE()))  " + add_state + \
                "	AND PITCHER = 'NA'  " \
                "	AND PITTEAM = '{0}'  " \
                "  AND OPPONENT = 'TEAM' " \
                "	AND STATE_SPLIT = 'VERSUS' " \
                " ) AAA " \
                "WHERE HITTER = '{1}'  ".format(pitcher_team, hitter_code)

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

        query = "SELECT RANK, SUBJECT, OPPONENT, LEAGUE, GYEAR, HITTER, HITNAME " \
                "							    , PITCHER, PITNAME, PITTEAM, PITTEAM_NAME  " \
                "								, PA, STATE, STATE_SPLIT, RESULT " \
                "FROM  " \
                "( " \
                "	SELECT DENSE_RANK() OVER(PARTITION BY STATE ORDER BY RESULT DESC) AS RANK " \
                "						, SUBJECT, OPPONENT, LEAGUE, GYEAR, HITTER, HITNAME, PITCHER, PITNAME, PITTEAM " \
                "						, PITTEAM_NAME, PA, STATE, STATE_SPLIT, RESULT " \
                "	FROM baseball.accum_record_hitter " \
                "	WHERE GYEAR IN ('NA', YEAR(CURDATE()))  " + add_state + \
                "	AND PITCHER = 'NA'  " \
                "	AND PITTEAM = 'NA'  " \
                "  AND OPPONENT = 'ALL' " \
                "	AND STATE_SPLIT = '{0}' " \
                " ) AAA " \
                "WHERE HITTER = '{1}'  ".format(score_split, hitter_code)

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

        query = "SELECT RANK, SUBJECT, OPPONENT, LEAGUE, GYEAR, HITTER, HITNAME " \
                "							    , PITCHER, PITNAME, PITTEAM, PITTEAM_NAME  " \
                "								, PA, STATE, STATE_SPLIT, RESULT " \
                "FROM  " \
                "( " \
                "	SELECT DENSE_RANK() OVER(PARTITION BY STATE ORDER BY RESULT DESC) AS RANK " \
                "						, SUBJECT, OPPONENT, LEAGUE, GYEAR, HITTER, HITNAME, PITCHER, PITNAME, PITTEAM " \
                "						, PITTEAM_NAME, PA, STATE, STATE_SPLIT, RESULT " \
                "	FROM baseball.accum_record_hitter " \
                "	WHERE GYEAR IN ('NA', YEAR(CURDATE()))  " + add_state + \
                "	AND PITCHER = 'NA'  " \
                "	AND PITTEAM = 'NA'  " \
                "  AND OPPONENT = 'ALL' " \
                "	AND STATE_SPLIT = '{0}' " \
                " ) AAA " \
                "WHERE HITTER = '{1}'  ".format(base_split, hitter_code)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        conn.close()
        return result

    @classmethod
    def get_hitter_continuous_record(cls, hitter_code):
        """
        연속 경기를 가져온다.
        :param hitter_code:
        :return:
        """
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        result_list = []
        query = "SELECT GMKEY, GDAY, HOW, PLACE, HITTER, HITNAME "\
                "FROM  baseball.gamecontapp_all "\
                "WHERE HITTER = '{0}' "\
                "AND GMKEY LIKE '{1}%'"\
                "ORDER BY GMKEY DESC, SERNO DESC " \
                "LIMIT 100 ".format(hitter_code, datetime.now().year)

        df = pd.read_sql(query, conn)
        df_to_dict = df.to_dict('records')
        if df_to_dict:
            result_list.extend(df_to_dict)

        conn.close()
        return result_list

    # endregion

    # region 타자기록 Update
    def update_hitter_count_record(self, data_dict):
        result = None
        conn = pymysql.connect(host=self._HOST, port=self._PORT, user=self._USER, password=self._PASSWORD, db=self._DB,
                               charset='utf8mb4')

        query = "UPDATE baseball.accum_record_hitter T1 INNER JOIN "\
                            "( "\
                            "SELECT HITTER, STATE, STATE_SPLIT, OPPONENT, LEAGUE, PITTEAM, GYEAR, RESULT "\
                            "FROM baseball.accum_record_hitter "\
                            "WHERE 1 = 1 " \
                            "AND HITTER = '{hitter}' "\
                            "AND STATE = '{state}' "\
                            "AND STATE_SPLIT = '{state_split}' "\
                            "AND OPPONENT ='{opponent}' "\
                            "AND GYEAR IN ('{gyear}', 'NA') "\
                            "AND PITCHER = '{pitcher}' "\
                            "AND PITTEAM = '{pitteam}' "\
                            ") AS T2 " \
                            "ON T1.HITTER = T2.HITTER " \
                            "AND T1.STATE = T2.STATE " \
                            "AND T1.STATE_SPLIT = T2.STATE_SPLIT " \
                            "AND T1.OPPONENT = T2.OPPONENT " \
                            "AND T1.LEAGUE = T2.LEAGUE " \
                            "AND T1.PITTEAM = T2.PITTEAM " \
                            "AND T1.GYEAR = T2.GYEAR " \
                "SET T1.RESULT = T2.RESULT  + 1 "\
                            "WHERE T1.HITTER = '{hitter}' " \
                            "AND T1.HITTER = T2.HITTER " \
                            "AND T1.STATE = T2.STATE " \
                            "AND T1.STATE_SPLIT = T2.STATE_SPLIT " \
                            "AND T1.OPPONENT = T2.OPPONENT " \
                            "AND T1.LEAGUE = T2.LEAGUE " \
                            "AND T1.PITTEAM = T2.PITTEAM " \
                            "AND T1.GYEAR = T2.GYEAR " \
                            "AND T1.STATE = '{state}' " \
                            "AND T1.STATE_SPLIT = '{state_split}' "\
                            "AND T1.OPPONENT = '{opponent}' "\
                            "AND T1.GYEAR IN ('{gyear}', 'NA') "\
                            "AND T1.PITCHER = '{pitcher}' "\
                            "AND T1.PITTEAM = '{pitteam}' ".format(**data_dict)

        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            conn.commit()
        return result
    # endregion

    def call_update_state_rank(self, data_dict):
        """
        Procedure 호출 (사용 X)
        :param data_dict:
        :return:
        """
        result = ""
        conn = pymysql.connect(host=self._HOST, port=self._PORT, user=self._USER, password=self._PASSWORD, db=self._DB,
                               charset='utf8mb4')

        args = (data_dict['state'], data_dict['splits'], result)

        with conn.cursor() as cursor:
            call_result = cursor.callproc('UPDATE_STATE_RANK', args)
            cursor.execute('SELECT @RESULT')
            result = cursor.fetchall()
            conn.commit()
        return result

    @classmethod
    def get_personal_info(cls, player_code):
        """
        선수 기본정보를 가져온다.
        :param player_code:
        :return:
        """
        result = None
        conn = pymysql.connect(host=cls._HOST, port=cls._PORT, user=cls._USER,
                               password=cls._PASSWORD, db=cls._DB, charset='utf8mb4')

        query = "SELECT NAME, TEAM, POSITION, BACKNUM, BIRTH, HEIGHT, " \
                "WEIGHT, MONEY, INDATE " \
                "FROM baseball.person " \
                "WHERE PCODE = {0}".format(player_code)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            conn.commit()
        return result

if __name__ == "__main__":
    record = Record()

    # hitter,hitteam,pitcher,pitteam,state,score,base
    # data = {'hitter': 78224, 'hitteam': 'OB', 'pitcher': 79140, 'pitteam': 'LG', 'state': 'HR', 'score': '0D', 'base': '1B'}
    # record_df = record.get_total_hitter_record(data)
    # print(record_df)
    hitter = '78224'
    print(Record.get_hitter_basic_record(hitter, "'HIT', 'H2', 'BB'"))
