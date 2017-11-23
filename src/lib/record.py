import pandas as pd
import pymysql.cursors

host = 'localhost'
user = 'root'
password = 'lab2ai64'
db = 'baseball'
port = 3307
file = None

def get_df_season_pitcher_record(pitcher):
    # print('get_this_season_pitcher_record')
    result = pd.DataFrame()
    return result

def get_df_season_hitter_vs_pitcher(hitter, pitcher):
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset='utf8mb4')
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
def get_season_cons_hitter_record(hitter):
        conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset='utf8mb4')
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

def get_df_season_hitter_record(hitter):
        conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset='utf8mb4')
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