This document will explain how to run the various functionalities of this package. 

Firstly, to run the main web_scraping functionality create a folder named data at the root directory of this project. The structure should look like STA2453_Project1/data/ .

Next cd directory to be outside of the project. such that if you run ls you will see STA2453_Project1 as one of the folders. Run the web scraper on the command line with

```bash
python -m STA2453_Project1.web_scraping
```

To run the unit tests for the web scraper use the following command

```bash
python -m STA2453_Project1.testing.web_scraping_test
```

Notice because this is a package there are no .py extensions.