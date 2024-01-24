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


def scrape_special_links(soup, base_url: str) -> list:
    special_links = []
    for link in soup.find_all('a', class_='item_label thm-hglight-text_color-hover'):
        href = link.get('href')
        full_url = href if href.startswith('http') else base_url.rstrip('/') + href
        if [full_url, link.text.strip()] not in special_links:
            special_links.append([full_url, link.text.strip()])
    return special_links

def scrape_nested_menu_links(base_url: str, menu_element) -> list:
    menu_urls = []
    for link in menu_element.find_all('a', href=True):
        href = link['href']
        full_url = href if href.startswith('http') else base_url.rstrip('/') + href
        if [full_url, link.text.strip()] not in menu_urls:
            menu_urls.append([full_url, link.text.strip()])

        # Handling nested dropdown menus
        parent_li = link.find_parent('li')
        if parent_li and 'dropdown' in parent_li.get('class', []):
            submenu = parent_li.find('ul', class_='dropdown-menu')
            if submenu:
                menu_urls.extend(scrape_nested_menu_links(base_url, submenu))

    return menu_urls

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
        # Enter the solution into the CAPTCHA input field and submit if necessary
        # This part will vary greatly depending on the website's structure

def get_meta_tags(url, headers):
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Fetching the Meta Title and Description
        title_tag = soup.find('title').text if soup.title else ''

        meta_description = soup.find('meta', {'name': 'description'})
        description = meta_description['content'] if meta_description else ''

        return title_tag, description
    except Exception as e:
        print(f"Error fetching meta tags for URL {url}: {e}")
        return 'Error', 'Error'

def scrape_menu_links(base_url: str, menu_element) -> [str]:
    menu_urls = []
    for link in menu_element.find_all('a', href=True):
        href = link['href']
        if (href.startswith('/') or href.startswith('#')):
            full_url = base_url.rstrip('/') + href
            if [full_url, link.text] not in menu_urls:
                menu_urls.append([full_url, link.text])
    return menu_urls

def scrape_nav_bar_urls(base_url: str, menu_element) -> [str]:
    # Scrape URLs from header navigation
    main_nav_urls = []
    nav_bar = menu_element.find('ul', class_='navbar-nav')  # Assuming the main navigation bar is wrapped in a <nav> tag
    if nav_bar:
        main_nav_urls = scrape_menu_links(base_url, nav_bar)
    else:
        print("No main navigation bar found")
    return main_nav_urls 

def scrape_sub_menu_urls(base_url: str, menu_element, nav_urls) -> [str]:
    nav_bar = menu_element.find('ul', class_='navbar-nav')  # Assuming the main navigation bar is wrapped in a <nav> tag
    if nav_bar:
        submenu_urls = []
        submenus = nav_bar.find_all(class_='submenu-class')  # Adjust the class name to match your HTML structure
        for submenu in submenus:
            submenu_urls += scrape_menu_links(base_url, submenu)

        # Combine Main Navigation and Submenu URLs
        nav_urls = nav_urls + submenu_urls
    return nav_urls
        
def scrape_meta_tags(base_url: str, nav_urls,headers) -> [str]:
    # Scrape Meta Tags for each URL
    data = []
    for url in nav_urls:
        try:
            title_tag, description = get_meta_tags(url[0],headers)
        except ValueError:
            title_tag, description = 'Error', 'Error'
        if url[0].endswith("#"):
            data.append([url[0], url[1],"",""])
        else:
            data.append([url[0], url[1], title_tag, description])
        print(url[0])
    return data

def scrape_website(base_url: str, headers, use_selenium=False) -> list:
    print("Parsing URL")
    try:
        if use_selenium:
            soup = scrape_with_selenium(base_url)
        else:
            response = requests.get(base_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

        # Handle CAPTCHA if present
        handle_captcha(soup)

        # Scraping special links
        special_links = scrape_special_links(soup, base_url)
        if special_links:
            print("Scraping Meta Tags")
            data = scrape_meta_tags(base_url,special_links,headers)
            return data

        main_menu = soup.find('ul', id='menu-main-menu')
        if main_menu:
            print("Scraping Menu URLs")
            nav_urls = scrape_nested_menu_links(base_url, main_menu)
            print("Scraping Meta Tags")
            data = scrape_meta_tags(base_url,nav_urls,headers)
            return data
        else:
            print("No main menu found")
            return []

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

base_url = "https://www.pohankaacura.com/"

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

scrape_with_selenium(base_url)
scraped_data_filename = extract_base_url_name(base_url)
folder_path = scraped_data_filename + "/"
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
dynamic_wait()

scraped_data = scrape_website(base_url, headers, True)
output_filename = os.path.join(folder_path, scraped_data_filename + '_scraped_data.csv')
export_to_csv(scraped_data, filename=output_filename)

print("Scraping completed and data exported to CSV.")
