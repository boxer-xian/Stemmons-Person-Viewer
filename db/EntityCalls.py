
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
                                    where SYSTEM_CODE = 'DPTJT'
                                    and EXTERNAL_DATASOURCE_OBJECT_ID = ( select [Emp_DEPARTMENT_JOB_TITLE_ID]
                                                                            from [DEPARTMENTS].[dbo].[vw_Table_DEPARTMENT_STRUCTURE_EMPLOYEE_MASTER]
                                                                            where SHORT_USER_NAME = '{user}'
                                                                        ) --job id goes here
                                    ) 
        and ENTITY_ID in (  select [ENTITY_ID]
                            from [BOXER_ENTITIES].[dbo].[ENTITY_LIST]
                            where ENTITY_TYPE_ID in (select [ENTITY_TYPE_ID]
                                                    from [BOXER_ENTITIES].[dbo].[ENTITY_TYPE]
                                                    where SYSTEM_CODE = 'USCSE'  -- Application Sys Code
                                                    )
                            )
        '''
        #return app.execQuery(query, conn)
        return self.db.execQuery(query)['ENTITY_ID'].values

    
    def query_title(self, entity_id):
        query = f'''
        SELECT eamt.[ENTITY_ID]
            ,[TEXT]
        FROM [BOXER_ENTITIES].[dbo].[ENTITY_ASSOC_TYPE] eat
        left join [BOXER_ENTITIES].[dbo].[ENTITY_ASSOC_METADATA_TEXT] eamt
        on eat.[ENTITY_ASSOC_TYPE_ID] = eamt.[ENTITY_ASSOC_TYPE_ID]

        where eat.SYSTEM_CODE in ('TITLE')
        and ENTITY_TYPE_ID = (  SELECT top 1 ENTITY_TYPE_ID
                                FROM [BOXER_ENTITIES].[dbo].[ENTITY]
                                where ENTITY_TYPE_ID = (
                                    SELECT TOP 1 [ENTITY_TYPE_ID]
                                    FROM [BOXER_ENTITIES].[dbo].[ENTITY_TYPE]
                                    where SYSTEM_CODE = 'USCSE'
                                    and IS_ACTIVE = 'Y')
                                and is_deleted = 'N'
                            )
        and eat.IS_ACTIVE = 'Y'
        and eamt.IS_ACTIVE = 'Y'
        and eamt.ENTITY_ID = {entity_id}
        '''
        return self.db.execQuery(query)
