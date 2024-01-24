import requests
import os
import time
import re
import csv
import random
from bs4 import BeautifulSoup
from twocaptcha import TwoCaptcha
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

time_start = time.time()

# Setup Selenium Chrome web driver
def setup_selenium():
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920x1080")
    driver = webdriver.Chrome(options=options)
    return driver 

# Get Soup with Selenium
def scrape_with_selenium(url):
    driver = setup_selenium()
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    return soup

# Find URL list
def scrape_page_for_urls(soup, base_url:str, container_tag, container_class, link_tag: str ='a') -> list:
    containers = soup.find_all(container_tag, class_=container_class)
    nav_urls = []
    if containers:
        print("Scraping homepage for Nav URLs")
        for container in containers:
            links = container.find_all(link_tag, href=True)
            for link in links:
                href = link.get('href')
                full_url = href if href.startswith('http') else base_url.rstrip('/') + href
                if [full_url, link.text.strip()] not in nav_urls:
                    nav_urls.append([full_url, link.text.strip()])
        return nav_urls if nav_urls != [] else None

# Get meta tags (title and description) from urls
def get_title_description_meta_tags(url):
    try:
        if with_selenium:
            soup = scrape_with_selenium(url)
        else:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

        # Fetching the Meta Title and Description
        title_tag = soup.find('title').text if soup.title else ''
        meta_description = soup.find('meta', {'name': 'description'})
        description = meta_description['content'] if meta_description else ''
        return title_tag, description

    except Exception as e:
        print(f"Error fetching meta tags for URL {url}: {e}")
        return 'Error', 'Error'

# build final rows for csv
def scrape_urls_for_title_and_description_tags(nav_urls) -> [str]:
    # Scrape Meta Tags for each URL
    if nav_urls:
        print("Scraping URLs for Title and Description Tags")
        data = []
        for url in nav_urls:
            try:
                title_tag, description = get_title_description_meta_tags(url[0])
            except ValueError:
                title_tag, description = 'Error', 'Error'
            if url[0].endswith("#"):
                data.append([url[0], url[1],"",""])
            else:
                data.append([url[0], url[1], title_tag, description])
            print()
            print(url[0])
            print(url[1])
            print(title_tag)
            print(description)
            print()
        return data
    else:
        return None

# Scrape website to get navigation URLs
def scrape_website(base_url: str, headers, use_selenium=False) -> list:
    try:
        if use_selenium:
            soup = scrape_with_selenium(base_url)
        else:
            response = requests.get(base_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
        
        for flags in container_tag_flags:
            # Scraping 'levellandchevrolet.com' <div class="header-navigation clearfix" links
            nav_urls = scrape_page_for_urls(soup, base_url, flags[0], flags[1])
            data = scrape_urls_for_title_and_description_tags(nav_urls)
            if data:
                return data     
        
    except Exception as e:
        print(f"Error parsing URL {base_url}: {e}")
        return []
    
def export_to_csv(data, filename='output.csv'):
    print("Exporting to CSV")
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['URL', 'Link Text', 'Meta Title', 'Meta Description'])
        writer.writerows(data)

def extract_base_url_name(url):
    match = re.search(r'://www\.(.*?)\.', url)
    return match.group(1)

def dynamic_wait():
    time.sleep(random.uniform(1,3))







# Main execution
solver = TwoCaptcha('3dc50ff10c3c15cd101490da3faf3c56')

base_url = "https://www.levellandchevrolet.com/"

container_tag_flags = [('div', 'header-navigation clearfix'), 
                       ('banner', 'banner'),
                       ('div', 'megamenu_navigation_container megamenu_nested')
                       ]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

with_selenium = False

scraped_data_filename = extract_base_url_name(base_url)
folder_path = scraped_data_filename + "/"
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
# dynamic_wait()

print("Parsing Homepage wtihout Selenium")
scraped_data = scrape_website(base_url, headers, with_selenium)
if scraped_data == None:
    with_selenium = True
    print("Parsing Homepage with Selenium")
    scraped_data = scrape_website(base_url, headers, True)
if scraped_data == None:
    scraped_data = [["Nothing was scraped!","Check that there are valid container tags for specified URL."]]


output_filename = os.path.join(folder_path, scraped_data_filename + '_scraped_data.csv')
export_to_csv(scraped_data, filename=output_filename)
print("Scraping completed and data exported to CSV.")

time_end = time.time()
time_execution = time_end - time_start
time_execution = f"{time_execution} seconds" if time_execution < 60 else f"{time_execution // 60} minutes"
print(f"This script took {time_execution} to complete.")








"""

# Handle CAPTCHA if present
# handle_captcha(soup)


# Solve Captcha
def solve_captcha(captcha_image_url) -> str:
    try:
        result = solver.solve_and_return_solution(captcha_image_url)
        if result != 0:
            print("CAPTCHA solved:", result)
            return result
        else:
            print("Failed to solve CAPTCHA")
            return ""
    except Exception as e:
        print("Error solving CAPTCHA:", e)
        return ""

def handle_captcha(soup):
    # This is an example, adjust based on how the CAPTCHA appears on your target website
    captcha_image = soup.find('img', {'id': 'captchaImage'})
    if captcha_image:
        captcha_url = captcha_image['src']
        captcha_solution = solve_captcha(captcha_url)
"""