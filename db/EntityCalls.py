
from stemmons.dataBases import sqlDB
import pandas as pd
import numpy as np


class EntityCalls:

    def __init__(self):
        self.db = sqlDB()

    
    def user_application(self, user):
        query = f'''
        select [ENTITY_ID] --application id
        from [BOXER_ENTITIES].[dbo].[ENTITY_ASSOC_METADATA]
        where IS_ACTIVE = 'Y' 
        and ENTITY_ASSOC_TYPE_ID in ( select [ENTITY_ASSOC_TYPE_ID]
                                    from [BOXER_ENTITIES].[dbo].[ENTITY_ASSOC_TYPE]
                                    where SYSTEM_CODE = 'DPTJT')
        and EXTERNAL_DATASOURCE_OBJECT_ID = (  select [Emp_DEPARTMENT_JOB_TITLE_ID]
                                                from [DEPARTMENTS].[dbo].[vw_Table_DEPARTMENT_STRUCTURE_EMPLOYEE_MASTER]
                                                where SHORT_USER_NAME = '{user}' 
                                            ) --job id goes here
                                    
        and ENTITY_ID in (  select [ENTITY_ID]
                            from [BOXER_ENTITIES].[dbo].[ENTITY_LIST]
                            where ENTITY_TYPE_ID in (select [ENTITY_TYPE_ID]
                                                    from [BOXER_ENTITIES].[dbo].[ENTITY_TYPE]
                                                    where SYSTEM_CODE = 'USCSE'  -- Application Sys Code
                                                    )
                        )
        '''
        #return app.execQuery(query, conn)
        return self.db.execQuery(query)['ENTITY_ID'].tolist()

    
    def entity_assoc_by_sys_code(self, entity_id, sys_code):
        entity_id = tuple(entity_id) if len(entity_id)>1 else tuple(entity_id*2)
        #sys_code = tuple(sys_code) if len(sys_code)>1 else tuple(sys_code*2)

        query = f'''
        select [ENTITY_ID] --application id
            ,[TEXT]
            ,[ENTITY_FILE_ID]
        from [BOXER_ENTITIES].[dbo].[ENTITY_ASSOC_METADATA_TEXT]
        where IS_ACTIVE = 'Y' 
        and ENTITY_ASSOC_TYPE_ID in ( select [ENTITY_ASSOC_TYPE_ID]
                                    from [BOXER_ENTITIES].[dbo].[ENTITY_ASSOC_TYPE]
                                    where SYSTEM_CODE = '{sys_code}')

        and ENTITY_ID in {entity_id}
        '''
        return self.db.execQuery(query)


    def entity_title(self, entity_id):
        return self.entity_assoc_by_sys_code(entity_id, 'TITLE')


    def application_icon(self, entity_id):
        return self.entity_assoc_by_sys_code(entity_id, 'APICN')
