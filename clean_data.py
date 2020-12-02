import pandas as pd
import math
import numpy as np
from fuzzywuzzy import process
import re
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))

#### clean the salary 
def convert_salary(data):

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
        
        
        if salary[i].split('a',1)[1][1:] =='year':
            y_m_h.append(1)
        elif salary[i].split('a',1)[1][1:] ==' hour':
            y_m_h.append(7*30*12)
        else:
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
    return data




# return a data frame
def clean_requirements(data):
    # clean requirements
    requirements = data['requirements']
    requirements_cleaned = []
    for i, text in enumerate(requirements):
        # changing all words to lower case
        text = text.lower()
        # changing multiple lines to one line
        text = text.replace("\n", " ")
        # removing all punctuations
        text = re.sub("[^a-z]", " ", text)
        # removing stop words
        text = ' '.join([word for word in text.split() if word not in stop_words])
        requirements_cleaned.append(text)

    bigram_vectorizer = CountVectorizer(ngram_range=(1, 2), max_features=1000)
    bigram = bigram_vectorizer.fit_transform(requirements_cleaned)
    feature_names = bigram_vectorizer.get_feature_names()
    df = pd.DataFrame(bigram.toarray(), columns=feature_names)
    data['requirements_cleaned'] = np.array(requirements_cleaned)
    data = pd.concat([data, df], axis=1)
    return data
