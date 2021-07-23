from db.CaseCalls import CaseCalls
from flask import request 
import pandas as pd

class CaseHandler:
    '''Class to handle data tranformations for all case tabs,
        prefix all methods with tab it is associated with.'''


    def groupby_case_type(self, case_list):
        df = case_list.groupby(['Case Type', 'Due Status'])['Case ID'].nunique().reset_index()
        df = df.rename(columns={'Case ID': 'Count of Cases'})
        return df
    
    def groupby_system_status(self, case_list):
        case_list['System Status'] = case_list['System Status'].fillna('Blank')
        df = case_list.groupby(['System Status', 'Due Status'])['Case ID'].nunique().reset_index()
        df = df.rename(columns={'Case ID': 'Count of Cases'})
        return df

    def to_json(self, data):
        return data.to_json(orient='split') if data is not None else None

    
    def security(self, case_list):
        user = request.cookies['user']
        
        filter_out = []
        for case_type_id in case_list['CASE_TYPE_ID'].unique().tolist():
            sec_code = CaseCalls().security_code(user, case_type_id)
            if sec_code is not None and sec_code.shape[0]==1 and sec_code['CODE'].values[0] in ['', 'C']:
                filter_out.append(case_type_id)
        
        if len(filter_out)>0:
            case_list = case_list[~case_list['CASE_TYPE_ID'].isin(filter_out)].reset_index(drop=True)
        
        return case_list
