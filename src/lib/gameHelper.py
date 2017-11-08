from lib import DBConnection as db

class GameHelper():
    # Setting Mysql Connector

    def __init__(self):
        self.MySqlHost = 'localhost'
        self.MySqlUser = 'root'
        self.MySqlPw = '0000'
        self.MySqlDB = 'baseball'
        self.LiveData = None
        self.CondTuple = None
        self.setCondDict()
        # TEST를 위한 변수
        self.currRowNum = 0

    def setCondDict(self):
        dbMyConn = db.MySqlConnector(host=self.MySqlHost, user=self.MySqlUser, pw=self.MySqlPw, db=self.MySqlDB)
        query = "select HOW, CONDITIONS from baseball.how_cond"
        self.CondTuple = dbMyConn.select(query, True)

    def getLiveData(self):
        dbMyConn = db.MySqlConnector(host=self.MySqlHost, user=self.MySqlUser, pw=self.MySqlPw, db=self.MySqlDB)
        query = "select * from baseball.livetext_score_mix order by seqNo limit 1"
        self.LiveData = dbMyConn.select(query, True)[0]
        return self.LiveData

    # Live가 아닌 Local Test를 위한 함수. getLiveData()로 대체될 것.
    def testLiveData(self):
        dbMyConn = db.MySqlConnector(host=self.MySqlHost, user=self.MySqlUser, pw=self.MySqlPw, db=self.MySqlDB)
        query = "select * from baseball.livetext_score_mix order by seqNo"
        self.LiveData = dbMyConn.select(query, True)
        return self.LiveData

    def getHowInfo(self, how):
        result = None
        for condDict in self.CondTuple:
            if how in condDict.values():
                condList = condDict['CONDITIONS'].split(',')
                for cond in condList:
                    method = getattr(self, cond)
                    method()
        return result

    # [HR]점수차 변화 : 리드, 역전, 동점, 추적, 도망
    def getScoreStatus(self):
        print('HR~~~~!')

    # [HR]득점 종류 : 안타, 홈런, 희생FL, 실책, 내야 땅볼 등
    def getKindOfScore(self):
        live_data_dict = self.LiveData[self.currRowNum]
        return {'kindOfScore': live_data_dict['HOW']}

    # [HR]주자 상황 : no, 1, 1-2or2-3, 1-2-3
    # return 0, 1, 2, 3
    def getBaseState(self):
        live_data_dict = self.LiveData[self.currRowNum]
        count = 0
        base_list = ['base1', 'base2', 'base3']

        for s in base_list:
            if live_data_dict[s] > 0:
                count += 1
        return {'baseState': count}

    # [HR]리그 종류에 대한 선수 기록
    def getPlayerLeague(self):
        print('BH~~~~!')

    # [HR]상대선수와의 기록
    def getVSPitcher(self):
        print('BH2~~~~!')

    # WPA 정보
    # return currWPA(후), prevWPA(전), varWAP(변화)
    def getWPA(self):
        live_data_dict = self.LiveData[self.currRowNum]
        dbMyConn = db.MySqlConnector(host=self.MySqlHost, user=self.MySqlUser, pw=self.MySqlPw, db=self.MySqlDB)
        query = "select BEFORE_WE_RT, AFTER_WE_RT, WPA_RT "\
                      " from baseball.ie_record_matrix "\
                      "where GAMEID = %s "\
                      "and GYEAR = %s "\
                      "and SEQNO = %s "\
                      "limit 1"
        query = query % (live_data_dict['gameID'], live_data_dict['GYEAR'], live_data_dict['seqNO'])
        result = dbMyConn.select(query, True)
        return result[0]