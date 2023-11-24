import os
import pathlib

import dotenv
import requests


def main():
    dotenv.load_dotenv()
    books_directory = os.getenv("BOOKS_DIRECTORY", "books")

    books_directory_abs_path = os.path.join(os.getcwd(), books_directory)
    pathlib.Path(books_directory_abs_path).mkdir(parents=True, exist_ok=True)
    start_id = 32168
    for i in range(10):
        params = {"id": start_id + i}
        url = "https://tululu.org/txt.php"
        response = requests.get(url, params=params)
        response.raise_for_status()
        filename = f"b{start_id + i}.txt"
        filepath = os.path.join(books_directory_abs_path, filename)
        with open(filepath, "wb") as file:
            file.write(response.content)


if __name__ == "__main__":
    main()
