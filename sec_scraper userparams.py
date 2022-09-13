from dateutil import parser
from datetime import datetime
from contextlib import closing
import sqlite3
from sqlite3 import Error
import time
import requests as req
import requests_random_user_agent as ragent
import pandas as pd
from bs4 import BeautifulSoup as bs4
import os, sys
import re

# ---------------------------------------------
# Refactor all of the below into a Class.
# company_CIKS = ['1018724', '1318605', '789019']
# filing_types = ['10-k']  # '10-k', '10-Q', '8-k', etc
# db_name = 'edgar.db'
# folder_path = r"/home/rocket/Code/Projects/Py/SECdb/sqlite/"  # convert to win64 'C:\'
# db_path = f"{folder_path}/{db_name}"

# start_date = '2020-01-01'
# end_date = '2022-08-31'
#---------------------------------------------


class UserParams:

    @classmethod
    def __init__(self):
        self.company_CIKS = []
        self.filing_types = []
        self.db_name = 'edgar.db'
        self.folder_path = r"/home/rocket/Code/Projects/Py/SECdb/sqlite/"
        self.db_path = ''
        self.start_date = '2020-01-01'
        self.end_date = '2022-08-31'
        self.error_messages = []


class DB_Connection:
    """Initialize obj attrs"""

    def __init__(self, db_name, folder_path, db_path):
        self.db_name = db_name
        self.folder_path = folder_path

    def create_folder(self):
        """ Create a directory for the DB file if the directory doesnt exist. """
        if not os.path.exists(UserParams.folder_path):
            os.makedirs(UserParams.folder_path)
            print( f'Successfully created the new folder path {UserParams.folder_path}')
        else:
            print(f'Folder path {UserParams.folder_path} already exists.')

    # Open connection to the db, if the connection fails then abort.
    # If db file doesn't exist, automatically create itself.
    @classmethod
    def open_con(cls, db_path):
        try:
            cls.conn = sqlite3.connect(db_path)
            print(f'Successfully connected to the {db_path} ')
            return cls.conn
        except sqlite3.Error as e:
            print(
                f'Error occured, unable to connect to the {db_path} database.')
            print(e)
            UserParams.error_messages.append(e)
            return None

    @classmethod
    def close_conn(cls):
        try:
            cls.conn.commit()
            print('Comitted transactions.')
            cls.conn.close()
            print('Closing all databse connections')
        except Exception as e:
            print(f'Unable to close database connection.\n{e}')


