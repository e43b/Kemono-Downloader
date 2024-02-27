import os
import requests
from bs4 import BeautifulSoup
import time
import re

# Function to extract links from a specific page
def extract_page_links(url):
    # Make the request and get the page content
    print("Requesting", url)
    response = requests.get(url, headers=headers)
    html_content = response.content

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Find all 'article' elements with the class 'post-card' and 'post-card--preview'
    articles = soup.find_all("article", class_="post-card post-card--preview")

    # List to store complete links
    complete_page_links = []

    # Iterate over the found 'article' elements
    for article in articles:
        # Check if the 'article' element does not contain an image
        if not article.find("img", class_="post-card__image"):
            # Find the 'a' element inside the 'article'
            link = article.find("a")
            # Get the href attribute of the link
            href = link.get("href")
            # Add the domain to the link and store it in the list
            complete_link = "https://kemono.su" + href
            complete_page_links.append(complete_link)

    return complete_page_links

# Function to create the main folder
def create_main_folder(page_title):
    main_folder = re.sub(r'[^\w\s]', '', page_title).replace(' ', '_').lower()
    if not os.path.exists(main_folder):
        os.makedirs(main_folder)
    return main_folder

# Base URL of the site
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

# Find the page title from the meta tag
page_title = soup.find("meta", property="og:title")['content']

# Create the main folder based on the page title
main_folder = create_main_folder(page_title)

# Print the main folder title
print("Main folder created:", main_folder)

# Find the <small> tag with the total number of pages
tag_small = soup.find("small")
if tag_small:
    # Extract the text inside the tag
    text = tag_small.get_text(strip=True)
    # Extract the total number of pages
    total_pages = int(text.split()[-1])
    # Calculate the maximum number of pages to be analyzed
    max_pages = (total_pages - 1) // 50 + 1

    print(f"Total number of pages: {total_pages}")
    print(f"Maximum number of pages to be analyzed: {max_pages}")

    # List to store all complete links
    all_complete_links = []

    # Extract links from the first page
    links_first_page = extract_page_links(url_first_page)
    all_complete_links.extend(links_first_page)

    # Save links from the first page to a text file
    with open(os.path.join(main_folder, "extracted_links.txt"), "w") as f:
        for link in links_first_page:
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
    print(f"Total links ignored due to having images: {total_ignored_links}")

    # Loop to access each extracted link and extract content
    for link in all_complete_links:
        # Make the HTTP request
        response = requests.get(link)

        # Check if the request was successful
        if response.status_code == 200:
            # Get the HTML content
            html_content = response.text

            # Parse the HTML content
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract the title from the <title> tag
            title_tag = soup.find('title').text.strip()

            # Remove invalid characters for file name
            invalid_chars = '\\/:*?"<>|'
            for char in invalid_chars:
                title_tag = title_tag.replace(char, '')

            # Extract the post title
            title = title_tag.split(' | ')[0]

            # Extract the publication date
            published = soup.find('div', class_='post__published').text.strip().split(': ')[1]

            # Extract the content keeping the formatting
            content = soup.find('div', class_='post__content').get_text(separator='\n')

            # Extract download links, if any
            downloads = ""
            downloads_section = soup.find('h2', string='Downloads')
            if downloads_section:
                download_links = downloads_section.find_next('ul', class_='post__attachments').find_all('a', class_='post__attachment-link')
                for link in download_links:
                    downloads += f"Download Link: {link['href']}\n"

            # Extract comments
            comments = ""
            comments_section = soup.find('footer', class_='post__footer')
            if comments_section:
                comments_header = comments_section.find('h2', class_='site-section__subheading')
                if comments_header and comments_header.text.strip() == 'Comments':
                    comment_articles = comments_section.find_all('article', class_='comment')
                    for article in comment_articles:
                        commenter = article.find('a', class_='fancy-link fancy-link--local comment__name').text.strip()
                        comment_message = article.find('p', class_='comment__message').text.strip()
                        comment_time = article.find('time', class_='timestamp').text.strip()
                        comments += f"Comment by {commenter} ({comment_time}):\n{comment_message}\n\n"

            # Name the file with the post title
            file_name = os.path.join(main_folder, "{}.txt".format(title))

            # Save the content in a text file keeping the formatting
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write("Title: {}\n".format(title))
                file.write("\nPublished Date: {}\n".format(published))
                file.write("\nContent:{}\n".format(content))
                if downloads:
                    file.write("\nDownloads:\n{}".format(downloads))
                if comments:
                    file.write("\nComments:\n{}".format(comments))

            print("Post content saved successfully to '{}'.\n".format(file_name))
        else:
            print("Error accessing the page:", response.status_code)
        # Wait for a brief interval to avoid overloading the server
        time.sleep(1)
else:
    print("Unable to find information about the total number of pages.")
