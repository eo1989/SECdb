import requests as req
import requests_random_user_agent as rrua


class UserParameters:
    @classmethod
    def __init_(self):
        self.company_CIKs = []  # find company's CIK number at https://www.sec.gov/edgar/searchedgar/companysearch.html
        self.filings_types = []  # '10-K', '10-Q', '8-K'
        self.db_name = 'edgar.db'  # db should be automatically created
        self.folder_path = '/home/rocket/Code/Projects/Py/SECdb/sqlite/db'
        self.db_path = ''
        self.start_date = '2020-01-01'
        self.end_date = '2022-08-10'
        self.error_messages = []

