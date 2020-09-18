
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

    

