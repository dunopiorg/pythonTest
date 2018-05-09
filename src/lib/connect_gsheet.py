import pandas as pd
import gspread
import config
from oauth2client.service_account import ServiceAccountCredentials


class Gspread(object):
    def __init__(self):
        self.scope = ['https://spreadsheets.google.com/feeds']
        self.creds = ServiceAccountCredentials.from_json_keyfile_dict(config.GSHEET_DICT, self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open_by_url('https://docs.google.com/spreadsheets/d/18dxnF4RC3xr77m6HQsx8mqayUcNYyaDVim3vi_lxK4M/edit?usp=sharing')
        self.worksheet = self.sheet.get_worksheet(0)

        self.list_of_hashes = self.worksheet.get_all_records()
        if self.list_of_hashes:
            self.df_template = pd.DataFrame(self.list_of_hashes)

    def get_df_template(self):
        return self.df_template

"""
# insert, update, delete 
sheet.row_values(1)
sheet.col_values(1)
sheet.cell(1, 1).value
sheet.update_cell(1, 1, "I just wrote to a spreadsheet using Python!")
row = ["I'm","inserting","a","row","into","a,","Spreadsheet","with","Python"]
index = 1
sheet.insert_row(row, index)
sheet.delete_row(1)
sheet.row_count
"""