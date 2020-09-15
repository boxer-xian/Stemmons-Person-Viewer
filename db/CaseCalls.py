
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

    def query_case_list(self, user, status, action):
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
            ,[Modified_by_Display_Name] as [Modified By]
            
            ,convert(date, [Created_Datetime Date]) as [Created Date]
            ,convert(date, [Modified_Datetime Date]) as [Modified Date]
            ,convert(date, [CaseClosed Date]) as [Closed Date]
            
        from [FACTS].[dbo].[vw_FACTS_DYN_CASE_LIST] a 
        join [BOXER_CME].[dbo].[CASE_LIST] b
        on a.CASE_ID = b.LIST_CASE_ID
        '''
        
        if status=='Current':
            #query = query + "\nwhere [Created_Datetime Date] is null"
            query = query + "\nwhere (b.LIST_CASE_STATUS_SYSTEM_CODE!='CLOSE' or b.LIST_CASE_STATUS_SYSTEM_CODE is null)"
            
        if action=='Created':
            query = query + f"\nand CREATED_BY_SAM='{user}'"
        elif action=='Assigned':
            query = query + f"\nand ASSIGNED_TO_SAM='{user}'"
        elif action=='Owned':
            query = query + f"\nand OWNED_BY_SAM='{user}'"
        elif action=='Modified':
            query = query + f"\nand MODIFIED_BY_SAM='{user}'"

        case_list = self.db.execQuery(query)
        #case_list = app.execQuery(query, conn)
        
        case_list = case_list.merge(self.query_case_type(), on='CASE_TYPE_ID')
        case_list['Case Title'] = case_list['Case Title'].fillna('NO TITLE')
        #case_list['Case URL'] = 'http://cases.boxerproperty.com/ViewCase.aspx?CaseID='+case_list['Case ID'].astype(str)
        case_list['Due Status'] = case_list['Due Status'].replace({'': None}).fillna('No Due Date')
        case_list['System Status'] = case_list['System Status'].fillna('Blank')
        #case_list['Priority'] = case_list['Priority'].fillna('').apply(lambda x: None if 'select' in x.lower() else x).replace({'': None})
        for c in ['Due Date', 'Created Date', 'Modified Date', 'Closed Date']:
            case_list[c] = pd.to_datetime(case_list[c], errors='coerce').dt.strftime('%m/%d/%Y')
        return case_list

    def groupby_case_type(self, case_list):
        df = case_list.groupby(['Case Type', 'Due Status'])['Case ID'].nunique().reset_index()
        df = df.rename(columns={'Case ID': 'Count of Cases'})
        # sort by case type
        """dfs = []
        case_type = pd.DataFrame({'Case Type': df['Case Type'].unique()})
        for due_status in ['No Due Date', 'Not Due', 'Due', 'Past Due']:
            dff = df[df['Due Status']==due_status].reset_index(drop=True)
            dff = pd.merge(case_type, dff, on='Case Type', how='outer')
            dff['Due Status'] = dff['Due Status'].fillna(due_status)
            dfs.append(dff)
        data = pd.concat(dfs)
        data['Count of Cases'] = data['Count of Cases'].fillna(0).astype(int)
        return data#.sort_values(['Case Type', 'Due Status']).reset_index(drop=True)"""
        return df

    def groupby_due_status(self, case_list):
        df = case_list.groupby(['Due Status'])['Case ID'].nunique().reset_index()
        df = df.rename(columns={'Case ID': 'Count of Cases'})
        return df
    
    def groupby_system_status(self, case_list):
        df = case_list.groupby(['System Status', 'Due Status'])['Case ID'].nunique().reset_index()
        df = df.rename(columns={'Case ID': 'Count of Cases'})
        return df