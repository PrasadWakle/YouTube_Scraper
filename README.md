# Django YouTube Scraper

This is a Django project that scrapes data from multiple YouTube channels using Selenium and BeautifulSoup.

## Features

The application takes multiple YouTube channel URLs and scrapes the following data:

- Channel name
- Total subscribers
- Data of the first video from the video section:
  - Video title
  - Video likes
  - Views
  - Upload date
  - Description
  - Comments

Please note that this project is not production-ready and is intended for educational purposes.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

- Python 3.8+
- Django 3.2+
- Selenium
- BeautifulSoup

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/PrasadWakle/YouTube_Scraper.git

2. Navigate to the project directory:
   ```bash
   cd Youtube_Scrapper

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt

4. Run the Django server:
   ```bash
   python manage.py runserver

Now, you should be able to see the application running at localhost:8000 in your web browser.
