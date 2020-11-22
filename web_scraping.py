import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import re
import math
from fuzzywuzzy import fuzz

def get_maxpages(page,jobs_per_page=15):
    #First get max number of pages for this job search
    #Each page displays a max of 15 jobs
    searchCountDiv = page.find(name='div', id='searchCountPages')
    if(searchCountDiv is None):
        #No results found for this search result
        return None
    
    #use regex to extract the max # of jobs
    results = re.findall('\d+',str(searchCountDiv.string))
    maxpages = math.ceil(int(results[1]) / jobs_per_page)
    
    return maxpages

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
            soup = BeautifulSoup(company_page.text, 'lxml', from_encoding="utf-8")
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

def extract_requirements(page, match_string = None):
    requirements = []
    for div in page.find_all(name='div', attrs={'class':'row'}):
        a = div.find(name='a', attrs={'data-tn-element':'jobTitle'})
        joblink = "https://ca.indeed.com"+a['href']
        job_page = requests.get(joblink)
        soup = BeautifulSoup(job_page.text, 'lxml', from_encoding="utf-8")

        passed=[]
        col_str = ""
        #Requirement-like titles are usually bolded
        for b in soup.find_all(name='b'):
            #if b.string matches some fuzzy criteria then
            ## TODO FUZZY MATCHING CRITERIA 
            if fuzzy_score(b, match_string) > 80:
                #if match is acceptable add it to list
                passed.append(b)

        if (len(passed) > 0):
            for b in passed:
                #scenario 1 a ul comes right after the title
                ul = b.parent.findNext(name='ul')
                if(ul is None):
                    continue
                #for ul in uls:
                #print(ul)
                for li in ul.findAll('li'):
                    #print(li)
                    if(li.string is not None):
                        col_str = col_str + li.string
                #scenario 2 it is a sequence of divs UNTIL next <b> tag. 
                #May not be able to do anything with this one. It is extremely rare ~2%
        else:
            ul = page.find(name='ul')
            #if ul is None throws exception
            for li in ul.findAll('li'):
                col_str = col_str + li.string
        #if no valid matches then do ul = b.parent.parent.findNext(name='ul') to find first ul in doc.
        #scenario 3, NO <b> tag its just a ul (assume the first)
        
        if(col_str != ""):
            requirements.append(col_str)
        else:    
            requirements.append("Nothing_found")
            
    return requirements

if __name__ == "__main__":
#Eventually use all cities by removing the Vancouver keyword.

    keyword_set = {"data+analyst", "data+scientist", "data+engineer", "software+engineer","software+developer","statistician"}
    columns = ["job_title", "company_name", "requirements", "location","industry", "salary"]
    df = pd.DataFrame(columns = columns)
    jobs_per_page=15
    location = 'Toronto ON'
    for keyword in keyword_set:
        #first do a quick preliminary search to find out how many pages
        page = requests.get("https://ca.indeed.com/jobs?q=" + str(keyword) + 
                            "&l=Vancouver,+BC&radius=0&jt=fulltime")
        soup = BeautifulSoup(page.text, 'lxml', from_encoding="utf-8")
        max_pages = get_maxpages(soup,jobs_per_page)
        if(max_pages is None):
            continue

        for start in range(1, max_pages+1):
            #pages show 15 results at a time

            #start numbers go 0, 10 ,20 ,30 , etc. but shows 15 results per page.
            #e.g. page 3 is start=20
            page = requests.get("https://ca.indeed.com/jobs?q=" + str(keyword) + 
                                "&l=Vancouver,+BC&radius=0&jt=fulltime&start=" + str((start*10)-10))
            soup = BeautifulSoup(page.text, 'lxml', from_encoding="utf-8")
            
            job_titles = extract_job_title(soup)
            locations = extract_location(soup)
            companies = extract_company(soup)
            salaries = extract_salary(soup)
            industry = extract_industry(soup)
            requirements = extract_requirements(soup)
            print("===========================")
            #The below texts need to come from the specific page for this job
            #requirements = extract_requirements(soup)
            #summaries = extract_summary(soup)
            data = {"job_title":job_titles, "company_name":companies,
                    "requirements":requirements,
                    "location":locations, "industry": industry,
                    "salary":salaries}
            temp_df = pd.DataFrame(data)
            df = df.append(temp_df)
            

