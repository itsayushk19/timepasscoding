import time, random, threading, queue, glob, requests, sys, os, subprocess, math, datetime, newspaper
from urllib.parse import urlparse
from newspaper import Article
from newspaper import Config
from fake_useragent import UserAgent
import requests
from database import save_article_to_db
from colorama import init, Fore, Back

init()
start_time = time.time()
now = datetime.datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

# Set up user agent rotation using fake_useragent library
ua = UserAgent()

# set cache duration to 30 minutes
CACHE_DURATION = 30 * 60

# Define global variables
url_queue = queue.Queue()
scraped_urls = set()
failed_urls = set()

# Read in a file of previously scraped URLs, if it exists
scraped_urls = set()
try:
    with open('scraped_urls.txt', 'r') as f:
        for line in f:
            scraped_urls.add(line.strip())
except FileNotFoundError:
    pass

from colorama import init, Fore, Back, Style

# Define lists to keep track of scraped and failed URLs
failed_urls = []

# URL of the Proxyscrape API to get a list of proxy servers
proxyscrape_url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"

# Initialize the proxy list and timestamp of last update
proxy_list = []
last_update_time = 0

def get_proxy():
    global proxy_list, last_update_time
    
    # Check if the proxy list needs to be updated
    current_time = time.time()
    if current_time - last_update_time > 1800: # update every 30 minutes
        response = requests.get(proxyscrape_url)
        if response.status_code == 200:
            # Split the response by line and update the proxy list
            proxy_list = response.text.strip().split('\n')
            last_update_time = current_time
            print("Updated proxy list from Proxyscrape")

    # Return a random proxy server from the list
    if len(proxy_list) > 0:
        return {"http": "http://" + random.choice(proxy_list)}
    else:
        return None

def scrape_url(url):

    wait_period = 2
    max_retries = 10
    num_retries = 0

    # Get a random proxy server from Proxyscrape
    proxy = get_proxy()
    # Skip the URL if it has already been scraped
    if url in scraped_urls:
        print(f"\r{Style.BRIGHT}{Fore.GREEN}Skipping {Style.RESET_ALL} |{Fore.RED}(already scraped){Style.RESET_ALL}|          -----          {url}")
        return
    while True:
        try:
            # Rotate user agent
            config = Config()
            config.browser_user_agent = ua.random

            # Print current IP and user agent being used
            response = requests.get(url, proxies=proxy, timeout=3)

            print("Using IP:", proxy["http"].split("//")[1].rstrip())
            print("User agent:", config.browser_user_agent)

            article = Article(url, config=config)
            article.download(input_html=response.text)
            article.parse()
            article.nlp()

            end_time = time.time()

            # Store the data to MySQL database
            save_article_to_db(article)

            # Save scraped URL to file
            with open("scraped_urls_{timestamp}.txt", "a") as f:
                f.write(url + "\n")

            # Add URL to scraped URLs list
            scraped_urls.add(url)

            # Print status

            # Calculate wait period dynamically based on server response time
            urls_remaining = url_queue.qsize()
            elapsed_time = end_time - start_time
            time_remaining = urls_remaining * (end_time - start_time + wait_period)
            estimated_time = time.strftime("%H:%M:%S", time.gmtime(time_remaining))
            wait_period = max(0, 6 - (end_time - start_time)) + 1
            
            # Define color and style constants
            COLOR_YELLOW = "\033[33m"
            COLOR_GREEN = "\033[32m"
            COLOR_RED = "\033[31m"
            COLOR_RESET = "\033[0m"
            STYLE_BOLD = "\033[1m"

            # Group related statements together
            status_line = f"Scraped {COLOR_YELLOW}(Sleeping for {wait_period} seconds...){COLOR_RESET}\n"
            separator_line = "--------------------------------------------------------------------------------------------------\n"
            progress_line = f"Elapsed time: {STYLE_BOLD}{COLOR_GREEN}{elapsed_time:.2f}s{COLOR_RESET}/{STYLE_BOLD}Estimated time remaining: {COLOR_RED}{estimated_time}{COLOR_RESET}/"
            url_line = f"{STYLE_BOLD}{COLOR_GREEN}Scraping{COLOR_RESET} {url}\n"

            # Print the formatted output
            print(status_line + separator_line + progress_line, end="\r", flush=True)
            print(url_line)

            break
        except requests.exceptions.Timeout:
            # Timeout occurred, retry with longer timeout
            if num_retries < max_retries:
                print(f"Timeout occurred while scraping {url}, retrying with timeout {wait_period}...",)
                num_retries += 1
                time.sleep(6)
            else:
                print(f"Maximum number of retries reached for {url}, adding to failed URLs file...")
                failed_urls.append(url)
                with open("failed_urls_{timestamp}.txt", "a") as f:
                    f.write(url + "\n")
                # Add URL to scraped URLs list to prevent it from being scraped again
                scraped_urls.add(url)
                break
        except Exception as e:
            print(f"Error occurred while scraping {url}: {e}",)
            failed_urls.append(url)
            with open("failed_urls_{timestamp}.txt", "a") as f:
                f.write(url + "\n")
            # Add URL to scraped URLs list to prevent it from being scraped again
            scraped_urls.add(url)
            # Wait for 5 seconds before scraping the next article
            wait_period = 5
            break

last_text_file = None

def worker():
    # Loop until there are no more URLs in the queue
    while True:
        try:
            # Get the next URL from the queue
            url, text_file = url_queue.get_nowait()

            # Check if the text file is different from the last one used
            global last_text_file
            if text_file != last_text_file:
                # Switch to the next available text file
                text_files = [t[1] for t in list(url_queue.queue)]
                text_files.append(text_file)
                text_files = list(set(text_files))
                idx = text_files.index(text_file)
                next_idx = (idx + 1) % len(text_files)
                next_text_file = text_files[next_idx]
                last_text_file = next_text_file

            # Scrape the URL
            scrape_url(url)
        except queue.Empty:
            # If the queue is empty, exit the loop
            break

def main():
    # Get the directory path and number of threads from command line arguments
    if len(sys.argv) != 3:
        print("Usage: python script.py <directory_path> <num_threads>")
        sys.exit(1)

    dir_path = sys.argv[1]
    num_threads = int(sys.argv[2])

    # Get a list of all .txt files in the directory
    text_files = glob.glob(os.path.join(dir_path, "*.txt"))
    num_files = len(text_files)

    # Initialize thread list
    threads = []

    # Divide the text files evenly between the threads
    files_per_thread = num_files // num_threads
    leftover_files = num_files % num_threads

    # Loop through each thread
    for i in range(num_threads):
        thread_files = []

        # Determine the text files assigned to this thread
        if i < leftover_files:
            start_file = i * (files_per_thread + 1)
            end_file = start_file + files_per_thread
        else:
            start_file = i * files_per_thread + leftover_files
            end_file = start_file + files_per_thread - 1
        assigned_files = text_files[start_file:end_file+1]

        # Enqueue URLs from the assigned text files for this thread
        for text_file in assigned_files:
            with open(text_file, 'r') as f:
                urls = f.read().splitlines()
            thread_files.append(text_file)
            for url in urls:
                url_queue.put((url, text_file))

        # Create and start the thread
        thread = threading.Thread(target=worker)
        thread.start()
        threads.append(thread)

    # Wait for all tasks to be processed
    for thread in threads:
        thread.join()

    print("All URLs have been scraped.")

if __name__ == '__main__':
    # Create a queue to hold the URLs
    url_queue = queue.Queue()
    main()