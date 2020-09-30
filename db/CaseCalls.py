
from stemmons.dataBases import sqlDB
import pandas as pd
import numpy as np



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
        order by DISPLAY_NAME
        '''
        return self.db.execQuery(query)
        #['SHORT_USER_NAME'].tolist()

    def query_case_list(self, users, liferange=None):
        if len(users)==0:
            return None
        
        users = tuple(users) if len(users)>1 else tuple(users*2)
        query = f'''
        select a.[CASE_ID] as [Case ID]
            ,[CASE_TYPE_ID]
            ,[Case Title]
            ,[Case_URL] as [Case URL]
            
            ,[Status Type] as [Status]
            ,b.LIST_CASE_STATUS_SYSTEM as [System Status]
            ,b.LIST_CASE_STATUS_SYSTEM_CODE as [STATUS_SYSTEM_CODE]
            ,[CaseDue_Status] as [Due Status]
            ,convert(date, [Due Date Date]) as [Due Date]
            --,[Priority Type] as [Priority]
            
            ,[CREATED_BY_SAM]
            ,[ASSIGNED_TO_SAM]
            ,[Owned_by_SAM] as [OWNER_SAM]
            ,[MODIFIED_BY_SAM]
            
            ,[Created_by_Display_Name] as [Created By]
            ,[Owned_by_Display_Name] as [Owner]
            ,[Assigned_to_Display_Name] as [Assigned To]
            ,[Modified_by_Display_Name] as [Last Modified By]
            
            ,convert(date, [Created_Datetime Date]) as [Created Date]
            ,convert(date, [Modified_Datetime Date]) as [Last Modified Date]
            ,convert(date, [CaseClosed Date]) as [Closed Date]
            ,convert(date, [Assign_Datetime date]) as [Assigned Date]
            
        from [FACTS].[dbo].[vw_FACTS_DYN_CASE_LIST] a 
        join (select LIST_CASE_ID
                    ,LIST_CASE_STATUS_SYSTEM
                    ,LIST_CASE_STATUS_SYSTEM_CODE
                from [BOXER_CME].[dbo].[CASE_LIST]
            ) b
        on a.CASE_ID = b.LIST_CASE_ID
        where (CREATED_BY_SAM in {users} 
            or ASSIGNED_TO_SAM in {users}
            or OWNED_BY_SAM in {users}
            or MODIFIED_BY_SAM in {users}
            )
        '''
        if liferange=='Active':
            query = query + f"and (LIST_CASE_STATUS_SYSTEM_CODE is null or LIST_CASE_STATUS_SYSTEM_CODE!='CLOSE')"
        case_list = self.db.execQuery(query)
        #case_list = app.execQuery(query, conn)
        
        case_list = case_list.merge(self.query_case_type(), on='CASE_TYPE_ID')
        case_list['Case Title'] = case_list['Case Title'].fillna('NO TITLE').replace({'': 'NO TITLE'})
        #case_list['Case URL'] = 'http://cases.boxerproperty.com/ViewCase.aspx?CaseID='+case_list['Case ID'].astype(str)
        case_list['Due Status'] = case_list['Due Status'].replace({'': None}).fillna('No Due Date')
        #case_list['Priority'] = case_list['Priority'].fillna('').apply(lambda x: None if 'select' in x.lower() else x).replace({'': None})
        for c in ['Due Date', 'Created Date', 'Last Modified Date', 'Closed Date']:
            case_list[c] = pd.to_datetime(case_list[c], errors='coerce').dt.strftime('%m/%d/%Y')

        ''' in some cases, display name could be empty string,
        repalce empty string with SAM '''
        for c1, c2 in zip(['Created By', 'Owner', 'Assigned To', 'Last Modified By'], ['CREATED_BY_SAM', 'OWNER_SAM', 'ASSIGNED_TO_SAM', 'MODIFIED_BY_SAM']):
            case_list[c1] = case_list[c1].replace({'': None}).fillna(case_list[c2])

        #case_list['Case Life Days'] = (pd.to_datetime(case_list['Closed Date'].replace({'NaT': pd.to_datetime('today')})) - pd.to_datetime(case_list['Created Date'])).dt.days
        case_list['Case Life Days'] = (pd.to_datetime(case_list['Closed Date'].fillna(pd.to_datetime('today'))) - pd.to_datetime(case_list['Created Date'])).dt.days
        #print ('query:', users, case_list.shape)
        return case_list

