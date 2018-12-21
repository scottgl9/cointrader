import sqlite3

class IndicatorCache(object):
    def __init__(self, symbol):
        self.cursor = None
        self.cache_list = None
        self.cache_entry = {}
        self.cache_result = {}
        self.id_list = []
        self.cache_counters = {}
        self.symbol = symbol
        self.loaded = False
        self.init_load = False
        self.table_created = False

    def empty(self):
        return not self.cache_list

    def get_cache_list(self):
        return self.cache_list

    def id_in_cache(self, id):
        if id in self.cache_list:
            return True
        return False

    def create_cache(self, id):
        if self.empty():
            self.cache_list = {}

        if 'ts' not in self.cache_list:
            self.cache_list['ts'] = []

        self.cache_list[id] = []
        self.id_list.append(id)

    def remove_cache(self, id):
        if self.empty():
            return

        if id not in self.cache_list:
            return

        del self.cache_list[id]

    def get_result_from_cache(self, id):
        id = str(id)
        counter = self.cache_counters[id]
        result = self.cache_list[id][counter]
        self.cache_counters[id] = counter + 1
        return float(result)

    def get_results_from_cache(self):
        result = {}
        row = self.cursor.fetchone()
        for i in range(0, len(self.id_list)):
            result[self.id_list[i]] = row[i]
        return result

    def add_result_to_cache(self, id, ts, result):
        #if not self.id_in_cache(id):
        #    return False
        #if ts not in self.cache_list['ts']:
        #    self.cache_list['ts'].append(ts)
        #self.cache_list[id].append(result)
        self.cache_entry['ts'] = ts
        self.cache_entry[id] = result
        return True

    def load_cache_from_db(self, db=None):
        self.init_load = True

        if not db:
            self.loaded = False
            return False

        #if not self.table_exists(db):
        #    self.loaded = False
        #    return False

        self.cache_list = {}

        c = db.cursor()
        try:
            c.execute("SELECT * FROM {}".format(self.symbol))
        except sqlite3.OperationalError:
            self.loaded = False
            c.close()
            return False

        self.cursor = c

        # get column names
        #ids = [description[0] for description in c.description]

        #for id in ids:
        #    self.cache_list[id] = []
        #    self.cache_counters[id] = 0

        #for row in c:
        #    for i in range(0, len(row)):
        #        self.cache_list[ids[i]].append(row[i])

        self.loaded = True

        return True

    #def table_exists(self, c):
    #    cursor = c.cursor()
    #    cursor.execute("""select count(*) from sqlite_master as tables where type='table'""")
    #    count = cursor.fetchone()[0]
    #    cursor.close()
    #    print(count)
    #    if count:
    #        return True
    #    return False

    def create_table(self, c, id):
        cur = c.cursor()
        if id == 'ts':
            sql = """CREATE TABLE IF NOT EXISTS {} (ts INTEGER)""".format(self.symbol)
        else:
            sql = """CREATE TABLE IF NOT EXISTS {} ('{}' REAL)""".format(self.symbol, id)
        cur.execute(sql)

    def add_column(self, c, id):
        cur = c.cursor()
        if id == 'ts':
            sql = """ALTER TABLE {} ADD COLUMN 'ts' INTEGER;""".format(self.symbol)
        else:
            sql = """ALTER TABLE {} ADD COLUMN '{}' REAL;""".format(self.symbol, id)
        cur.execute(sql)

    def write_results_to_cache(self, c):
        cursor = c.cursor()

        if not self.table_created:
            for id in self.id_list:
                if not self.table_created:
                    self.create_table(c, id)
                    self.table_created = True
                else:
                    self.add_column(c, id)

        values = []
        for id in self.id_list:
            values.append(self.cache_entry[id])

        temp = ['?'] * len(values)

        sql = """INSERT INTO {} VALUES {}""".format(self.symbol, "(" + ",".join(temp) + ")")
        cursor.execute(sql, values)

        self.cache_entry = {}
