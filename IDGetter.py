from bs4 import BeautifulSoup as bs
import requests
import csv
from random import randint
from argparse import ArgumentParser
import os
 
USER_AGENTS = [
 "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
 "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
 "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
 "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
 "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
 "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
 "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
 "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
 "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
 "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
 "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
 "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
 "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
 "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
 "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]
 
random_agent = USER_AGENTS[randint(0, len(USER_AGENTS)-1)]
headers = {
    'User-Agent':random_agent,
}

# Get arguments
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

def download_preview_id():
    url = "https://www.cac.edu.tw/star113/system/ColQry_xforStu113Star_Qk65d4gZ4w/TotalGsdShow.htm"
    r = requests.get(url, headers=headers)
    r.encoding = "utf-8"
    html = r.text
    soup = bs(html, "html.parser")
    results = soup.find_all("a")
    
    path = "csv/113"
    if not os.path.isdir(path):
        os.makedirs(path)
    file = open("csv/113/113_id.csv", "w", newline="")
    writer = csv.writer(file)
    writer.writerow(["ID", "Name"])
    id = [0, 0]
    for result in results:
        text = result.text
        id[0] = text[1:4]  # ID
        dash_index = text.find("-")
        id[1] = text[5:dash_index]   # Name
        writer.writerow(id)

def download_id(year):
    if (year == 113):
        return download_preview_id()
    
    # Get data from CAC
    url = f"https://www.cac.edu.tw/cacportal/star_his_report/{year}/{year}_result_standard/one2seven/collegeList_1.php"
    html = requests.get(url, headers=headers)
    soup = bs(html.text, "html.parser")
    results = soup.find_all("a")

    # Create folder and open writer
    path = f"csv/{year}"
    if not os.path.isdir(path):
        os.makedirs(path)
    file = open(f"csv/{year}/{year}_id.csv", "w", newline="")
    writer = csv.writer(file)
    writer.writerow(["ID", "Name"])

    # Read ID and Name
    id = [0, 0]
    if year < 111:
        for result in results: 
            text = result.text
            id[0] = text[2:5]  # ID
            id[1] = text[6:]   # Name
            writer.writerow(id)
    else:
        for result in results: # Format: (xxx)name
            text = result.text
            id[0] = text[1:4]  # ID
            id[1] = text[5:]   # Name
            writer.writerow(id)

if __name__ == "__main__":
    for year in range(start_year, end_year + 1):
        download_id(year)