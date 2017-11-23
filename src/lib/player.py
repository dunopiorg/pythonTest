class Player:
    player_info = {}
    this_season_record = {}

    def __init__(self, name):
        self.name = name
        self.getPlayerInfo()

    def get_player_info(self):
        print('get_player_info')

    def set_this_season_record(self, this_season_record):
        self.this_season_record = this_season_record

class Hitter(Player):

    def get_hitter_info(self):
        print('get_hitter_info')

class Pitcher(Player):

    def get_pitcherr_info(self):
        print('get_pitcher_info')
