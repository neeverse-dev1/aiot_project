import json
import sys
import time
import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials



GDOCS_OAUTH_JSON       = 'thermal-shuttle-462907-n3-67e56bbfe64c.json'

# Google Docs spreadsheet name.
GDOCS_SPREADSHEET_NAME = 'https://docs.google.com/spreadsheets/d/1e5729Xo60oVCM6nnpcjSVp3KTZp8UeVy2UosJTZ0C8s/edit?usp=sharing'
GDOCS_SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1e5729Xo60oVCM6nnpcjSVp3KTZp8UeVy2UosJTZ0C8s/edit?usp=sharing'

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS      = 30


def get_gspread_sheet_data(sheet):
    """
        get gspread_sheet_data
    """
    ret = False
    ret_list = []

    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive',
    ]
    json_file_name = GDOCS_OAUTH_JSON
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        json_file_name, scope)
    gc = gspread.authorize(credentials)
    spreadsheet_url = GDOCS_SPREADSHEET_URL

    doc = gc.open_by_url(spreadsheet_url)

    worksheet = doc.worksheet(sheet)

    # range
    # range_list = worksheet.range('A1:j2')

    # all list
    try:
        ret_list = worksheet.get_all_values()
        ret = True
    except Exception as e:
        print('Error : ' + str(e))
    return ret, ret_list

def delete_gspread_sheet_data(sheet):
    """
        get gspread_sheet_data
    """
    ret = False
    ret_list = []

    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive',
    ]
    json_file_name = GDOCS_OAUTH_JSON
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        json_file_name, scope)
    gc = gspread.authorize(credentials)
    spreadsheet_url = GDOCS_SPREADSHEET_URL

    doc = gc.open_by_url(spreadsheet_url)

    worksheet = doc.worksheet(sheet)

    try:
        worksheet.clear()
        ret = True
    except Exception as e:
        print('Error : ' + str(e))
    return ret, ret_list



def update_gspread_sheet_data(sheet, data):
    """
        get gspread_sheet_data
    """
    ret = False
    ret_list = []

    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive',
    ]
    json_file_name = GDOCS_OAUTH_JSON
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        json_file_name, scope)
    gc = gspread.authorize(credentials)
    spreadsheet_url = GDOCS_SPREADSHEET_URL

    doc = gc.open_by_url(spreadsheet_url)

    worksheet = doc.worksheet(sheet)

    try:
        
        # worksheet.update('A1:B2', [[1, 2], [3, 4]])
        # worksheet.update_cell(1, 2, 'Gorio')
        for i, x in enumerate(data[1]):
            worksheet.update_cell(data[0], i+1, x)
        ret = True
    except Exception as e:
        print('Error : ' + str(e))
    return ret, ret_list


if __name__ == "__main__":

    # print(get_gspread_sheet_data('dht11_sensors'))
    delete_gspread_sheet_data('dht11_sensor')
    update_gspread_sheet_data('dht11_sensor', [1, ['2025-06-16 15:30:22', '23', '50']])