class Filing_Links:
    """a"""

    def __init__(self):
        UserParams.filing_types = [
            item.upper() for item in UserParams.filing_types
        ]
        # self.company_CIKS = company_CIKS
        # # Capitalize the letters of the forms, by default sqlite is case sensitive.
        # self.filing_types = [item.upper() for item in filing_types]
        # self.start_date = start_date
        # self.end_date = end_date

    # Get all available filings for the specified CIKS and their respective links.
    def Get_FLinks(self):
        try:
            for Company_CIK_Number in UserParams.company_CIKS:
                for Filing_Type in UserParams.filing_types:
                    # define the params dict
                    filing_params = {
                        'action': 'getcompany',
                        'CIK': Company_CIK_Number,
                        'type': Filing_Type,
                        'dateb': '',
                        'owner': 'exclude',
                        'start': '',
                        'output': '',
                        'count': '100'
                    }
                    # req the url & parse response.
                    response = req.get(
                        url=r'https://www.sec.gov/cgi-bin/browse-edgar',
                        params=filing_params)

                    # add 1/10th sec delay to comply w/ SEC.gov's 10req/s limit (see robots.txt)
                    time.sleep(0.1)
                    soup = bs4(response.content, 'html.parser')
                    # Find doc table that contains filing info
                    main_table = soup.find_all('table', class_='tableFile2')
                    # base url will be used to construct doc link urls
                    sec_base_url = r"https://www.sec.gov"
                    Company_Name_path = str(
                        soup.find('span', {"class": "companyName"}))
                    if Company_Name_path != None:
                        try:
                            Company_Name = re.search(
                                '<span class="companyName">(.*)<acronym title',
                                Company_Name_path).group(1)
                        except AttributeError:
                            print(f"Couldn't find company name, \
                                       assigning NULL value to company name.")
                            Company_Name = None
                    # loop through ea row of the table & extract filing numbers, links, etc.
                    for row in main_table[0].find_all('tr'):
                        # find all of the rows under the 'td' element.
                        cols = row.find_all("td")
                        # if no info was detected, move onto the next row.
                        if len(cols) != 0:
                            # get the text from the table.
                            Filing_Type = cols[0].text.strip()
                            Filing_Date = cols[3].text.strip()
                            Filing_Number = cols[4].text.strip()
                            Filing_Number = ''.join(e for e in Filing_Number
                                                    if e.isalnum())
                            # Get the URL path to the filing number.
                            filing_number_path = cols[4].find('a')
                            if filing_number_path != None:
                                Filing_Number_Link = sec_base_url + filing_number_path[
                                    'href']
                            else:
                                break
                            # Get the URL path to the doc.
                            document_link_path = cols[1].find(
                                'a', {
                                    'href': True,
                                    'id': 'documentsbutton'
                                })
                            if document_link_path != None:
                                Document_Link = sec_base_url + document_link_path[
                                    "href"]
                            else:
                                Document_Link = None

                            try:
                                Account_Number = cols[2].text.strip()
                                Account_Number = re.search(
                                    'Acc-no:(.*)(34 Act)',
                                    Account_Number).group(1)
                                Account_Number = ''.join(
                                    e for e in Account_Number if e.isalnum())
                            except Exception as e:
                                """
                                Add break if you dont want empty rows of account numbers. If account numbers arent
                                present, the interactive document link wont be available. If the interactive link
                                  isnt present, we wont be able to extract the individual tables containing
                                   financial statements.
                                """
                                Account_Number = None
                                print(f'Couldnt retrieve the account number, \
                                        assigning NULL value.\n{e}')

                        # Get the URL path to the interactive documents
                        interact_data_path = cols[1].find(
                            'a', {
                                'href': True,
                                'id': 'interactiveDataBtn'
                            })
                        if interact_data_path != None:
                            Interactive_Data_Link = sec_base_url + interact_data_path[
                                "href"]
                            # If the interactive data link exists, then so does the FilingSummary.xml link
                            Xml_Summary = Document_Link.replace(f"{Account_Number}", '')\
                               .replace('-', '')\
                               .replace('index.htm', '/FilingSummary.xml')
                        else:
                            # break ...?
                            Interactive_Data_Link = None
                            Xml_Summary = None

                        self.info_to_sql(Company_Name, Company_CIK_Number,
                                         Account_Number, Filing_Type,
                                         Filing_Number, Filing_Date,
                                         Document_Link, Interactive_Data_Link,
                                         Filing_Number_Link, Xml_Summary)
        except Exception as e:
            print(f'Couldnt retrieve the table containing the necessary info. \
                      \nAborting the program.\nIf index list is out of range, \
                   that you entered the correct CIK number(s).')
            print(e)
            UserParams.error_messages.append(e)
            return None

    # Migrate the df containing the filing & document links to a local sqlite db.
    def info_to_sql(self, Company_Name, Company_CIK_Number, Account_Number,
                    Filing_Type, Filing_Number, Filing_Date, Document_Link,
                    Interactive_Data_Link, Filing_Number_Link, Xml_Summary):

        with DB_Connection.open_con(UserParams.db_path) as conn:
            try:
                with closing(conn.cursor()) as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS filing_list (
                        filing_number integer PRIMARY KEY,
                        account_number integer,
                        company_name text NOT NULL,
                        cik integer NOT NULL,
                        filing_type text NOT NULL,
                        filing_date text NOT NULL,
                        document_link_html TEXT NOT NULL,
                        filing_number_link TEXT NOT NULL,
                        interactive_dash_link TEXT,
                        xml_summary TEXT
                        )
                        ;""")
            except ValueError as e:
                print(
                    f'Error occured while attempting to create the filing_list table.\
                        \nAborting the program.')
                print(e)
                UserParams.error_messages.append(e)
                return None
            else:
                print(f"Successfully created the table.")
                print(
                    f"Migrating info for filing number {Filing_Number} to the SQL table..."
                )
                try:
                    # Insert or IGNORE will insert a record if it doesnt duplicate an existing record.
                    with closing(conn.cursor()) as cursor:
                        cursor.execute(
                            """
                        INSERT or IGNORE INTO filing_list (
                        filing_number,
                        account_number,
                        company_name,
                        cik,
                        filing_type,
                        filing_date,
                        document_link_html,
                        filing_number_link,
                        interactive_dash_link,
                        summary_link_xml
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """,
                            (Filing_Number, Account_Number, Company_Name,
                             Company_CIK_Number, Filing_Type, Filing_Date,
                             Document_Link, Filing_Number_Link,
                             Interactive_Data_Link, Xml_Summary))
                except ValueError as e:
                    print(
                        f'Error occured while attempting to insert values into the filing_list table.\n{e}'
                    )

        DB_Connection.close_con()

    # Extract individual table links to financial statements, supplementary data tables, etc (everything?)
    def get_table_links(self):
        dfs = []
        with DB_Connection.open_con(UserParams.db_path) as conn:
            try:
                for Company_CIK_Number in UserParams.company_CIKS:
                    for Filing_Type in UserParams.filing_types:
                        df = pd.read_sql_query(
                            """
                            SELECT filing_number, xml_summary
                            FROM filing_list
                            WHERE xml_summary IS NOT NULL
                            AND filing_type = ?
                            AND cik = ?
                            AND filing_date BETWEEN ? AND ?
                            """,
                            con=conn,
                            params=(Filing_Type, Company_CIK_Number,
                                    self.start_date, self.end_date))
                        dfs.append(df)
                df_query2 = pd.concat(dfs)

            except Exception as e:
                print(
                    f"Error occured while attempting to retireve data from filing_list table.\n{e}"
                )
                print(e)
                UserParams.error_messages.append(e)
                return None

            # If the df is empty, exit.
            if len(df_query2) == 0:
                error_msg = 'Dataframe is empty. (Error in the get_table_links method.) '
                print(error_msg)
                UserParams.error_messages.append(error_msg)
                return None
            try:
                with closing(conn.cursor()) as cursor:
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS individual_report_links (
                    filing_number integer,
                    short_name text,
                    report_url text,
                    FOREIGN KEY(filing_number) REFERENCES filing_list(filing_number),
                    UNIQUE(report_url)
                    )
                    ;""")
            except ValueError as e:
                print(
                    f"Error occured while attempting to create individual_report_links table.\n{e}"
                )
                print(e)
                UserParams.error_messages.append(e)
                return None

            # Extract the tables name and its respective URL
            # Currently, there isnt a function/method(?) to extract data from the .xml extension
            for filing_number, xml_summary in df_query2.itertuples(
                    index=False):
                resp_2 = req.get(xml_summary).content
                time.sleep(0.1)
                soup_2 = bs4(resp_2, 'lxml')
                for item in soup_2.find_all('report')[:-1]:
                    if item.shortname:
                        Short_Name = item.shortname.text
                        # Remove special/unicode/ascii characters && whitespace end of string
                        Short_Name = re.sub(r"[^a-zA-Z0-9]+", ' ', Short_Name)
                        Short_Name = Short_Name.rstrip()
                    else:
                        print(f'Short name couldnt be retrieved.')
                        Short_Name = None
                    # some tables come only in xml form...
                    if item.htmlfilename:
                        Report_Url = xml_summary.replace(
                            'FilingSummary.xml', item.htmlfilename.text)
                    elif item.xmlfilename:
                        Report_Url = xml_summary.replace(
                            'FilingSummary.xml', item.xmlfilename.text)
                    else:
                        print(
                            f'URL to the individual report couldnt be retrieved.'
                        )
                        Report_Url = None

                    print(Short_Name)
                    print(Report_Url)
                    print(filing_number)
                    print('*' * 50 + ' Inserting values into the table .... ' +
                          '*' * 50)

                    try:
                        with closing(conn.cursor()) as cursor:
                            cursor.execute(
                                """
                            INSERT OR IGNORE INTO individual_report_links (
                            filing_number,
                            short_name,
                            report_url
                            ) VALUES (?, ?, ?) """, (filing_number, Short_Name, Report_Url))
                    except ValueError as e:
                        print(
                            f'Error occured while attempting to insert values into \
                                  the individual_report_links table.\nAborting the program.\n{e}')
                        print(e)
                        UserParams.error_messages.append(e)
                        return None

    DB_Connection.close_con()


