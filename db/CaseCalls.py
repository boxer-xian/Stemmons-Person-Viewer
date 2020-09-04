
from stemmons.dataBases import sqlDB
class CaseCalls:

    def __init__(self):
        self.db = sqlDB()

    def case_types(self):
        #print('executed')
        query = '''select distinct CASE_TYPE_ID  from facts.dbo.case_list '''
        #print(app.execQuery(query))
        return self.db.execQuery(query)


