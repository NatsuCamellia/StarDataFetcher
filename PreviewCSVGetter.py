import requests
from random import randint
import pandas as pd
import csv
import os
import bs4

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

YEAR = 113

def parse_scoresum(scoresum):
    result = "學測"
    if ("國文" in scoresum):
        result += "國"
    if ("英文" in scoresum):
        result += "英"
    if ("數學A" in scoresum):
        result += "數A"
    if ("數學B" in scoresum):
        result += "數B"
    if ("社會" in scoresum):
        result += "社"
    if ("自然" in scoresum):
        result += "自"
    return result

def parse_filter(filter):
    arr = filter.split("\n")[1:-1]

    toReturn = list()
    for i in range(len(arr)):
        str = arr[i]
        if ("在校學業" in str):
            arr[i] = "在校學業"
        elif ("級分總和" in str):
            arr[i] = parse_scoresum(str)
        elif ("學測" in str):
            start = str.find("學測")
            end = str.find("級分")
            arr[i] = str[start:end]
        elif ("學業" in str):
            start = str.find("、")
            end = str.find("學業")
            arr[i] = str[start+1:end + 2]
        elif ("術科考試" in str):
            start = str.find("、")
            if ("(百分等級)" in str):
                end = str.find("(百分等級)")
            else:
                end = str.find("分數")
            arr[i] = "術科" + str[start+4:end]
        else:
            print(f"Warning: Unknown filter item {str}")
            continue
        toReturn.append(arr[i])
    return "\n".join(toReturn)

def parse_standard(standard):
    for i in range(len(standard)):
        if (standard[i] == "--"):
            standard[i] = None
    return standard

def download_pdf(id):
    # Read html file
    file = open(f'html/{id}.html', "r")
    html = file.read()
    soup = bs4.BeautifulSoup(html, "html.parser")
    results = soup.find_all("a")

    print(f'Writing {YEAR}_{id}.csv...')
    path = f'csv/{YEAR}'
    if not os.path.isdir(path):
        os.makedirs(path)
    file = open(f'csv/{YEAR}/{YEAR}_{id}.csv', "w", newline="")
    header = ["校系代碼", "校系名稱", "招生名額", "總錄取人數", 
                  "國文", "英文", "數學A", "數學B", "社會", "自然", "英聽",
                  "比序項目", "第一輪錄取", "第一輪比序", "第二輪錄取", "第二輪比序"]
    writer = csv.writer(file)
    writer.writerow(header)
    for result in results:
        # Get html url
        url = "https://www.cac.edu.tw/star113/system/ColQry_xforStu113Star_Qk65d4gZ4w/" + result["href"][2:]
        random_agent = USER_AGENTS[randint(0, len(USER_AGENTS)-1)]
        headers = { 'User-Agent':random_agent }
        r = requests.get(url, headers=headers)
        r.encoding = "utf-8"
        html = r.text
        soup = bs4.BeautifulSoup(html, "html.parser")

        table = soup.find("table", {"class": "gsd"})
        # We need: 校系代碼,校系名稱,招生名額,國文,英文,數學A,數學B,社會,自然,英聽,比序項目
        rows = table.find_all("tr")
        dep_name = rows[0].find_all("td")[0].text.split("\n")[-2]
        if (len(rows) > 9):
            print(f"Warning: {dep_name} has more than 9 rows")
            continue
        dep_id = rows[2].find_all("td")[1].text
        quota = int(rows[4].find_all("td")[1].text)
        standards = list(rows[2].find_all("td")[3].stripped_strings)
        standards = parse_standard(standards)
        if (len(rows[0].find_all("td")) > 3):
            filter = rows[1].find_all("td")[4].text
        else:
            filter = rows[1].find_all("td")[2].text
        filter = parse_filter(filter)

        print(f"Department ID = {dep_id}")

        # Write to csv
        writer.writerow([dep_id, dep_name, quota, None] + standards + [filter, None, None, None, None])

if __name__ == "__main__":
    id_csv = open(f"csv/{YEAR}/{YEAR}_id.csv", "r")
    csv_reader = csv.reader(id_csv)
    csv_reader.__next__() # Skip first line

    for [id, name] in csv_reader:
        download_pdf(id)
