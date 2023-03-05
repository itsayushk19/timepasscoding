This program is a web scraper that uses the Python libraries newspaper, requests, and fake_useragent to scrape news articles from the internet and save them to a MySQL database. The program is split into two files: database.py and main.py.

database.py contains a MySQL connection pool setup and a function save_article_to_db that inserts data into the MySQL database. The function first checks whether the URL is valid and has enough words in the title, and if it passes these tests, it parses the domain name from the URL and executes an INSERT statement with the article's title, domain, keywords, URL, text, description, summary, category, and top image.

main.py contains the main web scraping logic. It reads in a list of previously scraped URLs, initializes a queue of URLs to scrape, and defines a function scrape_url that takes a URL from the queue, scrapes the article from the website, and saves it to the database using the save_article_to_db function. The scrape_url function also handles proxy rotation and URL skipping if the URL has already been scraped. The program dynamically calculates the wait period based on server response time, and saves scraped URLs and rejected URLs to files. Finally, the program prints status updates to the console.:

1. Title
2. Domain 
3. Keywords (Generated Using Newspaper3k Natural Language Processing)
4. URL of article
5. Text Content of Article
6. Description (Meta Description, if available)
7. Summary (Summary of the article, Generated using Newspaper3k NLP)
8. Category (Article Categorization using NLP)
9. Top Image (Main featured image of the article)

How to use it:
1. Clone it to your computer using "git clone https://github.com/itsayushk19/timepasscoding" or just download it from this repository
2. Save URLs of the articles you want to scrape in the "urls" folder or wherever you want
3. Install database module by running "pip install ."
4. (You might wan't to start a local MySQL Server using XAMPP or some other server, create a database called "articles" & edit the database credentials in database/database.py)
5. Create the database table "articles" by importing the table_schema.sql file by opening the MySQL phpmyadmin panel or whichever way you want (located inside database/table_schema.sql)
6. Run the following command from the root dir of the project "python main.py <path to dir containing url text files> <number of threads you want to start>"

Features:
1.Connection Pooling: The program uses a MySQL connection pool to manage connections to the database. Connection pooling allows for efficient use of database resources and reduces the overhead of creating and tearing down connections for each query.

2. You might not want to store static pages like "about us" and other archieve pages if links to them are present in your lakhs long lines of URLs as you most probably had this URL collection system automated. To filter this out, this program is filtering those article that have titles short than 5-6 words as 99% of article are likely to violate this line. The program also checks if the "URL" field is filled & contains a valid URL, otherwise it rejects those URLs from saving them to DB. 

3.Article Scraper: The program uses the newspaper library to scrape articles from web pages. The library allows for easy extraction of article metadata and content, as well as natural language processing.

4.User Agent Rotation: The program uses the fake_useragent library to rotate user agents between requests. This helps to avoid detection and prevent blocking by websites that impose rate limits.

5.Proxy Rotation: The program uses the Proxyscrape API to obtain a list of proxy servers, and selects a random proxy server to use for each request. This helps to avoid detection and prevent blocking by websites that impose rate limits. To avoid overwhelming the Proxyscrape API and potentially getting timed out, take the list of proxies from proxyscrape, rotate through that list & refreshed the proxy list only after every 30 minutes which is set by the line "CACHE_DURATION = 30 * 60"

6.Multithreading: The program uses threads to scrape multiple URLs simultaneously. This allows for faster scraping of large numbers of URLs.

7.URL Queue: The program uses a queue to manage the URLs that need to be scraped. This allows for efficient processing of large numbers of URLs.

8.Timeout Settings: The program sets a base timeout of 2 seconds which is used to dynamically set buffer time between each request based on the response time of the website.

9.Logging: The program logs scraped URLs, rejected URLs, and any errors that occur during scraping to separate files. This allows for easy analysis and troubleshooting of the scraping process.

10.Error Handling: The program uses error handling to catch and log any exceptions that occur during scraping. This helps to prevent the program from crashing and allows for easy troubleshooting. In case a website blocks the crawler, it sets a auto-retry with incrementing timeout that doubles after each failed URL until, it's accessible for max 50 retries, after that it logs the url to failed_urls.txt and moves on

Summary:
Overall the program is quite messy, i should've distributed in various modules than stuffing it all in a main.py and it may or may not have bugs or issues as i've really not looked into that yet but, it gets the work done. If you have a set of URLs of website articles you want to scrape from this could be the solution to your problem. It's got all features you might want weather it's User Agent & IP Rotating or Multi-threading. It handles the issues very well, but settings automatic timeout to not miss any URL as it may get hard to analyse what URLs have been missed when there's millions of them but it handles it well by providing enought retries and still if that's not working, it logs the URL for you to have a look later and moves on. I'll also be sharing an update of this file in a few days for better improved crawling speed & in-built indexer that automatically gets the links of all articles on a site using sitemaps or newspapers3k if sitemap is not availabls.
