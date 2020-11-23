import pandas as pd
import math
import numpy as np


#### clean the salary 
def convert_salary():

    data = pd.read_csv("data/job_salary.csv")

    salary =  data.salary.tolist()

    #-- convert salary into numbers
    converted_salary = []
    #-- to detect if the salary based on year/month/hour
    y_m_h = []  

    #-- I use 0 to replace "nothing_found", nust for easier converting the salary
    for i in range(len(salary)):
            if salary[i] == "Nothing_found":
                    salary[i] = 0
    
    for i in range(len(salary)):
        if salary[i] == 0: y_m_h.append(0)

        else:
            if salary[i].split('a',1)[1][1:] =='year':
                y_m_h.append(1)
            elif salary[i].split('a',1)[1][1:] ==' hour':
                y_m_h.append(7*30*12)
            elif salary[i].split('a',1)[1][1:] == 'month':
                y_m_h.append(12)
                
            
    for i in range(len(salary)):
        if salary[i] ==0 : pass

        else:
            salary[i] = salary[i].split('a')[0].replace(',', '').replace('$', '')[:-1]


    for i in salary:
        if i ==0 : converted_salary.append(i)

        else:
            a = i.split('-')
            if len(a) == 2: 
                converted_salary.append(np.mean([float(b) for b in a]))
            else:
                #print("pass")
                converted_salary.append(float(a[0]))


    converted_salary = np.multiply(converted_salary, y_m_h).tolist()
    data['salary'] = converted_salary
    data.to_csv("data/clean_job_salary.csv", encoding='utf-8')

convert_salary()
