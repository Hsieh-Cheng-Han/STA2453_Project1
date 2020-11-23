import unittest
import pickle
import os
from STA2453_Project1.web_scraping_config import match_list
from STA2453_Project1.web_scraping import fuzzy_match, get_matches, extract_requirements, get_col_str, get_maxpages, adjust_maxpages, get_maxjobs
#import fuzzy_match, get_matches, extract_requirements, get_col_str, get_maxpages, adjust_maxpages, get_maxjobs

from bs4 import BeautifulSoup

class AdjustMaxPagesTest(unittest.TestCase):
    def setUp(self):
        print(os.getcwd())
        with open("STA2453_Project1/testing/lastpagevancouversdev.html", "r") as f:
            self.last_page = BeautifulSoup(f, 'lxml')
    def test_adjust_maxpages_VancouverData1(self):
        num = adjust_maxpages(self.last_page,68,1012,15)
        self.assertEqual(50,num)

class GetMaxJobsTest(unittest.TestCase):
    def setUp(self):
        with open("STA2453_Project1/testing/vancouverlistingssoup.html", 'r') as f:
            self.dslistings = BeautifulSoup(f, 'lxml')
        with open("STA2453_Project1/testing/vancouversdevlistingssoup.html", 'r') as f:
            self.sdevlistings = BeautifulSoup(f, 'lxml')

    def test_get_maxjobs_VancouverData1(self):
        num = get_maxjobs(self.dslistings)
        self.assertEqual(44, num)
    def test_get_maxjobs_VancouverData2(self):
        num = get_maxjobs(self.sdevlistings)
        self.assertEqual(1012,num)
    

class GetMaxPagesTest(unittest.TestCase):
    def test_get_maxpages_VancouverData1(self):
        num = get_maxpages(43)
        self.assertEqual(3,num)
    def test_get_maxpages_VancouverData2(self):
        num = get_maxpages(1012)
        self.assertEqual(68, num)

class GetColStrTestCase(unittest.TestCase):
    def setUp(self):
            with open("STA2453_Project1/testing/vancouverdsjobsoup.pickle", "rb") as f:
                self.page = pickle.load(f)
    def test_get_col_str_Data1(self):
        passed = get_matches(self.page, match_list)
        str1 = "2+ years of industry experience in large-scale ML modelling and engineering, preferably in deep learning.Expertise in software engineering at scale, along with proficiency in using industry-standard development tools such as Git, and being comfortable using Linux command-line tools.Proficiency in Python development, and the usage of libraries such as NumPy, Pandas, and TensorFlow.Proficiency in C (and familiarity with C++).Understanding of basic signal processing concepts, such as signal statistics and the Fourier transform.Ph.D. or M.S. in mathematics, physics, engineering, or another quantitative discipline.Eligible to work in CanadaExposure to database systems and familiarity with SQL.Experience deploying ML models using libraries such as TensorRT."
        self.assertEqual(str1,get_col_str(self.page,passed))

class GetMatchesTestCase(unittest.TestCase):
    def setUp(self):
            with open("STA2453_Project1/testing/vancouverdsjobsoup.pickle", "rb") as f:
                self.page = pickle.load(f)
    def test_get_matches_VancouverData1(self):
        matches = get_matches(self.page,match_list)
        self.assertEqual(2,len(matches))
        self.assertEqual('Required Qualifications', matches[0].text)
        self.assertEqual('Preferred Qualifications', matches[1].text)



class FuzzyMatchTestCase(unittest.TestCase):
    def test_fuzzy_match_True(self):
        self.assertEqual([False,False,False,True,True,False,False,False,False,False],fuzzy_match("requirements",match_list))
    def test_fuzzy_match_musthave(self):
        self.assertNotEqual([False,False,False,False,False,False,False,False,False,False],fuzzy_match("must have",match_list))
        self.assertEqual([False,True,False,False,False,False,False,False,False,False],fuzzy_match("must have",match_list))
    def test_fuzzy_match_Data1(self):
        self.assertEqual([False,False,True,True,False,False,False,False,False,False],fuzzy_match("required qualifications",match_list))
        self.assertEqual([False,False,True,False,False,False,False,False,False,False],fuzzy_match("preferred qualifications",match_list))

if __name__ =='__main__':
    unittest.main()