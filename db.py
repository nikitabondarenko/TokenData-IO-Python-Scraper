import sqlite3
import time
import datetime

class Database:

    _path = 'database.db'
    _conn = None
    _c = None


    def __init__(self):
        self._conn = sqlite3.connect(self._path)
        self._c = self._conn.cursor()
        self._create_tables()

        datum["name"] = info[1].text
        try:
            datum['usd_raised'] = float(info[2].text.strip().replace(",", "")[1:])
        except:
            datum['usd_raised'] = 0

        datum['month'] = info[3].text

        try:
            datum['token_sale_price'] = float(info[4].text.strip().replace(",", "")[1:])
        except:
            datum['token_sale_price'] = 0
        try:
            datum['current_token_price'] = float(info[5].text.strip().replace(",", "")[1:])
        except:
            datum['current_token_price'] = 0

        datum['token_return'] = info[6].text 
        datum['eth_return'] = info[7].text 
        datum['btc_return'] = info[8].text 
        datum['token/eth_return'] = info[9].text 
        datum['token/btc_return'] = info[10].text


    def _create_tables(self):
        """Creates the tables.
        Creates the tables token and val unless they already exist.
        """
        self._c.execute("CREATE TABLE IF NOT EXISTS token ( "
                        "id INTEGER PRIMARY KEY, "
                        "name CHAR(50) NOT NULL)")
        
        self._c.execute("CREATE TABLE IF NOT EXISTS val ( "
                        "id INTEGER PRIMARY KEY, "
                        "usd_raised REAL NOT NULL, "
                        "month CHAR NOT NULL, "
                        "token_sale_price REAL NOT NULL, "
                        "current_token_price REAL NOT NULL, "
                        "token_return CHAR NOT NULL, "
                        "eth_return CHAR NOT NULL, "
                        "btc_return CHAR NOT NULL, "
                        "token_eth_return CHAR NOT NULL, "
                        "token_btc_return CHAR NOT NULL, "
                        "datetime DATETIME NOT NULL, "
                        "token_name CHAR(50) NOT NULL, "
                        "FOREIGN KEY(token_name) REFERENCES token(name) "
                        "ON DELETE CASCADE ON UPDATE CASCADE)")

        self._conn.commit()


    def _val_entry(self, name, usd_raised, month, token_sale_price,
                   current_token_price, token_return, eth_return,btc_return,
                   token_eth_return, token_btc_return, datetime):
        """Enter new data into the database."""
        # If token does not exist yet, insert entry
        self._c.execute("SELECT * FROM token WHERE name = ?", (name,))
        if (self._c.fetchone() is None):
            self._c.execute("INSERT INTO token (name) VALUES (?)",
                (name))
            self._conn.commit()
        # Insert values
        self._c.execute("INSERT INTO val ("
                        "usd_raised, month, token_sale_price,"
                        "current_token_price, token_return, eth_return, btc_return,"
                        "token_eth_return, token_btc_return, datetime, token_name) "
                        "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
                            usd_raised, month, token_sale_price, current_token_price,
                            token_return, eth_return,btc_return, token_eth_return, token_btc_return, datetime, name))
        self._conn.commit()


    def batch_entry(self, data, name, type):
        for entry in data:
            self._val_entry(name,
                            entry['name'],
                            type,
                            entry['usd_raised'],
                            entry['month'],
                            entry['token_sale_price'],
                            entry['current_token_price'],
                            entry['token_return'],
                            entry['eth_return'],
                            entry['btc_return'],
                            entry['token_eth_return'],
                            entry['token_btc_return'],
                            entry['time'])


    def __del__(self):
        self._conn.close()