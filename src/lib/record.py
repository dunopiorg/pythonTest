import pandas as pd
import pymysql.cursors
from datetime import datetime

class Record(object):

    def __init__(self):
        self._HOST = 'localhost'
        self._USER = 'root'
        self._PASSWORD = 'lab2ai64'
        self._DB = 'baseball'
        self._PORT = 3307

    def get_df_season_pitcher_record(self, pitcher):
        result = pd.DataFrame()
        return result

    def get_df_season_hitter_vs_pitcher(self, hitter, pitcher):
        conn = pymysql.connect(host=self._HOST, port=self._PORT, user=self._USER, password=self._PASSWORD, db=self._DB, charset='utf8mb4')
        sql = "SELECT HITTER, HITNAME, PITCHER, PITNAME "\
                "               , RBI AS RBI_CN "\
                "               , DENSE_RANK() OVER(ORDER BY RBI DESC) AS RBI_RNK  "\
                "               , BB AS BB_CN "\
                "               , DENSE_RANK() OVER(ORDER BY BB DESC) AS BB_RNK "\
                "               , SB AS SB_CN "\
                "               , DENSE_RANK() OVER(ORDER BY SB DESC) AS SB_RNK "\
                "               , H2 AS H2_CN "\
                "               , DENSE_RANK() OVER(ORDER BY H2 DESC) AS H2_RNK "\
                "               , HIT AS HIT_CN "\
                "               , DENSE_RANK() OVER(ORDER BY HIT DESC) AS HIT_RNK "\
                "               , HR AS HR_CN "\
                "               , DENSE_RANK() OVER(ORDER BY HR DESC) AS HR_RNK "\
                "FROM  "\
                "( "\
                "SELECT HITTER, HITNAME, PITCHER, PITNAME "\
                "		, SUM(CASE WHEN HOW IN ('H1','H2','H3','HR','HI','HB','BB','IB','HP','KK','KN','KB' "\
                "					,'KW','KP','IN','OB','IP','XX','SH','SF','FC','GD','TP','GR','BN','FL','LL','IF','FF') THEN 1 "\
                "		ELSE 0 END) AS PA "\
                "		, SUM(CASE WHEN HOW IN ('H1','H2','H3','HR','HI','HB','GR','BN','FL','LL','IF','FF','KK','KN','KB','KW','KP','IP','XX','FC','GD','TP') THEN 1 " \
                "						ELSE 0 END) AS AB "\
                "		, SUM(CASE WHEN HOW IN ('H1','H2','H3','HR','HI','HB') THEN 1 "\
                "							ELSE 0 END) AS HIT "\
                "		, SUM(CASE WHEN HOW = 'H2' THEN 1 ELSE 0 END) H2 "\
                "		, SUM(CASE WHEN HOW = 'H3' THEN 1 ELSE 0 END) H3 "\
                "		, SUM(CASE WHEN HOW = 'HR' THEN 1 ELSE 0 END) HR "\
                "		, SUM(CASE WHEN PLACE IN ('E','R','H')  THEN 1 ELSE 0 END) RBI "\
                "		, SUM(CASE WHEN HOW = 'SH' THEN 1 ELSE 0 END) SH " \
                "		, SUM(CASE WHEN HOW = 'SB' THEN 1 ELSE 0 END) SB " \
                "		, SUM(CASE WHEN HOW = 'SF' THEN 1 ELSE 0 END) SF "\
                "		, SUM(CASE WHEN HOW IN ('BB', 'IB') THEN 1 ELSE 0 END) BB "\
                "		, SUM(CASE WHEN HOW = 'IB' THEN 1 ELSE 0 END) IB "\
                "		, SUM(CASE WHEN HOW = 'HP' THEN 1 ELSE 0 END) HBP "\
                "		, SUM(CASE WHEN HOW IN ('KK','KN','KB','KW','KP') THEN 1  "\
                "						ELSE 0 END) SO "\
                "		, SUM(CASE WHEN HOW IN ('GD','TP') THEN 1 ELSE 0 END)	DP "\
                "FROM baseball.gamecontapp "\
                "WHERE 1 = 1 "\
                "AND PITCHER = '%s' " \
                "AND HITTER = '%s' " \
                "GROUP BY HITTER, HITNAME "\
                ") AAA "\
                "ORDER BY HIT_RNK " % (pitcher, hitter)

        df  = pd.read_sql(sql, conn, coerce_float=False)
        df = df.set_index('HITTER')
        return df

    # consecutive hitter record
    def get_season_cons_hitter_record(self, hitter):
            conn = pymysql.connect(host=self._HOST, port=self._PORT, user=self._USER, password=self._PASSWORD, db=self._DB, charset='utf8mb4')
            sql = "SELECT GDAY, HITTER, HITNAME " \
                  "		, SUM(CASE WHEN HOW IN ('H1','H2','H3','HR','HI','HB') THEN 1 " \
                  "							ELSE 0 END) AS HIT " \
                  "		, SUM(CASE WHEN HOW = 'HR' THEN 1 ELSE 0 END) HR " \
                  "		, SUM(CASE WHEN HOW = 'SH' THEN 1 ELSE 0 END) SH " \
                  "FROM baseball.gamecontapp " \
                  "WHERE 1 = 1 " \
                  "AND GYEAR = YEAR(CURDATE()) " \
                  "AND HITTER = %s " \
                  "GROUP BY GMKEY, GDAY, HITTER, HITNAME " \
                  "ORDER BY GDAY DESC " % hitter
            df  = pd.read_sql(sql, conn)
            return df

    def get_hitter_record_df(self, hitter):
            conn = pymysql.connect(host=self._HOST, port=self._PORT, user=self._USER, password=self._PASSWORD, db=self._DB, charset='utf8mb4')
            sql = "SELECT * " \
                  "FROM  " \
                  "( " \
                  "SELECT A.PCODE, B.NAME, A.GAMENUM " \
                  "               , RBI " \
                  "               , DENSE_RANK() OVER(ORDER BY RBI DESC) AS RBI_RNK " \
                  "               , BB " \
                  "               , DENSE_RANK() OVER(ORDER BY BB DESC) AS BB_RNK " \
                  "					     , SB " \
                  "               , DENSE_RANK() OVER(ORDER BY SB DESC) AS SB_RNK " \
                  "               , SH " \
                  "               , DENSE_RANK() OVER(ORDER BY SH DESC) AS SH_RNK " \
                  "               , H2 " \
                  "               , DENSE_RANK() OVER(ORDER BY H2 DESC) AS H2_RNK " \
                  "               , H3 " \
                  "               , DENSE_RANK() OVER(ORDER BY H3 DESC) AS H3_RNK " \
                  "               , HIT " \
                  "               , DENSE_RANK() OVER(ORDER BY HIT DESC) AS HIT_RNK " \
                  "               , HR " \
                  "               , DENSE_RANK() OVER(ORDER BY HR DESC) AS HR_RNK " \
                  "               , RUN " \
                  "               , DENSE_RANK() OVER(ORDER BY RUN DESC) AS RUN_RNK " \
                  "               , KK " \
                  "               , DENSE_RANK() OVER(ORDER BY KK DESC) AS KK_RNK " \
                  "               , ERR " \
                  "               , DENSE_RANK() OVER(ORDER BY ERR DESC) AS ERR_RNK " \
                  "               , ROUND(C.HRA, 3) AS HRA " \
                  "               , DENSE_RANK() OVER(ORDER BY C.HRA DESC) AS HRA_RNK " \
                  "FROM baseball.battotal A " \
                  ", baseball.person B " \
                  ", (SELECT CASE  " \
                  "			WHEN GAMENUM > B.AVG_GAMENUM THEN HRA " \
                  "			ELSE 0 " \
                  "		 END AS HRA " \
                  "	  , A.PCODE " \
                  "FROM baseball.battotal A,  " \
                  "     (SELECT ROUND(AVG(GAMENUM)) AS AVG_GAMENUM FROM baseball.battotal) B " \
                  ") C " \
                  "WHERE A.GYEAR = YEAR(CURDATE()) " \
                  "AND A.PCODE = B.PCODE " \
                  "AND A.PCODE = C.PCODE " \
                  ") AAA " \
                  "WHERE PCODE = '%s' " % hitter

            df = pd.read_sql(sql, conn)
            df = df.set_index('PCODE')
            return df

    def get_first_ball_info(self, hitter):
        result_list = []
        conn = pymysql.connect(host=self._HOST, port=self._PORT, user=self._USER, password=self._PASSWORD, db=self._DB, charset='utf8mb4')
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
                    "WHERE HITTER = %s " % hitter
        df = pd.read_sql(query, conn)
        df_to_dict = df.to_dict('records')
        if df_to_dict:
            result_list.extend(df_to_dict)

        conn.close()
        return result_list

    def get_total_hitter_record(self, live_dict):
        conn = pymysql.connect(host=self._HOST, port=self._PORT, user=self._USER, password=self._PASSWORD, db=self._DB,
                               charset='utf8mb4')
        param = live_dict

        result_list = []
        query = "SELECT SUBJECT, OPPONENT, LEAGUE, GYEAR, HITTER, HITNAME, PITCHER, PITNAME, PITTEAM, PITTEAM_NAME "\
                            "					, PA, STATE, STATE_SPLIT, RESULT, RNK "\
                            "FROM baseball.accum_record_hitter "\
                            "WHERE HITTER = '{hitter}' "\
                            "AND GYEAR IN ('NA', year(curdate())) "\
                            "AND PITCHER IN ('NA', '{pitcher}') "\
                            "AND PITTEAM IN ('NA', '{pitteam}') "\
                            "AND STATE_SPLIT IN ('BASIC', 'VERSUS', '{score}', '{base}') ".format(**param)

        df = pd.read_sql(query, conn)
        df_to_dict = df.to_dict('records')
        if df_to_dict:
            result_list.extend(df_to_dict)

        conn.close()
        return result_list

    def get_today_hitter_record(self, gmkey, hitter):
        result = None
        conn = pymysql.connect(host=self._HOST, port=self._PORT, user=self._USER, password=self._PASSWORD, db=self._DB,
                               charset='utf8mb4')

        query ="SELECT HITNAME, PA, AB, HIT, HR, RBI, BB, KK "\
                            "FROM "\
                            "( "\
                            "	SELECT SUM(CASE WHEN HOW IN ('H1','H2','H3','HR','HI','HB','BB','IB','HP','KK','KN','KB' "\
                            "						,'KW','KP','IN','OB','IP','XX','SH','SF','FC','GD','TP','GR','BN','FL','LL','IF','FF') THEN 1 "\
                            "											ELSE 0 END) AS PA "\
                            "						, SUM(CASE WHEN HOW IN ('H1','H2','H3','HR','HI','HB','GR','BN','FL','LL','IF','FF', "\
                            "						'KK','KN','KB','KW','KP','IP','XX','FC','GD','TP') THEN 1 "\
                            "										ELSE 0 END) AS AB "\
                            "						, SUM(CASE WHEN HOW IN ('H1','H2','H3','HR','HI','HB') THEN 1 ELSE 0 END) AS HIT "\
                            "						, SUM(CASE WHEN HOW = 'HR' THEN 1 ELSE 0 END) AS HR "\
                            "						, SUM(CASE WHEN PLACE IN ('E','R','H')  THEN 1 ELSE 0 END) AS RBI "\
                            "						, SUM(CASE WHEN HOW IN ('BB', 'IB') THEN 1 ELSE 0 END) AS BB "\
                            "						, SUM(CASE WHEN HOW = 'KK' THEN 1 ELSE 0 END) AS KK "\
                            "						, HITNAME "\
                            "	FROM baseball.gamecontapp_all "\
                            "	WHERE HITTER = '{1}' "\
                            "	AND GMKEY = '{0}' "\
                            ") TODAY "\
                            "WHERE PA > 0 ".format(gmkey, hitter)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        return result

    def get_hitter_continuous_record(self, hitter):
        conn = pymysql.connect(host=self._HOST, port=self._PORT, user=self._USER, password=self._PASSWORD, db=self._DB,
                               charset='utf8mb4')

        result_list = []
        query = "SELECT GMKEY, GDAY, HOW, PLACE, HITTER, HITNAME "\
                            "FROM  baseball.gamecontapp "\
                            "WHERE HITTER = '{0}' "\
                            "AND GMKEY LIKE '{1}%'"\
                            "ORDER BY GMKEY DESC, SERNO DESC".format(hitter, datetime.now().year)

        df = pd.read_sql(query, conn)
        df_to_dict = df.to_dict('records')
        if df_to_dict:
            result_list.extend(df_to_dict)

        conn.close()
        return result_list

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

    def call_update_state_rank(self, data_dict):
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

        pass

if __name__ == "__main__":
    record = Record()

    # hitter,hitteam,pitcher,pitteam,state,score,base
    live_dict = {'hitter': 78224, 'hitteam': 'OB', 'pitcher': 79140, 'pitteam': 'LG', 'state': 'HR', 'score': '0D', 'base': '1B'}
    record_df = record.get_total_hitter_record(live_dict)
    print(record_df)