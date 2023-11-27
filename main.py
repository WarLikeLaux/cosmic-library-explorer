import argparse
import os
import pathlib
import sys
import time
import urllib

import dotenv
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

BASE_URL = "https://tululu.org"


class BookNotFoundException(Exception):
    def __init__(self, message="Book not found, redirect occurred."):
        self.message = message

    def set_book_id(self, book_id):
        self.message = f"Book with ID {book_id} not found, redirect occurred."

    def __str__(self):
        return self.message


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


def get_scraped_page(url_for_scraping, limits):
    response = make_request_with_backoff(url_for_scraping, limits=limits)
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


def download_image(url, limits, folder="images/"):
    response = make_request_with_backoff(url, limits=limits)
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
    filename = get_filename_from_url(url)
    filepath = os.path.join(folder, filename)
    with open(filepath, "wb") as file:
        file.write(response.content)
    return filepath


def download_txt(url, limits, filename, folder="books/"):
    response = make_request_with_backoff(url, limits=limits)

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
        raise BookNotFoundException()


def make_request_with_backoff(url, limits):
    timeout, max_timeout, max_attempts = (
        limits.get("read_timeout", 5),
        limits.get("max_retries_timeout", 60),
        limits.get("max_retries_attempts", 5),
    )
    attempt = 1
    while attempt <= max_attempts:
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            check_for_redirect(response)
            return response
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.ReadTimeout
        ) as error:
            eprint(
                f"Attempt {attempt} of {max_attempts} "
                f"to retrieve data from {url} failed: {error}"
            )
            if attempt != max_attempts:
                time.sleep(timeout)
            timeout = min(timeout * 2, max_timeout)
            attempt += 1

    raise Exception(
        f"Failed to retrieve data from {url} after {max_attempts} attempts"
    )


def eprint(*args, **kwargs):
    print("\033[31m", *args, "\033[0m", file=sys.stderr, **kwargs)


def main():
    dotenv.load_dotenv()
    books_directory = os.getenv("BOOKS_DIRECTORY", "books")
    images_directory = os.getenv("IMAGES_DIRECTORY", "images")
    requests_limit = {
        "read_timeout": int(
            os.getenv("REQUESTS_TIMEOUT", 5)
        ),
        "max_retries_timeout": int(
            os.getenv("REQUESTS_MAX_RETRIES_TIMEOUT", 60)
        ),
        "max_retries_attempts": int(
            os.getenv("REQUESTS_MAX_RETRIES_ATTEMPTS", 5)
        ),
    }

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
    for book_id in range(start_id, end_id + 1):
        url_for_scraping = get_url_for_scraping(book_id)
        try:
            scraped_page = get_scraped_page(url_for_scraping, requests_limit)
        except BookNotFoundException as error:
            error.set_book_id(book_id)
            eprint(error, end="\n\n")
            continue
        except Exception as error:
            eprint(error, end="\n\n")
            continue

        book_details = parse_book_page(
            scraped_page,
            url_for_scraping
        )
        download_image(
            url=book_details["image"],
            limits=requests_limit,
            folder=images_directory,
        )

        try:
            downloaded = download_txt(
                url=get_url_for_download_txt(book_id),
                limits=requests_limit,
                filename=f"{book_id}. {book_details['title']}.txt",
                folder=books_directory,
            )
        except BookNotFoundException as error:
            error.set_book_id(book_id)
            eprint(error, end="\n\n")
            continue
        except Exception as error:
            eprint(error, end="\n\n")
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
