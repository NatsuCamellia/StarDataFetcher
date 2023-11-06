import csv
import json
import os
import pandas as pd
import numpy as np
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-s", "--start", help="start year of pdf to download", metavar="START_YEAR")
parser.add_argument("-e", "--end", help="end year of pdf to download", metavar="END_YEAR")
args = parser.parse_args()
start_year = int(args.start)
end_year = int(args.end)

EARLIEST_YEAR = 105
LATEST_YEAR = 113

if start_year not in range(EARLIEST_YEAR, LATEST_YEAR + 1) or end_year not in range(EARLIEST_YEAR, LATEST_YEAR + 1):
    print("Error: Year should be in range {} to {}".format(EARLIEST_YEAR, LATEST_YEAR))
    exit(1)
if start_year > end_year:
    print("Error: Start year should not be later than end year")
    exit(1)

def get_result(df: pd.DataFrame, name: str, year: int): # Get result of a department as a dict
    if df is None:
        return None
    
    result = dict()
    row = df[df['校系名稱'] == name]
    if row.empty:
        return None
    result['year'] = year
    if row['總錄取人數'].iloc[0] is None:
        result['admissionAll'] = 0
    else:
        result['admissionAll'] = int(row['總錄取人數'].iloc[0])
    if row['第一輪錄取'].iloc[0] is None:
        result['admissionOne'] = 0
    else:
        result['admissionOne'] = int(row['第一輪錄取'].iloc[0])
    if row['第二輪錄取'].iloc[0] is None:
        result['admissionTwo'] = 0
    else:
        result['admissionTwo'] = int(row['第二輪錄取'].iloc[0])
    result['quota'] = int(row['招生名額'].iloc[0])

    # Get requirements
    subject_arr = df.head(0).columns[4:11].tolist()
    requirements = list({"subject": subject, "value": row[subject].iloc[0]} for subject in subject_arr)
    result['requirements'] = requirements

    # Get filters
    filter_arr = row['比序項目'].iloc[0].split("\n")

    if result['admissionOne'] != 0:
        filter_one_arr = row['第一輪比序'].iloc[0].split("\n")
        filter_one = [
            {
                "subject": filter_arr[i],
                "value": filter_one_arr[i] if filter_one_arr[i] != '' else None
            } for i in range(len(filter_arr))
        ]
        result['filterOne'] = filter_one
    else:
        filter_one = [
            {
                "subject": filter_arr[i],
                "value": None
            } for i in range(len(filter_arr))
        ]
        result['filterOne'] = filter_one

    if result['admissionTwo'] != 0:
        filter_two_arr = row['第二輪比序'].iloc[0].split("\n")
        filter_two = [
            {
                "subject": filter_arr[i],
                "value": filter_two_arr[i] if filter_two_arr[i] != '' else None
            } for i in range(len(filter_arr))
        ]
        result['filterTwo'] = filter_two

    return result

def get_dataframe(school_id: str, year: int):
    path = f'csv/{year}/{year}_{school_id}.csv'
    if not os.path.exists(path):
        return None
    dtype = {'校系代碼': str, "招生名額": pd.Int64Dtype, "總錄取人數": pd.Int64Dtype, "第一輪錄取": pd.Int64Dtype, "第二輪錄取": pd.Int64Dtype}
    df = pd.read_csv(path, dtype={'校系代碼': str})
    df.replace(pd.NA, None, inplace=True)
    df.replace(np.nan, None, inplace=True)
    pd.set_option('display.max_columns', None)
    return df

def csv_to_json(school_id: str):
    dataframes = dict()
    for year in range(start_year, end_year + 1):
        dataframes[year] = get_dataframe(school_id, year)

    dir = f'json/{school_id}'
    if not os.path.exists(dir):
        os.makedirs(dir)

    for (code, name) in dataframes[end_year].loc[:, '校系代碼':'校系名稱'].itertuples(index=False):
        json_dict = dict()
        json_dict['code'] = code
        json_dict['name'] = name
        print(f'Parsing {json_dict["name"]}({json_dict["code"]})...')
        results = list()
        for year in range(start_year, end_year + 1):
            result = get_result(dataframes[year], name, year)
            if result is not None:
                results.append(result)
        json_dict['results'] = results
        
        path = os.path.join(dir, f'{json_dict["name"].replace("/", "")}.json')
        json.dump(json_dict, open(path, "w", encoding="utf-8"), ensure_ascii=False)
    pass

if __name__ == "__main__":
    # Read school id
    csv_file = open(f'csv/{end_year}/{end_year}_id.csv', "r")
    reader = csv.reader(csv_file)
    header = next(reader)
    for [id, name] in reader:
        print(f'Parsing {name}({id})...')
        csv_to_json(id)