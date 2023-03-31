#!/usr/bin/env python

# -*- coding: utf-8 -*-

import csv
import json
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import numpy as np
import os
import time

### connect to the database
engine = sqlalchemy.create_engine("mysql://codetest:swordfish@database/codetest",encoding='utf8')
connection = engine.connect()

def pandas_ingest(tablename, engine):
    start = time.time()
    df = pd.read_csv(str('/data/'+tablename+'.csv'))
    df.to_sql(tablename, con=engine, if_exists='replace', index=False)
    stop = time.time()
    count_rows = pd.read_sql('SELECT COUNT(*) as nrows FROM %s' % tablename, con=engine)['nrows'][0]
    print("%s table %s rows - %ss" % (tablename, count_rows, round(stop-start,2)))

def query_to_json(query, path_to_json):
    start = time.time()
    rows = connection.execute(sqlalchemy.text(query))
    printrows = [{row[0]: row[1] for row in rows}][0]
    with open(path_to_json, 'w') as json_file:
        json.dump(printrows, json_file, separators=(',', ':'), ensure_ascii=False)
    stop = time.time()
    print("%s written - %ss" % (path_to_json, round(stop-start,2)))

    
def main():

        ### Load dataset csvs into database
    try:
        for i in ('people','places'):
            pandas_ingest(i, engine)

            ### Query for number of births for each country in datasets, write to json
        try:
            births_query = '''SELECT country,COUNT(*) as count
                                FROM people
                                LEFT JOIN places ON people.place_of_birth = places.city
                                GROUP BY country'''
            query_to_json(births_query,'/data/summary_output.json')

            ### Query for most common month of birth for each county in N. Ireland in datasets, write to json
            months_query = '''SELECT county, month
                                FROM (
                                SELECT places.county,
                                    MONTHNAME(people.date_of_birth) AS month,
                                    COUNT(people.date_of_birth) AS births,  
                                    ROW_NUMBER() OVER (PARTITION BY county ORDER BY COUNT(people.date_of_birth) DESC) AS intRow
                                FROM people
                                LEFT JOIN places ON people.place_of_birth = places.city
                                WHERE country = 'Northern Ireland'
                                GROUP BY county, month) as T
                                WHERE T.intRow = 1'''
            query_to_json(months_query,'/data/commmon_birth_months_output.json')
        except Exception as ex:
            print('There was a problem with query to json:')
            print(ex.__class__)
            print(ex)

    except Exception as ex:
        print('There was a problem loading '+i+' data:')
        print(ex.__class__)
        print(ex)

    connection.close()
    engine.dispose()

if __name__ == '__main__':
    main()
