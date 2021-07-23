
from stemmons.dataBases import sqlDB
import pandas as pd
import numpy as np
from datetime import datetime




class CaseCalls:

    def __init__(self):
        self.db = sqlDB()

    def query_case_type(self):
        query = '''
        select CASE_TYPE_ID, NAME as [Case Type]
        from [BOXER_CME].[dbo].[CASE_TYPE]
        where IS_ACTIVE='Y'
        '''
        return self.db.execQuery(query)

    def query_hopper(self, user):
        query = f'''
        select 'HOPPER_'+SYSTEM_CODE as [HOPPER_SAM]
        from [BOXER_CME].[dbo].[CASE_HOPPER]
        where IS_ACTIVE='Y'
        and HOPPER_OWNER='{user}'
        '''
        return self.db.execQuery(query)['HOPPER_SAM'].tolist()

    def query_team(self, user):
        query = f'''
        select SHORT_USER_NAME, EmpDisplayName as DISPLAY_NAME
        from [DEPARTMENTS].[dbo].[vw_Table_DEPARTMENT_STRUCTURE_EMPLOYEE_MASTER]
        where ACTIVE=1
        and Manager_SHORT_USER_NAME='{user}'
        and SHORT_USER_NAME not like '%HVAC%'  -- remove non-person account
        --and EmpLastName!=''
        order by DISPLAY_NAME
        '''
        return self.db.execQuery(query)
        #['SHORT_USER_NAME'].tolist()

    def due_status(self, due_date):
        if pd.isnull(due_date) or due_date=='' or due_date=='NaT':
            return 'No Due Date'
        else:
            due_date = datetime.strptime(due_date, '%m/%d/%Y').date()
            if  due_date > datetime.today().date():
                return 'Not Due'
            elif due_date < datetime.today().date():
                return 'Past Due'
            elif due_date == datetime.today().date():
                return 'Due'


    def query_case_list(self, users, liferange=None):
            if len(users)==0:
                return None
            
            users = tuple(users) if len(users)>1 else tuple(users*2)
            query = f'''
            select [LIST_CASE_ID] as [Case ID]
                ,[LIST_CASE_TYPE_ID] as [CASE_TYPE_ID]
                ,b.[NAME] as [Case Type]
                ,[LIST_CASE_TITLE] as [Case Title]
                ,(select [VALUE] from [BOXER_CME].[dbo].[CONFIG_SYSTEM] where [SYSTEM_CODE]='VCASE')+'?CaseID='+str(LIST_CASE_ID) as [Case URL]
                
                ,[LIST_CASE_STATUS_VALUE] as [Status]
                ,[LIST_CASE_STATUS_SYSTEM] as [System Status]
                ,[LIST_CASE_STATUS_SYSTEM_CODE] as [STATUS_SYSTEM_CODE]
                ,[LIST_CASE_DUE] as [Due Date]
                
                ,[LIST_CASE_CREATED_BY_SAM] as [CREATED_BY_SAM]
                ,[LIST_CASE_ASSGN_TO_SAM] as [ASSIGNED_TO_SAM]
                ,[LIST_CASE_OWNER_SAM] as [OWNER_SAM]
                ,[LIST_CASE_MODIFIED_BY_SAM] as [MODIFIED_BY_SAM]
                
                ,[LIST_CASE_CREATED_BY_DISPLAY_NAME] as [Created By]
                ,[LIST_CASE_OWNER_DISPLAY_NAME] as [Owner]
                ,[LIST_CASE_ASSGN_TO_DISPLAY_NAME] as [Assigned To]
                ,[LIST_CASE_MODIFIED_BY_DISPLAY_NAME] as [Last Modified By]
                
                ,convert(date, [LIST_CASE_CREATED_DATETIME]) as [Created Date]
                ,convert(date, [LIST_CASE_MODIFIED_DATETIME]) as [Last Modified Date]
                ,convert(date, [LIST_CASE_CLOSED_DATETIME]) as [Closed Date]
                ,convert(date, [LIST_CASE_ASSGN_DATETIME]) as [Assigned Date]
                
            from [BOXER_CME].[dbo].[CASE_LIST] a
            join [BOXER_CME].[dbo].[CASE_TYPE] b
            on a.LIST_CASE_TYPE_ID = b.CASE_TYPE_ID and b.IS_ACTIVE='Y'
            where (LIST_CASE_CREATED_BY_SAM in {users} 
                or LIST_CASE_ASSGN_TO_SAM in {users}
                or LIST_CASE_OWNER_SAM in {users}
                or LIST_CASE_MODIFIED_BY_SAM in {users}
                )
            '''
            if liferange=='Active':
                query = query + f"and (LIST_CASE_STATUS_SYSTEM_CODE is null or LIST_CASE_STATUS_SYSTEM_CODE!='CLOSE')"
            case_list = self.db.execQuery(query)
            #case_list = app.execQuery(query)
            
            case_list['Case Title'] = case_list['Case Title'].fillna('NO TITLE').replace({'': 'NO TITLE'})
            if case_list.shape[0]>0:
                for c in ['Due Date', 'Created Date', 'Last Modified Date', 'Closed Date']:
                    case_list[c] = pd.to_datetime(case_list[c].str.replace('Z', '').str.replace('T', ''), errors='coerce').dt.strftime('%m/%d/%Y')
                case_list['Due Status'] = case_list['Due Date'].apply(lambda x: self.due_status(x))
            else:
                case_list['Due Status'] = None
            
            ''' in some cases, display name could be empty string,
            repalce empty string with SAM '''
            for c1, c2 in zip(['Created By', 'Owner', 'Assigned To', 'Last Modified By'], ['CREATED_BY_SAM', 'OWNER_SAM', 'ASSIGNED_TO_SAM', 'MODIFIED_BY_SAM']):
                case_list[c1] = case_list[c1].replace({'': None}).fillna(case_list[c2])

            #case_list['Case Life Days'] = (pd.to_datetime(case_list['Closed Date'].replace({'NaT': pd.to_datetime('today')})) - pd.to_datetime(case_list['Created Date'])).dt.days
            case_list['Case Life Days'] = (pd.to_datetime(case_list['Closed Date'].fillna(pd.to_datetime('today'))) - pd.to_datetime(case_list['Created Date'])).dt.days
            
            return case_list


    def security_code(self, user, case_type_id):
        query = f"select [BOXER_CME].[dbo].[fn_Cases_GetCaseTypeSecurity]('{user}', {case_type_id}) as CODE"
        return self.db.execQuery(query)
