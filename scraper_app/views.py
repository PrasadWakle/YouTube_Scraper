from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import URLField
from django.core.exceptions import ValidationError
from django.contrib import messages
from scraper_app.mymodules.sraper import YouTube_Scraper
import json
import logging
import traceback
import sys

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging_format = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
file_handler = logging.FileHandler('django_app_log.log')
file_handler.setFormatter(logging_format)
logger.addHandler(file_handler)

# Home view that renders the index.html template
def home(request):
    logger.info("Rendering home page.")
    return render(request, "index.html")

# Function to validate a YouTube URL
def validate_youtube_url(url):
    url_form_field = URLField()
    try:
        url = url_form_field.clean(url)  # Validate the URL
    except ValidationError:
        return False  # Return False if validation fails
    return True  # Return True if validation succeeds

# View to handle POST requests and return scraped data as a downloadable JSON file
def get_data(request):
    try:
        if request.method == "POST":
            logger.info("Received POST request.")
            data = request.POST
            youtube_links = data.get("ylink")
            urls = youtube_links.split(",")

            youtube_data = list()  # Initialize an empty list to store the scraped data

            for url in urls:
                if validate_youtube_url(url):  # Validate the YouTube URL
                    channel = YouTube_Scraper(url)  # Create a YouTube_Scrapper object
                    logger.info(f"Created an YouTube_Scraper object for {url}.")
                    data = channel.scrap_data()  # Scrape the data
                    logger.info(f"Successfully scrapped data for url: {url}.")
                    youtube_data.append(data)  # Append the scraped data to the list
                else:
                    messages.error(request, "Invalid URL")  # Send an error message for invalid URLs
                    return redirect("/")  # Redirect to the home page

            json_str = json.dumps(youtube_data, indent=4)  # Convert the list of scraped data to a JSON string

            response = HttpResponse(json_str, content_type='application/json')  # Create an HttpResponse
            logger.info("Created HttpResponse with JSON data.")

            response['Content-Disposition'] = 'attachment; filename=data.json'  # Prompt a file download
            logger.info("Added Content-Disposition header to response.")

            logger.info("Done!")
            return response  # Return the response
        else:
            logger.warning("Received non-POST request.")
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()  # Get exception info
        logger.error("Exception type: ", exc_type)
        logger.error("Exception message: ", exc_value)
        logger.error("Exception occurred on line: ", traceback.format_exc())
        return HttpResponse("An error occurred. Please try again.")  # Return an error message

# About Page
def about(request):
    return render(request,"about.html")
