import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# Function to check and correct the link
def fix_link(link):
    if not link.endswith("dms"):
        link += "/dms"
    return link

# Function to extract the content of the articles and create text files
def extract_content(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all("article", class_="dm-card")

    # Extract title for folder
    title = soup.find("meta", property="og:title")["content"]
    title = title.replace("|", "-").strip()  # Remove invalid characters for folder name
    os.makedirs(title, exist_ok=True)  # Create folder if it doesn't exist

    for i, article in enumerate(articles, start=1):
        content = article.find("div", class_="dm-card__content").text.strip()
        published_date = article.find("div", class_="dm-card__added").text.strip()
        file_title = f"{i}_{published_date.replace(':', '-')}"

        file_path = os.path.join(title, f"{file_title}.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
            file.write(f"\n\nPublished: {published_date}")

# Profile link
link = input('Enter the Profile Link you want to download DMs from: ')
link = fix_link(link)

# Extract content and create text files
extract_content(link)
