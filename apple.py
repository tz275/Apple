from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import re
import random
import json
import requests
from bs4 import BeautifulSoup


def nextPage():
    wd.find_element(By.CSS_SELECTOR, "#translations-container > div:nth-child(2) > main > div.results-area--search-term.results-area1.results-area-hldr.clearfix > section.results-right > div.results > div.results-pagination > nav > ul > li.pagination__next > span > a > span.next").click()


def saveFile(file, index):
    with open(f"apple{index}.json", 'w') as f:
        json.dump(file, f)


def getNumbers(target):
    temp = ""
    for i in target:
        try:
            temp += str(int(i))
        except:
            pass
    return temp


def getInnerInfo(url):
    session = requests.Session()
    headers = {
            'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection' : 'Keep-Alive',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    url_obj = session.get(url, headers = headers)
    bs = BeautifulSoup(url_obj.text, "html.parser")
    try:
        date = bs.time.text
    except:
        date = ""
    try:
        summary = bs.find("div", {'id': "jd-job-summary", 'class': "jd__row--main jd__summary--main"}).text
    except:
        summary = ""
    try:
        qualifications = bs.find("div", {'id':'jd-key-qualifications'}).text
    except:
        qualifications = ""
    try:
        major_requirement = bs.find("div", {"id":'jd-education-experience'}).text
    except:
        major_requirement = ""
    try:
        degree_requirement = bs.find('div', {"id":"jd-additional-requirements"}).text
    except:
        degree_requirement = ""
    try:
        payment = bs.find('div', {'id': "jd-posting-supplement-footer-0"}).text
    except:
        payment = None
    return date, summary, qualifications, major_requirement, degree_requirement, payment


def getSalary(target):
    if not target:
        return [None] * 2
    ret = []
    for i in target.split(' '):
        if re.match(r"^\$", i):
            ret.append(i)
    if len(ret) >= 2:
        return ret
    elif len(ret) == 1:
        return ret * 2
    else:
        return [None] * 2

def educationRequirement(target):
    temp = ""
    if "BS" in target or "Bachelors" in target:
        temp += "bachelors"
    if "M.S." in target or "MS" in target or "Masters" in target:
        if not temp:
            temp += "masters"
        else:
            temp += " | masters"
    if "Ph.D." in target or "PhD" in target:
        if not temp:
            temp += "phd"
        else:
            temp += "| phd"
    if not temp:
        return {"education" : None, "major" : target}
    return {"education": temp, "major" : target}



if __name__ == "__main__":
    wd = webdriver.Chrome(r'/Users/tingkangzhao/SeleniumDriver/chromedriver')
    wd.implicitly_wait(10)
    # software, machine learning, technology, data, engineer
    url = "https://jobs.apple.com/en-us/search?sort=relevance&key=software+data+engineer+machine%252520learning+technology&location=united-states-USA"
    wd.get(url)

    # get all the job urls
    count = 0
    file_index = 0
    jobs_dic = {}
    while True:
        for i in wd.find_elements(By.CSS_SELECTOR, "tbody"):
            time.sleep(random.randint(1, 3))
            job_dic = {}
            # get info from outer HTML
            title = i.find_element(By.CSS_SELECTOR, '.table-col-1>a').text
            href = i.find_element(By.CSS_SELECTOR, '.table-col-1>a').get_attribute("href")
            location = i.find_element(By.CSS_SELECTOR, ".table-col-2").text
            _id = i.find_element(By.CSS_SELECTOR, '.table-col-1>a').get_attribute("id")
            # get info from inner HTML
            date, summary, qualifications, major_requirement, degree_requirement, payment = getInnerInfo(href)

            # save each job into dictionary
            id = getNumbers(_id)
            job_dic["jobID"] = id
            job_dic["origin_search"] = None
            job_dic["posted"] = date
            job_dic["jobTitle"] = title
            job_dic["companyName"] = "Apple"
            job_dic["link"] = href
            job_dic["jobLocation"] = {"remote": "not specified", "city": location, "state": None, "country": "US"}
            job_dic["educationRequirement"] = educationRequirement(major_requirement)
            job_dic["jobType"] = {"internship" : False, "partTime": False, "fullTime": True, "coop": False, "contract": False, "independent_contractor": False, "temporary": False, "oncall" : False, "volunteer": "False"}
            job_dic["visaSponsorship"] = {"none": True, "cpt_opt": True, "h1b": True, "eb": True}
            salary_lst = getSalary(payment)
            job_dic["salary"] = {"min": salary_lst[0], "max": salary_lst[-1]}
            job_dic["benefits"] = None
            job_dic["requirements"] = qualifications + major_requirement + degree_requirement
            job_dic["jobDescription"] = summary
            print(f"we get {count}th job")
            jobs_dic[id] = job_dic
            count += 1

        if count >= 100:
            count = 0
            file_index += 1
            saveFile(jobs_dic, file_index)
            jobs_dic = {}

        time.sleep(random.randint(5, 13))
        try:
            nextPage()
        except:
            break
