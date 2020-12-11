This document will explain how to run the various functionalities of this package. 

Make sure your working directory should be outside of the project. such that if you run ls you will see STA2453_Project1 as one of the folders. Run the web scraper on the command line with

```bash
python -m STA2453_Project1.web_scraping data+scientist -l Toronto,+ON
```

The above command indicates you are scraping with job title "data scientist" and location is set to "Toronto, ON"

The default searching radius is set to 100 kilometers. To change the radius, add -r options as following:

```bash
python -m STA2453_Project1.web_scraping data+scientist -l Toronto,+ON -r 50
```

This changes radius to be 50 kilometers.

To run the unit tests for the web scraper use the following command

```bash
python -m STA2453_Project1.testing.web_scraping_test
```

Notice because this is a package there are no .py extensions.
