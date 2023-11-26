<a name="readme-top"></a>

# Cosmic Library Explorer

<details>
<summary><h2>Table of Contents</h2></summary>

  - [Overview](#overview)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Project objectives](#project-objectives)
  - [License](#license)
</details>

# Book Downloader and Parser

Cosmic Library Explorer is designed to automate the process of downloading books from [tululu.org](https://tululu.org). It scrapes book details, downloads text files and cover images, and saves them locally.

## Features

- **Book Detail Parsing:** extracts details like title, author, comments, and genres from a book's webpage.
- **Image Downloading:** downloads book cover images and saves them in a specified folder.
- **Text File Downloading:** downloads the text of the book and saves it as a `.txt` file.
- **Customizable Range:** allows users to specify the range of book IDs to download.
- **Error Handling:** includes checks for redirects and HTTP errors to ensure smooth execution.
- **Environment Variable Support:** uses `.env` for configurable directories for saving books and images.
- **Command-Line Interface:** provides a simple CLI for easy usage and customization.
- **File Naming and Sanitization:** ensures safe file naming for downloaded content.

### 1. 🐍 Environment setup

First of all, make sure you have Python 3 installed, version `3.8.0` or higher. If not, visit the [official Python website](https://www.python.org/) and download the latest version.

The command to check your Python version should show a version no lower than `3.5.0`. You might need to use aliases such as `python`, `py`, `python3.8`, or onwards up to `python3.12` instead of `python3`.

```
$ python --version
Python 3.8.10
```

### 2. 📥 Repository cloning

Clone the repository using the command below:

```
git clone https://github.com/WarLikeLaux/cosmic-library-explorer
```

Then, navigate to the project folder:

```
cd cosmic-library-explorer
```

### 3. 🧩 Dependencies installation

Use pip (or pip3, if there's a conflict with Python2) to install the dependencies:

```
pip install -r requirements.txt
```

### 4. 🗝️ Environment variables setup

To set up your environment variables, you'll need to create a `.env` file in the root directory of the project. If you already have a `.env.example` file, you can simply copy with rename it to `.env` using the command `cp .env.example .env`. Once you've done this, add or/and fill the following lines by values in your `.env` file:

- `BOOKS_DIRECTORY`: this variable specifies the directory where the downloaded book text files will be saved. If not set, the script defaults to a directory named `books` in the current working directory. Ensure this directory is writable.
- `IMAGES_DIRECTORY`: this variable defines the directory for saving the downloaded cover images of the books. In the absence of this setting, the script uses a default directory named `images` in the current working directory. Similar to `BOOKS_DIRECTORY`, this should also be a writable location.

Please ensure that each environment variable is assigned the correct value.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

To use this script, you can specify the start and end IDs of the books you wish to download. By default, it downloads books with IDs from 1 to 10. 

Run the script using the command:

```bash
python main.py [start_id] [end_id]
```

To see how the script works, you can download books with IDs 10, 11, and 12 from tululu.org. These IDs correspond to specific books in their database. To do this, run the script with the following command:

```
python main.py 10 12
```

This command instructs the script to download and process books starting from ID 10 up to and including ID 12. The expected output in your console will be as follows:

```
Название: Бизнес путь: Amazon.com
Автор: Саундерс Ребекка
Жанры: деловая литература
Файл: 'books/10. Бизнес путь Amazon.com.txt'

Название: Бизнес путь: Yahoo! Секреты самой популярной в мире интернет-компании
Автор: Вламис Энтони
Жанры: деловая литература, прочая компьютерная литература
Файл: 'books/11. Бизнес путь Yahoo! Секреты самой популярной в мире интернет-компании.txt'

Название: Бизнес со скоростью мысли
Автор: Гейтс Билл
Жанры: деловая литература
Файл: 'books/12. Бизнес со скоростью мысли.txt'
```

This output shows the title (`Название`), author (`Автор`), genres (`Жанры`), and the file path (`Файл`) for each downloaded book, indicating successful downloading and processing of the book data.

## Project objectives

This code was written for educational purposes as part of an online course for web developers at [dvmn.org](https://dvmn.org/).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

This code is open-source and free for any modifications, distributions, and uses. Feel free to utilize it in any manner you see fit.

<p align="right">(<a href="#readme-top">back to top</a>)</p>