import argparse
import os
import pathlib
import urllib

import dotenv
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

BASE_URL = "https://tululu.org"


def parse_book_page(scraped_page, url):
    soup = BeautifulSoup(scraped_page, "lxml")
    title, author = [
        element.strip() for element in soup.find("h1").text.split("::")
    ]
    image = urllib.parse.urljoin(
        url, soup.select_one(".bookimage img")["src"]
    )
    comments = [
        element.find("span", class_="black").text
        for element in soup.find_all("div", class_="texts")
    ]
    genres = [
        element.text
        for element in soup.find("span", class_="d_book").find_all("a")
    ]
    return {
        "title": title,
        "author": author,
        "image": image,
        "comments": comments,
        "genres": genres
    }


def get_url_for_scraping(id):
    safe_id = urllib.parse.quote(str(id))
    safe_url = f"{BASE_URL}/b{safe_id}/"
    return safe_url


def get_scraped_page(url_for_scraping):
    response = requests.get(url_for_scraping)
    response.raise_for_status()
    check_for_redirect(response)
    return response.text


def get_url_for_download_txt(id):
    url = f"{BASE_URL}/txt.php"
    params = {
        "id": id
    }
    parsed_url = urllib.parse.urlparse(url)
    encoded_params = urllib.parse.urlencode(params)
    full_url = urllib.parse.urlunparse(
        parsed_url._replace(query=encoded_params)
    )
    return full_url


def get_filename_from_url(url):
    split_url = urllib.parse.urlsplit(url)
    path = split_url.path
    filename = path.split("/")[-1]
    return urllib.parse.unquote(filename)


def download_image(url, folder="images/"):
    response = requests.get(url)
    response.raise_for_status()
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
    filename = get_filename_from_url(url)
    filepath = os.path.join(folder, filename)
    with open(filepath, "wb") as file:
        file.write(response.content)
    return filepath


def download_txt(url, filename, folder="books/"):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)

    filename_without_extension, _ = os.path.splitext(filename)
    cleaned_filename = sanitize_filename(filename_without_extension)
    final_filename = cleaned_filename + ".txt"

    filepath = os.path.join(folder, final_filename)

    with open(filepath, "wb") as file:
        file.write(response.content)

    return filepath


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError(response=response)


def main():
    dotenv.load_dotenv()
    books_directory = os.getenv("BOOKS_DIRECTORY", "books")
    images_directory = os.getenv("IMAGES_DIRECTORY", "images")

    parser = argparse.ArgumentParser(
        description="Script for downloading books from tululu.org."
    )
    parser.add_argument(
        "start_id",
        nargs="?",
        default=1,
        type=int,
        help="ID of first book to download, default is 1."
    )
    parser.add_argument(
        "end_id",
        nargs="?",
        default=10,
        type=int,
        help="ID of last book to download, default is 10."
    )
    args = parser.parse_args()
    start_id, end_id = args.start_id, args.end_id
    for current_id in range(start_id, end_id + 1):
        url_for_scraping = get_url_for_scraping(current_id)
        try:
            scraped_page = get_scraped_page(url_for_scraping)
        except requests.HTTPError:
            continue
        book_details = parse_book_page(
            scraped_page,
            url_for_scraping
        )
        download_image(book_details["image"], images_directory)

        try:
            downloaded = download_txt(
                url=get_url_for_download_txt(current_id),
                filename=f"{current_id}. {book_details['title']}.txt",
                folder=books_directory,
            )
        except requests.HTTPError:
            continue

        title = book_details["title"]
        author = book_details["author"]
        genres = book_details["genres"]
        print(
            f"Название: {title}",
            f"Автор: {author}",
            f"Жанры: {', '.join(genre.lower() for genre in genres)}",
            f"Файл: '{downloaded}'",
            sep="\n",
            end="\n\n",
        )


if __name__ == "__main__":
    main()
