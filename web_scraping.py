import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import re
import math
import os
from fuzzywuzzy import fuzz
from STA2453_Project1.web_scraping_config import match_list, columns, keyword_set, jobs_per_page
import time

def get_maxjobs(page):
    #Get number of jobs corresponding to search
    searchCountDiv = page.find(name='div', id='searchCountPages')
    if(searchCountDiv is None):
        #No results found for this search result
        return None
    
    #use regex to extract the initial estimate max # of jobs
    results = re.findall('\d+',str(searchCountDiv.string))
    if(len(results) > 2):
        #for long numbers separated by commas
        num_jobs = "".join(results[1:])
    else:
        num_jobs = results[1]
    return int(num_jobs)


def get_maxpages(num_jobs,jobs_per_page=15):
    #Each page displays a max of 15 jobs
    maxpages = math.ceil(int(num_jobs) / jobs_per_page)
    return maxpages

def get_last_page(search, max_pages):
    '''get the last page for a search'''
    last_page = requests.get(search+"&start=" + str((max_pages*10)-10))
    soup = BeautifulSoup(last_page.text, 'lxml')
    return soup

def adjust_maxpages(last_page, max_pages, num_jobs, jobs_per_page=15):
    '''Calculate the true number of max pages given the last page of a search'''
    deleted_msg = last_page.find(name='p',class_='dupetext')
    if(deleted_msg is None):
        return max_pages
    else:
        results = re.findall('\d+',str(deleted_msg.text))
        jobs_removed = int(results[0])
        jobs_diff = (num_jobs) - jobs_removed
        return math.ceil(jobs_diff/ jobs_per_page)



def extract_job_title(page):
    jobs = []
    for div in page.find_all(name='div', attrs={'class':'row'}):
        for a in div.find_all(name='a', attrs={'data-tn-element':'jobTitle'}):
            jobs.append(a['title'])
    return(jobs)

#The span may either contain text or a link
def extract_company(page): 
    companies = []
    for div in page.find_all(name='div', attrs={'class':'row'}):
        try:
            a = div.find(name='a', attrs={'data-tn-element':'companyName'})
            if(a is None):
                span = div.find(name='span', class_='company')
                company = span.string.strip()
            else:
                company = a.string.strip()
                
            companies.append(company)
        except:
            companies.append("Nothing_found")
    return(companies)

def extract_salary(page):
    salaries = []
    for div in page.find_all(name='div', attrs={'class':'row'}):
        try:
            salary = div.find(name='span', attrs={'class':'salaryText'})
            salaries.append(salary.text.strip())
        except:
            salaries.append('Nothing_found')
    return(salaries)

def extract_location(page):
    locations = []
    
    for div in page.find_all(name='div', attrs={'class':'row'}):
        try:
            a = div.find(name='a', attrs={'data-tn-element':'companyName'})
            if(a is None):
                span = div.find(name='span', class_='company')
                company = span.string.strip()
            else:
                company = a.string.strip()
            span = div.find(name='span', class_='location')
            locations.append(span.string)
        except:
            #Occasionally a location is missing and it says it is remote in the description.
            locations.append('Remote')
    return locations

def extract_industry(page):
    industries = []
    for div in page.find_all(name='div', attrs={'class':'row'}):
        #sometimes just a span, sometimes the span includes a link
        span = div.find(name='span', class_='company')
        
        try:
            inner_span = span.find(name='a', attrs={'data-tn-element':'companyName'})
            #if inner_span is None this indexing will throw exception
            link = "https://ca.indeed.com"+inner_span['href']
            company_page = requests.get(link)
            soup = BeautifulSoup(company_page.text, 'lxml')
            a = soup.find(name='a',class_='cmp-AboutMetadata-plainLink')
            industries.append(a.string)
            
        except:
            #Sometimes company do not list an industry.
            industries.append('Nothing_found')
            
    return industries

def fuzzy_score(Str1, Str2):
    if Str2 == None:
        return 100
    else:
        return fuzz.partial_ratio(Str1.lower(),Str2.lower())


def fuzzy_match(Str1, match_list):
    matches = [None]*len(match_list)
    for counter, it in enumerate(match_list,start=0):
        matches[counter] = fuzzy_score(Str1,it) > 75
    return matches


