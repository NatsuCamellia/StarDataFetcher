import csv
import json
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

def get_departments(school_id: str):
    csv_reader = csv.reader(open(f"csv/{year}/{year}_{school_id}.csv", "r"))
    header = next(csv_reader)
    departments = [{'code': row[0], 'name': row[1]} for row in csv_reader]
    return departments

def get_schools(year: int):
    csv_reader = csv.reader(open(f"csv/{year}/{year}_id.csv", "r"))
    header = next(csv_reader)
    schools = list()
    for [id, name] in csv_reader:
        school = dict()
        school['id'] = id
        school['name'] = name
        school['departments'] = get_departments(id)
        schools.append(school)
    return schools

if __name__ == "__main__":
    for year in range(start_year, end_year + 1):
        schools = get_schools(year)
        json.dump(schools, open(f"json/{year}_schools.json", "w", encoding='utf-8'), ensure_ascii=False)