class Extract_Data:

    def __init__(self):
        self.df_xml = None

    # extract table data from a xml
    def html_table_extractor(self, report_url):
        # Note to self, .text is unicode u"", .content is in byes b""
        response_xml = req.get(report_url).content
        time.sleep(0.1)
        xml_soup = bs4(response_xml, 'lxml')
        table = xml_soup.find_all('table')
        if table:
            try:
                print("Insert table data into the dataframe.")
                self.df_xml = pd.read_html(str(table))[0]
                self.df_xml = self.df_xml.replace({'\$': ''}, regex = True)\
                    .replace({'\)':''}, regex = True)\
                    .replace({'\(':''}, regex = True)\
                    .replace({'\%':''}, regex = True)\
                    .replace({' ','', 1}, regex = True)

            except Exception as e:
                print(f'Error occurred while attempting to insert \
                        table data into the DataFrame.\n{e}')
        else:
            print(f'No table detected for {report_url}.')

    # Retrieve necessary information to extract data from the table's URL.
    def get_tables(self):
        dfs = []
        with DB_Connection.open_con(UserParams.db_path) as conn:
            for company_CIK in filings1.company_CIKs:
                for filing_type in filings1.filingstypes:
                    try:
                        df = pd.read_sql_query("""
                            SELECT a.filing_number,
                                   a.company_name,
                                   a.filing_type,
                                   a.filing_date,
                                   b.short_name,
                                   b.report_url
                            FROM filing_list a
                            INNER JOIN individual_report_links b
                            ON a.filing_number = b.filing_number
                            WHERE b.report_url LIKE '%.htm%'
                            AND a.cik = ?
                            AND a.filing_type = ?
                            AND a.filing_date BETWEEN ? AND ?
                            ORDER by filing_date DESC
                            LIMIT ?
                            """,
                                               con=conn,
                                               params=(company_CIK,
                                                       filing_type,
                                                       filings1.start_date,
                                                       filings1.end_date, 10))
                        dfs.append(df)
                    except ValueError as e:
                        print(
                            f"Error occured while attempting to retrieve data \
                                from the SQL db.\nAborting the program.\n{e}")
                        sys.exit(1)

            df_query1 = pd.concat(dfs)
            # if the df is empty, terminate the program.
            if len(df_query1) == 0:
                print( 'Dataframe is empty, aborting the program.\nAborting the program')
                sys.exit(1)
            else:
                # if max recursion error occurs, increase recursion limit. sys.setrecursionlimit(25000)
                pass
            for filing_number, company_name, filing_type, filing_date, short_name, report_url in df_query1.itertuples(
                    index=False):
                print(f'Processing {short_name} table at {report_url}.')

                if report_url.endswith('.htm'):
                    try:
                        self.html_table_extractor(report_url)
                    except ValueError as e:
                        print(
                            f'Couldnt retrieve the table for filing number {filing_number} at {report_url}\n{e}'
                        )
                        break
                    else:
                        try:
                            # want to name the table with a unique table name for easy reference
                            table_name = filing_type + filing_date + '_' + \
                                         short_name.replace( ' ', '_') + '_' + str(filing_number)
                            # remove all special chars (unicode, ascii) except '_'
                            table_name = re.sub(r"[^a-zA-Z0-9]+", '_',
                                                table_name)
                            print(
                                f'Inserting data from the dataframe into SQL table {table_name}'
                            )
                            # check to see if the table already exists in db to avoid duplication
                            with closing(conn.cursor()) as cursor:
                                cursor.execute(f""" SELECT count(name)
                                               FROM sqlite_master
                                               WHERE type='table' AND name= '{table_name}' """
                                               )  # SQL injection much?
                                # if count is 1 -> table exists
                                if cursor.fetchone()[0] == 1:
                                    print(
                                        f'Table {table_name} already exists.')
                                else:
                                    # Write records that are stored in the Dataframe into a SQL server database.
                                    self.df_xml.to_sql(con=conn,
                                                       name=table_name,
                                                       schema='SCHEMA',
                                                       index=False,
                                                       if_exists='fail')
                        except ValueError as e:
                            print(
                                f"Couldnt migrate the {short_name} table to the SQL database.\n{e}"
                            )
                elif report_url.endswith('.xml'):
                    print(
                        f'.xml extension link detected. Unable to process the table.\
                        \n.xml extension link support will be developed in the future.')
                else:
                    print(
                        f'Table for filing number {filing_number} couldnt be detected.'
                    )
        DB_Connection.close_conn()

    # Normalizing data.
    def transpose(self):

        db2_path = UserParams.db_path.replace('.db', '_transposed;db')
        with DB_Connection.open_con(UserParams.db_path) as conn:
            try:
                df_table_list = pd.read_sql_query(
                    """
                    SELECT name AS table_name
                    FROM sqlite_master
                    WHERE type='table'
                    """, conn)
            except ValueError as e:
                print(f'Couldnt retrieve table list.\n{e}')
            for row in df_table_list.itertuples(index=False):
                try:
                    df_table = pd.read_sql_query(
                        """ SELECT * FROM "{}" """.format(row.table_name), con=conn)
                except ValueError as e:
                    print(f'couldnt read table {table_name}.\n{e}')
                else:
                    try:
                        while row.table_name not in ['filing_list', 'individual_report_links']:
                            # remove dup rows w/ same values
                            df_table = df_table.drop_duplicates()
                            # tranpose da pandas df!
                            df_table = df_table.T
                            # transform that first rows into the header!
                            df_table.columns = df_table.iloc[0]
                            df_table = df_table[1:]
                            # remove special chars again {unicode, ascii}, replace empty spaces with _
                            df_table = df_table.rename(
                                columns=lambda x: re.sub('\W+', '_', str(x)))
                            df_table.columns = df_table.columns.str.strip('_')
                            df_table.columns = df_table.columns.str.lower('_')
                            # convert idx of df into a col
                            df_table.reset_index(level=0, inplace=True)
                            # Format that dirty date col
                            try:
                                date_list = []
                                for item in df_table.iloc[:, 0]:
                                    match = re.search('\D{3}. \d{2}, \d{4}',
                                                      item)
                                    if match is not None:
                                        # .strftime removes the timestamp
                                        date = parser.parse(
                                            match.group()).strftime("%Y-%m-%d")
                                        date_list.append(date)
                                    else:
                                        date_list.append(item)
                                df_table.rename(
                                    columns={df_table.columns[0]: 'date'},
                                    inplace=True)
                                df_table['date'] = date_list
                                print('Successfully formatted the date.')
                            except Exception as e:
                                df_table.rename(
                                    columns={df_table.columns[0]: 'name'},
                                    inplace=True)
                                print(e)

                            # convert rows to numeric dtypes (ints, floats)
                            df_table.replace(',', '', regex=True, inplace=True)
                            df_table = df_table.apply(pd.to_numeric,
                                                      errors='ignore')
                            # rename duplicate rows w/ same name
                            if any(df_table.columns.duplicated()):
                                print(
                                    'Duplicate column name detected.\nRenaming the duplicate column name.  '
                                )
                                columns_series = pd.Series(df_table.columns)
                                for dup in columns_series[
                                        columns_series.duplicated()].unique():
                                    columns_series[columns_series[
                                        columns_series ==
                                        dup].index.values.tolist()] = [
                                            dup + '.' +
                                            str(i) if i != 0 else dup
                                            for i in range(
                                                sum(columns_series == dup))
                                        ]
                                    df_table.columns = columns_series
                                break
                    except Exception as e:
                        print(f'Couldnt transpose the table :|.\n{e}')
                    else:
                        with DB_Connection.open_con(db2_path) as conn2:
                            # chk to see if table already exists in db
                            with closing(conn2.cursor()) as cursor:
                                cursor.execute(f""" SELECT count(name)
                                               FROM sqlite_master
                                               WHERE type='table' AND name= '{row.table_name}'"""
                                        )  # SQL INJECTOIN MUCH
                                # if count is 1, then table exists
                                if cursor.fetchone()[0] == 1 and row.table_name not in [
                                        'filing_list',
                                        'individual_report_links'
                                ]:
                                    print( f'Table {row.rable_name} already exists.')
                                else:
                                    try:
                                        print( f'Connected to {db2_path} database.')
                                        print( f'Inserting data from the dataframe into SQL table {row.table_name}')
                                        # write records that are stored in the df into sql db
                                        df_table.to_sql(con=conn2,
                                                        name=row.table_name,
                                                        schema='SCHEMA',
                                                        if_exists='replace',
                                                        index=False)
                                    except Exception as e:
                                        print( f'Couldnt migrate the {row.table_name} \
                                                 table to the normalized SQL db.\n{e}')
        DB_Connection.close_con()


user_one = UserParams()
connection1 = DB_Connection()
filings1 = Filing_Links()
data1 = Extract_Data
# connection1 = DB_Connection(db_name, folder_path, db_path)
# connection1.create_folder()

# filings1 = Filing_Links(company_CIKS, filing_types, start_date, end_date)
# filings1.Get_FLinks()
# filings1.get_table_links()

# data1 = Extract_Data()
# data1.get_tables()
# data1.transpose()