def get_matches(soup, match_list):
    '''Given a job page find the relevant bold headers.

    Args: 
        soup (BeautifulSoup page): Html page
        match_list (List[str]): the list of terms to match
    Returns:
        Union[None,List[BeautifulSoup.Tag]]'''

    passed=[]
    #Requirement-like titles are usually bolded
    bolds = soup.find_all(name='b')
    if(bolds is None):
        return []
    for b in bolds:
        if any(fuzzy_match(b.text, match_list)):
            #if match is acceptable add it to list
            passed.append(b)

    return passed

def get_col_str(page,passed):
    col_str = ""
    if (len(passed) > 0):
        for b in passed:
            #scenario 1 a ul comes right after the title
            ul = b.parent.findNext(name='ul')
            if(ul is None):
                continue
            #for ul in uls:
            for li in ul.findAll('li'):
                if(li.string is not None):
                    col_str = col_str + li.string
            #scenario 2 it is a sequence of divs UNTIL next <b> tag. 
            #May not be able to do anything with this one. It is extremely rare ~2%
    else:
        ul = None
        lis = None
        ul = page.find(name='ul')

        if(ul is not None):
            lis = ul.findAll('li')

        if(lis is not None):
            for li in lis:
                if(li.string is not None):
                    col_str = col_str + li.string
    
    return col_str



def extract_requirements(page, match_list):
    '''Returns:
        List[str]'''
    requirements = []
    for div in page.find_all(name='div', attrs={'class':'row'}):
        a = div.find(name='a', attrs={'data-tn-element':'jobTitle'})
        joblink = "https://ca.indeed.com"+a['href']
        job_page = requests.get(joblink)
        soup = BeautifulSoup(job_page.text, 'lxml')
        passed = get_matches(soup, match_list)

        col_str = get_col_str(soup,passed)
        #if no valid matches then do ul = b.parent.parent.findNext(name='ul') to find first ul in doc.
        #scenario 3, NO <b> tag its just a ul (assume the first)
        if(col_str != ""):
            requirements.append(col_str)
        else:    
            requirements.append("Nothing_found")
            
    return requirements


def data_folder_create(folder_name):
    try:
        # create folder       
        os.mkdir(folder_name)
        print("Now create " + folder_name + " folder")
    except:
        # if the folder already exists, do nothing
        pass

if __name__ == "__main__":
#Eventually use all cities by removing the Vancouver keyword.
    
    # create data folder
    data_folder_create("STA2453_Project1/data")

    df = pd.DataFrame(columns = columns)
    for keyword in keyword_set:
        #first do a quick preliminary search to find out how many pages
        search = "https://ca.indeed.com/jobs?q=" + str(keyword) + \
                            "&l=Vancouver,+BC&radius=0&jt=fulltime"
        page = requests.get(search)
        soup = BeautifulSoup(page.text, 'lxml')
        num_jobs = get_maxjobs(soup)
        if(num_jobs is None):
            print(f"No jobs found for keyword: {keyword}")
            continue
        max_pages = get_maxpages(num_jobs,jobs_per_page)
        last_page = get_last_page(search,max_pages)
        adjust_pages = adjust_maxpages(last_page,max_pages,num_jobs,jobs_per_page)

        if(adjust_pages is None):
            continue

        print(f"There are totally {adjust_pages} pages to be scrapped.")
        for start in range(1, adjust_pages+1):
            #pages show 15 results at a time
            if(start == 50):
                print("Sleeping to avoid captcha")
                time.sleep(60)

            print(f"Scraping page {start} of keyword search: {keyword}")
            #start numbers go 0, 10 ,20 ,30 , etc. but shows 15 results per page.
            #e.g. page 3 is start=20
            page = requests.get("https://ca.indeed.com/jobs?q=" + str(keyword) + 
                                "&l=Vancouver,+BC&radius=0&jt=fulltime&start=" + str((start*10)-10))
            soup = BeautifulSoup(page.text, 'lxml')
            
            job_titles = extract_job_title(soup)
            locations = extract_location(soup)
            companies = extract_company(soup)
            salaries = extract_salary(soup)
            industry = extract_industry(soup)
            requirements = extract_requirements(soup,match_list=match_list)

            data = {"job_title":job_titles, "company_name":companies,
                    "requirements":requirements,
                    "location":locations, "industry": industry,
                    "salary":salaries}
            temp_df = pd.DataFrame(data)
            df = df.append(temp_df)
            time.sleep(2)

        print("===========================")
        time.sleep(60)

    df.to_csv('STA2453_Project1/data/job_salary.csv')

