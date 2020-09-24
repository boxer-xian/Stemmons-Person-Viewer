import pandas as pd
import numpy as np
import re
import dash_html_components as html
import dash_core_components as dcc

# generatate a table head with given column names
# the first row as column names
# seconde row as input row, used to search content in the corresponding column
# column names in url_col use class 'case_title' in assets/table.css, wider than others
def generate_table_head(columns, url_col):
    filter_cell_style = {'height': '100%', 'width': '100%', 'border': 'none', 'padding': '0px', 'color': 'blue'}
    return html.Thead([
        html.Tr([
            html.Th(col, id={'type':'header', 'colname':col}, className='case_title') if col in url_col else \
            html.Th(col, id={'type':'header', 'colname':col}) for col in columns
        ], className='head'), 
        # filter row
        html.Tr([
            html.Th(dcc.Input(value='', placeholder='filter...', id={'type':'filter','colname':col}, debounce=True, style=filter_cell_style), className='filter case_title') if col=='Case Title' else \
            html.Th(dcc.Input(value='', placeholder='filter...', id={'type':'filter','colname':col}, debounce=True, style=filter_cell_style), className='filter') for col in columns
        ], className='head_filter') 
    ])

# generate table body, no column names included
def generate_table_body(df, url_col):
    rows = []
    for i in range(df.shape[0]):
        rows.append(html.Tr([
            html.Td(html.A(href=df.loc[i, col][1], children=df.loc[i, col][0], target='_blank'), className='case_title') if col in url_col else \
            html.Td(df.loc[i, col]) for col in df.columns
        ],
            style={'background-color': '#f2f2f2' if i%2==1 else 'white'}
        ))
    return html.Tbody(rows)

# fiter dataframe with input content from input row
def filter_table(df, filter_values, filter_ids, url_col=[]):
    if sum(len(value) for value in filter_values if value!=None)>0:
        for value, id in zip(filter_values, filter_ids):
            if value is not None and len(value)>=1:
                filter_col = id['colname']
                keyword = str(value)
                url_col = url_col
                df = filter(df, filter_col, keyword, url_col)
    return df

# sort dataframe
# odd click times on header name, sort as asc; even click tiems on header name, sort as desc
def sort_table(df, header_clicks, header_ids, previous_header_clicks, url_col=[], col_filter='date'):
    if any(header_clicks):
        index, n_clicks = list_diff(header_clicks, previous_header_clicks)
        col = header_ids[index]['colname']
        sort = True if n_clicks%2==1 else False
        # date or datetime column sorting
        if col_filter in col.lower():   # or 'due' in col.lower()
            df[col+'2'] = pd.to_datetime(df[col])
            df = df.sort_values(col+'2', ascending=sort, na_position='last').reset_index(drop=True)
            df = df.drop(col+'2', axis=1)
        # string column sorting, ignore upper or lower case
        elif df[col].dtype=='O' and col not in url_col:
            df = df.loc[df[col].str.lower().sort_values(ascending=sort, na_position='last').index].reset_index(drop=True)
        else:
            df = df.sort_values(col, ascending=sort, na_position='last').reset_index(drop=True)
    return df

def filter(df, col, keyword, url_col=[], key_filters=['na', 'n/a', 'nan', 'nat', 'null', 'none', ' ']):
    keyword = keyword.lower()
    if keyword in key_filters:
        return df[df[col].isnull() | (df[col].astype(str)=='')].reset_index(drop=True)
    keyword = keyword.strip()
    
    if df[col].dtype in ['int64', 'float64'] or 'date' in col.lower():     # or 'due' in col.lower()
        keyword = keyword.replace(',', '').replace('&', '').replace(';', '')
        if keyword[0] in ['!', '~'] or keyword[:2] in ['<>', '!=']:    #'!10'
            value = keyword.replace('<>', '').replace('!', '').replace('!=', '').replace('~', '')
            df = compare(df, col, '!=', value)
        elif '>' in keyword and '<' in keyword:   # '<=1 >=5', '>=01/01/2020 <=01/31/2020'
            if keyword[0] == '>':
                op1 = '>=' if keyword[1]=='=' else '>'
                op2 = '<=' if keyword[keyword.index('<')+1]=='=' else '<'
                value1 = keyword[len(op1): keyword.index(op2)]
                value2 = keyword[keyword.index(op2)+len(op2): ]
            elif keyword[0] == '<':
                op1 = '<=' if keyword[1]=='=' else '<'
                op2 = '>=' if keyword[keyword.index('>')+1]=='=' else '>'
                
                value1 = keyword[len(op1): keyword.index(op2)]
                value2 = keyword[keyword.index(op2)+len(op2): ]
            df = compare(df, col, op1, value1)
            df = compare(df, col, op2, value2)
        elif '>' in keyword:   # '>=1', '>=01/01/2020'
            op = '>=' if '=' in keyword else '>'
            value = keyword.replace(op, '')
            df = compare(df, col, op, value)
        elif '<' in keyword:   # '<=1', '<=01/01/2020'
            op = '<=' if '=' in keyword else '<'
            value = keyword.replace(op, '')
            df = compare(df, col, op, value)
        else:  # '1', '=1', '==1', '1/1/2020'
            value = keyword.replace('=', '')
            df = compare(df, col, '==', value)
    elif col in url_col:    #eg. col=='Case Title'  ['title', 'url']
        if keyword[0]=='!':
            df = df[~df[col].apply(lambda x: x[0]).fillna('').str.lower().str.contains(keyword[1:])].reset_index(drop=True)
        else:
            df = df[df[col].apply(lambda x: x[0]).fillna('').str.lower().str.contains(keyword)].reset_index(drop=True)
    else:
        if keyword[0]=='!':
            df = df[~df[col].fillna('').str.lower().str.contains(keyword[1:])].reset_index(drop=True)
        else:
            df = df[df[col].fillna('').str.lower().str.contains(keyword)].reset_index(drop=True)
    return df
    
def compare(df, col, op, value):
    if df[col].dtype in ['int64', 'float64']:
        value = float(value)
    elif 'date' in col.lower():    # or 'due' in col.lower()
        try: 
            value = pd.to_datetime(value)
            df[col+'2'] = pd.to_datetime(df[col])
        except: df[col+'2'] = df[col]
        col = col+'2'
    if op=='==':
        df = df[df[col]==value].reset_index(drop=True)
    elif op=='!=':
        df = df[df[col]!=value].reset_index(drop=True)
    elif op=='>':
        df = df[df[col]>value].reset_index(drop=True)
    elif op=='>=':
        df = df[df[col]>=value].reset_index(drop=True)
    elif op=='<':
        df = df[df[col]<value].reset_index(drop=True)
    elif op=='<=':
        df = df[df[col]<=value].reset_index(drop=True)
    if 'date' in col.lower():   # or 'due' in col.lower()
        df = df.drop(col, axis=1)
    return df

def list_diff(list1, list2):
    index = 0
    value = list1[0]
    for i in range(len(list1)):
        if list1[i]!=list2[i]:
            index = i
            value = list1[i]
    return index, value

