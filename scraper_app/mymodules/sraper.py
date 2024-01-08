from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup as bs
import traceback
import sys
import logging
import time

class YouTube_Scraper:
    """
    A class used to scrape data from a YouTube channel.

    ...

    Attributes
    ----------
    channel_url : str
        the URL of the YouTube channel to scrape

    Methods
    -------
    scrap_data():
        Scrapes data from the YouTube channel and video.
    """
    
    def __init__(self,channel_url):
        """
        Constructs all the necessary attributes for the Youtube_Scrapper object.

        Parameters
        ----------
            channel_url : str
                the URL of the YouTube channel to scrape
        """
        self.channel_url = channel_url
        
    def scrap_data(self):
        """
        Scrapes data from the YouTube channel and video and returns a dictionary object.
        """
        try:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.INFO)

            logging_format=logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

            file_handler=logging.FileHandler('youtube_scraper_log.log')
            file_handler.setFormatter(logging_format)

            logger.addHandler(file_handler)
            
             # Install ChromeDriver and initialize driver variable
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
            logger.info("Successfully istalled the webdriver!")
            driver.implicitly_wait(10)
            driver.maximize_window()

            try:
                # Load the channel page
                driver.get(self.channel_url)
                logger.info(f"URL {self.channel_url} loaded successfully!")
         
            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logger.error("Exception type: ", exc_type)
                logger.error("Exception message: ", exc_value)
                logger.error("Exception occurred on line: ", traceback.tb_lineno(exc_traceback))

            # Extract channel name and total number of videos
            channel_name = driver.find_element(By.XPATH,"//yt-formatted-string[@id = 'text']").text.encode('ascii', 'ignore').decode('ascii')
            total_videos = driver.find_element(By.XPATH,"//yt-formatted-string[@id='videos-count']/span").text
            logger.info(f"Successfully scraped channel name and total number of videos of the channel: {channel_name}.")

            try:
                # Load the videos page
                driver.get(f"{self.channel_url}/videos")
                logger.info("Successfully loaded the videos page!")
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//ytd-rich-grid-media//a[@href]"))
                )

                # Extract the href attribute value
                video_href_value = element.get_attribute("href")

                # Extract the href attribute value
                driver.get(video_href_value)
                logger.info(f"Successfully located and loaded the first video of the channel: {channel_name}.")
   
            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logger.error("Exception type: ", exc_type)
                logger.error("Exception message: ", exc_value)
                logger.error("Exception occurred on line: ", traceback.tb_lineno(exc_traceback))

            # Extract video and channel details
            video_title = driver.find_element(By.CSS_SELECTOR,"h1.ytd-watch-metadata").text.encode('ascii', 'ignore').decode('ascii')
            channel_element = driver.find_element(By.ID,"owner")
            channel_subs = channel_element.find_element(By.ID,"owner-sub-count").text.replace(" subscribers","")
            video_likes = driver.find_element(By.CLASS_NAME,"YtLikeButtonViewModelHost").text
            logger.info(f"Successfully scraped the video and channel details of the channel: {channel_name}.")

            #Expand the description box
            driver.find_element(By.ID, 'expand').click()

            #Locate and extract description information
            description_box = driver.find_elements(By.CSS_SELECTOR, '#info-container span')
            views = description_box[0].text.replace(' views', '')
            upload_date = description_box[2].text
            description = driver.find_element(By.CSS_SELECTOR,"#description-inline-expander .ytd-text-inline-expander span span").text.encode('ascii', 'ignore').decode('ascii')
            logger.info(f"Successfully scrapped the description details of the channel: {channel_name}.")
            
            # Scroll down to reveal comments
            SCROLL_PAUSE_TIME = 2
            last_height = driver.execute_script("return document.documentElement.scrollHeight")

            while True:
                # Scroll to the bottom of the page
                driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                time.sleep(SCROLL_PAUSE_TIME)
                new_height = driver.execute_script("return document.documentElement.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height


            #Locate and extract comments section elements using beautiful soup
            comments_section = driver.find_element(By.XPATH,"//ytd-comments[@id = 'comments']/ytd-item-section-renderer[@id = 'sections']/div[@id = 'contents']")
            comments_html = comments_section.get_attribute("innerHTML")
            soup = bs(comments_html,"html.parser")
            comment_authors = soup.find_all("a",{"id":"author-text"})
            comments = soup.find_all("yt-formatted-string",{'class': 'style-scope ytd-comment-renderer'})
            logger.info(f"Successfully scrapped the comment authors and comments of the channel: {channel_name}.")

            # Dictionary object to store the channel information
            channel = {
                "channel_name":channel_name,
                "total_videos":total_videos,
                "total_subscribers":channel_subs,
                "channel_url":self.channel_url,
                "video":{
                    "video_title":video_title,
                    "video_views":views,
                    "video_description":description,
                    "video_upload_date":upload_date,
                    "video_likes":video_likes,
                    "video_url":video_href_value
                    }
                }

            # 'comments' : An empty list that will store the comments for the video
            channel["video"]["comments"] = list()

            # This code block iterates over 'comment_authors' and 'comments', creates a dictionary for each comment, and appends it to the 'comments' list in 'channel' dictionary if it's not already present.
            # It ensures that each comment is unique and no duplicates are added to the 'comments' list.
            for authors, comment in zip(comment_authors, comments):
                comment_author = authors.text.encode('ascii', 'ignore').decode('ascii').replace("\n","")
                comment_text = comment.text.encode('ascii', 'ignore').decode('ascii').replace("\n","")
                comment_dict = {"comment_author": comment_author, "comment_text": comment_text}

                # Only append if the comment_dict is not already in the list
                if comment_dict not in channel["video"]["comments"]:
                    channel["video"]["comments"].append(comment_dict)

            logger.info(f"Done!")
            return channel

            
        # This block catches NoSuchElementException, prints its type, message, and the line number where it occurred.
        except NoSuchElementException:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error("Exception type: ", exc_type)
            logger.error("Exception message: ", exc_value)
            logger.error("Exception occurred on line: ", traceback.tb_lineno(exc_traceback))

        # This block catches all other exceptions, prints their type, message, and the full traceback including the line number where they occurred.   
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error("Exception type: ", exc_type)
            logger.error("Exception message: ", exc_value)
            logger.error("Exception occurred on line: ", traceback.format_exc())

        finally:
            logger.info("Closing the driver.")
            # Close the driver
            driver.quit()
