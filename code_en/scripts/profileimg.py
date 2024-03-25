from bs4 import BeautifulSoup
import requests
import time
import os
import logging
import re
from urllib.parse import urlparse

# Configuring logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to extract links from a specific page
def extract_page_links(url):
    # Make the request and get the page content
    print("Requesting", url)
    response = requests.get(url, headers=headers)
    html_content = response.content

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Find all 'article' elements with class 'post-card' and 'post-card--preview'
    articles = soup.find_all("article", class_="post-card post-card--preview")

    # List to store complete links
    complete_page_links = []

    # Iterate over found 'article' elements
    for article in articles:
        # Check if the 'article' element contains an image
        if article.find("img", class_="post-card__image"):
            # Find the 'a' element inside the 'article'
            link = article.find("a")
            # Get the href attribute of the link
            href = link.get("href")
            # Add the domain to the link and store it in the list
            complete_link = "https://kemono.su" + href
            complete_page_links.append(complete_link)

    return complete_page_links

def sanitize_filename(filename):
    """Remove special characters from a file name."""
    return re.sub(r'[<>:"/\\|?*]', '', filename)

# Base URL of the profile
url_base = input('Enter the Profile Link you want to download the posts from: ')

# Browser header
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.4535.0 Safari/537.36"
}

# Make the request and get the content of the first page
url_first_page = url_base
response = requests.get(url_first_page, headers=headers)
html_content = response.content

# Parse the HTML content
soup = BeautifulSoup(html_content, "html.parser")

# Find the <title> tag to get the main page title
title_tag = soup.find("title")
if title_tag:
    # Extract the text inside the tag
    title = title_tag.text.strip()
    # Sanitize the title to remove special characters
    title = sanitize_filename(title)
else:
    # If <title> tag is not found, set a default title
    title = "Posts"

# Create a main folder with the title of the main page
main_folder = os.path.join(os.getcwd(), title)
os.makedirs(main_folder, exist_ok=True)

# Find the <small> tag with the total number of pages
tag_small = soup.find("small")
if tag_small:
    # Extract the text inside the tag
    text = tag_small.get_text(strip=True)
    # Extract the total number of pages
    total_pages = int(text.split()[-1])
    # Calculate the maximum number of pages to be analyzed
    max_pages = (total_pages - 1) // 50 + 1

    print(f"\nTotal number of pages: {total_pages}")
    print(f"Maximum number of pages to be analyzed: {max_pages}\n")

    # List to store all complete links
    all_complete_links = []

    # Extract links from the first page
    links_first_page = extract_page_links(url_first_page)
    all_complete_links.extend(links_first_page)

    # Save links from the first page to a text file
    with open(os.path.join(main_folder, "extracted_links.txt"), "w") as f:
        for link in all_complete_links:
            f.write(link + "\n")

    # Counters for extracted and ignored links
    total_extracted_links = len(links_first_page)
    total_ignored_links = 50 - len(links_first_page)

    # Loop to navigate through remaining pages and extract links
    for page_number in range(1, max_pages):
        # Calculate the offset 'o' for the current page
        offset = page_number * 50
        # Build the URL of the current page
        url_page = f"{url_base}?o={offset}"

        # Extract links from the current page
        page_links = extract_page_links(url_page)
        all_complete_links.extend(page_links)

        # Update links in the text file
        with open(os.path.join(main_folder, "extracted_links.txt"), "a") as f:
            for link in page_links:
                f.write(link + "\n")

        # Update counters
        total_extracted_links += len(page_links)
        total_ignored_links += 50 - len(page_links)

    # Print statistics
    print(f"Total extracted links: {total_extracted_links}")
    print(f"Total links ignored due to lack of image: {total_ignored_links}\n")
else:
    print("Unable to find information about the total number of pages.")

# Loop to download posts from each extracted link
for link in all_complete_links:
    try:
        response = requests.get(link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            title_tag = soup.find("title")
            title = title_tag.text.strip()
            title = title.split("by")[0].strip().replace(" ", "_")
            title = sanitize_filename(title)
            title = title[:45]
            # Create a folder for the post inside the main folder
            post_folder = os.path.join(main_folder, title)
            os.makedirs(post_folder, exist_ok=True)
            file_thumb_links = soup.find_all("a", class_="fileThumb")
            for idx, link in enumerate(file_thumb_links):
                image_url = link["href"]
                _, ext = os.path.splitext(os.path.basename(urlparse(image_url).path))
                image_path = os.path.join(post_folder, f"{idx + 1}{ext}")
                # Check if the file already exists
                if not os.path.exists(image_path):
                    print(f"Image {idx + 1} of {title} downloading...")
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        with open(image_path, "wb") as f:
                            f.write(image_response.content)
                        print(f"Image {idx + 1} of {title} downloaded.")
                    else:
                        logging.error(f"Failed to download image from: {image_url}")
                else:
                    print(f"Image {idx + 1} of {title} already exists. Skipping download.")
        else:
            logging.error(f"Failed to access the page: {link}\n")
    except:
        print('Something error happen. Continue...')
