import pdfplumber as pr
import csv
from argparse import ArgumentParser

# Get arguments
parser = ArgumentParser()
parser.add_argument("-s", "--start", help="start year of pdf to download", metavar="START_YEAR")
parser.add_argument("-e", "--end", help="end year of pdf to download", metavar="END_YEAR")
args = parser.parse_args()
start_year = int(args.start)
end_year = int(args.end)

EARLIEST_YEAR = 105
LATEST_YEAR = 112

def parse_pdf(year):
    id_reader = csv.reader(open(f'csv/{year}/{year}_id.csv', "r"))
    id_header = next(id_reader)
    for [id, name] in id_reader:
        print(f'Parsing {year}_{id}.pdf...')
        path = f'csv/{year}/{year}_{id}.csv'
        csv_file = open(path, "w", newline="")
        writer = csv.writer(csv_file)
        
        # Write header
        if year >= 111:
            header = ["校系代碼", "校系名稱", "招生名額", "總錄取人數", 
                  "國文", "英文", "數學A", "數學B", "社會", "自然", "英聽",
                  "比序項目", "第一輪錄取", "第一輪比序", "第二輪錄取", "第二輪比序"]
        else:
            header = ["校系代碼", "校系名稱", "招生名額", "總錄取人數", 
                  "國文", "英文", "數學", "社會", "自然", "總級分", "英聽",
                  "比序項目", "第一輪錄取", "第一輪比序", "第二輪錄取", "第二輪比序"]
        writer.writerow(header)

        pdf = pr.open(f'pdf/{year}/{year}_{id}.pdf') # Read PDF
        pages = pdf.pages
        for page in pages:

            table = page.extract_tables()[0]
            
            for i in range(2, len(table)): # Skip header
                arr = table[i]
                code = arr[0]
                name = arr[1].replace('\n', '')
                quota = arr[2]
                total = arr[3]
                standards = arr[5].replace('--', '').split("\n")
                filter_items = arr[10]
                admission_round_1 = arr[11]
                filter_round_1 = arr[12].replace('--', '')
                admission_round_2 = arr[13].replace('--', '')
                filter_round_2 = arr[14].replace('--', '')

                writer.writerow(
                    [code, name, quota, total] + 
                    standards + 
                    [filter_items, admission_round_1, filter_round_1, admission_round_2, filter_round_2]
                )

if __name__ == "__main__":
    for year in range(start_year, end_year + 1):
        parse_pdf(year)