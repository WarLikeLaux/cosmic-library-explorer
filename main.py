import os
import pathlib
import urllib

import dotenv
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

BASE_URL = "https://tululu.org"


def get_book_details_from_response(response):
    soup = BeautifulSoup(response.text, "lxml")
    title, author = [
        element.strip() for element in soup.find("h1").text.split("::")
    ]
    image = urllib.parse.urljoin(
        BASE_URL, soup.select_one(".bookimage img")["src"])
    comments = [element.find(
        "span", class_="black").text for element in soup.find_all("div", class_="texts")]
    return title, author, image, comments


def get_url_for_scraping(id):
    safe_id = urllib.parse.quote(str(id))
    return f"{BASE_URL}/b{safe_id}/"


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

    # books_directory_abs_path = os.path.join(os.getcwd(), books_directory)
    # pathlib.Path(books_directory_abs_path).mkdir(parents=True, exist_ok=True)
    # images_directory_abs_path = os.path.join(os.getcwd(), images_directory)
    # pathlib.Path(images_directory_abs_path).mkdir(parents=True, exist_ok=True)

    start_id = 5

    for increment in range(1):
        current_id = start_id + increment

        url = get_url_for_scraping(current_id)
        response = requests.get(url)
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue
        book_title, book_author, book_image, comments = get_book_details_from_response(
            response
        )
        download_image(book_image, images_directory)

        try:
            downloaded = download_txt(
                url=get_url_for_download_txt(current_id),
                filename=f"{current_id}. {book_title}.txt",
                folder=books_directory,
            )
        except requests.HTTPError:
            continue

        print(downloaded)


if __name__ == "__main__":
    main()
