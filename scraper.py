import requests
import os
import time
import re
import csv
from bs4 import BeautifulSoup

def get_meta_tags(url):
    try:
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
        
def scrape_meta_tags(base_url: str, nav_urls) -> [str]:
    # Scrape Meta Tags for each URL
    data = []
    for url in nav_urls:
        try:
            title_tag, description = get_meta_tags(url[0])
        except ValueError:
            title_tag, description = 'Error', 'Error'
        if url[0].endswith("#"):
            data.append([url[0], url[1],"",""])
        else:
            data.append([url[0], url[1], title_tag, description])
        print(url[0])
    return data

def scrape_website(base_url: str) -> [str]:
    print("Parsing URL")
    try:
        response = requests.get(base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Error parsing URL {base_url}: {e}")
        return []

    # Scrape URLs from header navigation
    print("Scraping Main Navigation URLs")
    nav_urls = scrape_nav_bar_urls(base_url, soup)
    if nav_urls:
        print("Scraping Submenu URLs")
        nav_urls = scrape_sub_menu_urls(base_url, soup, nav_urls)
        print("Scraping Meta Tags")
        data = scrape_meta_tags(base_url, nav_urls)
        return data
    else:
        nav_urls = scrape_menu_links(base_url, soup)
        data = scrape_meta_tags(base_url, nav_urls)
        return data
    
def export_to_csv(data, filename='output.csv'):
    print("Exporting to CSV")
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['URL', 'Link Text', 'Meta Title', 'Meta Description'])
        writer.writerows(data)

def extract_base_url_name(url):
    match = re.search(r'://www\.(.*?)\.', url)
    return match.group(1)

# Main execution
base_url = "https://www.levellandchevrolet.com/"
scraped_data_filename = extract_base_url_name(base_url)
folder_path = scraped_data_filename + "/"
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
scraped_data = scrape_website(base_url)
output_filename = os.path.join(folder_path, scraped_data_filename + '_scraped_data.csv')
export_to_csv(scraped_data, filename=output_filename)

print("Scraping completed and data exported to CSV.")
