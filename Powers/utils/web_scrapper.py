import os
import re
from typing import List

import httpx

from Powers import *

# import requests
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.expected_conditions import \
#     presence_of_element_located
# from selenium.webdriver.support.wait import WebDriverWait


class SCRAP_DATA:
    """Class to get and handel scrapped data"""

    def __init__(self, urls: List[str] or str) -> None:
        self.urls = urls
        self.path = scrap_dir
        if not os.path.isdir(self.path):
            os.makedirs(self.path)

    def get_images(self) -> list:
        images = []
        if isinstance(self.urls, str):
            requested = httpx.get(self.urls)
            try:
                name = f"{self.path}img_{str(time()).replace('.', '_')}.jpg"
                with open(name, "wb") as f:
                    f.write(requested.content)
                images.append(name)
            except Exception as e:
                LOGGER.error(e)
                LOGGER.error(format_exc())
                requested.close()
        else:
            for i in self.urls:
                if i:
                    requested = httpx.get(i)
                else:
                    continue
                try:
                    name = f"{self.path}img_{str(time()).replace('.', '_')}.jpg"
                    with open(name, "wb") as f:
                        f.write(requested.content)
                    images.append(name)
                except Exception as e:
                    LOGGER.error(format_exc())
                    LOGGER.error(e)
                    requested.close()
                    continue
        return images

    def get_videos(self) -> list:
        videos = []
        if isinstance(self.urls, str):
            if i:
                requested = httpx.get(i)
            else:
                return []
            try:
                name = f"{self.path}vid_{str(time()).replace('.', '_')}.mp4"
                with open(name, "wb") as f:
                    f.write(requested.content)
                videos.append(name)
            except Exception as e:
                LOGGER.error(e)
                LOGGER.error(format_exc())
                requested.close()
        else:
            for i in self.urls:
                if i:
                    requested = httpx.get(i)
                else:
                    continue
                try:
                    name = f"{self.path}vid_{str(time()).replace('.', '_')}.mp4"
                    with open(name, "wb") as f:
                        f.write(requested.content)
                    videos.append(name)
                except Exception as e:
                    LOGGER.error(e)
                    LOGGER.error(format_exc())
                    requested.close()
                    continue
        return videos


# class DRIVER:
#     """Class to make selenium driver"""

#     def __init__(self) -> None:
#         self.BIN = CHROME_BIN
#         self.CHROME_DRIVER = CHROME_DRIVER

#     def initialize_driver(self):
#         if not self.BIN:
#             LOGGER.error(
#                 "ChromeBinaryErr: No binary path found! Install Chromium or Google Chrome.")
#             return (
#                 None,
#                 "ChromeBinaryErr: No binary path found! Install Chromium or Google Chrome.",
#             )

#         try:
#             options = Options()
#             options.binary_location = self.BIN
#             options.add_argument("--disable-dev-shm-usage")
#             options.add_argument("--ignore-certificate-errors")
#             options.add_argument("--disable-gpu")
#             options.add_argument("--headless=new")
#             options.add_argument("--test-type")
#             options.add_argument("--no-sandbox")

#             service = Service(self.CHROME_DRIVER)
#             driver = webdriver.Chrome(options, service)
#             return driver, None
#         except Exception as e:
#             LOGGER.error(f"ChromeDriverErr: {e}")
#             return None, f"ChromeDriverErr: {e}"

#     def driver_close(self, driver: webdriver.Chrome):
#         driver.close()
#         driver.quit()


# class INSTAGRAM(DRIVER):
#     """Class to scrap data from instagram"""

#     def __init__(self, url: str) -> None:
#         self.url = url
#         self.article = "article._aa6a"
#         self.ul_class = "_acay"
#         self.image_class = "x5yr21d"
#         self.video_class = "x1lliihq"
#         self.next_button = "button._afxw"
#         self.return_dict = {"image": [], "video": []}
#         super().__init__()

#     def is_correct_link(self):
#         return bool((re.compile(r"^https?://(?:www\.)?instagram\.com/")).match(self.url))

#     def get_all(self):
#         driver, error = self.initialize_driver()
#         if not driver:
#             return error

#         driver.get(self.url)
#         wait = WebDriverWait(driver, 30)
#         if "reel" in self.url:
#             element = wait.until(
#                 presence_of_element_located((By.TAG_NAME, "video")))
#             reels = element.get_attribute("src")
#             self.driver_close(driver)
#             self.return_dict.get("video").append(reels)
#             return self.return_dict
#         elif bool((re.compile(r"^https?://(?:www\.)?instagram\.com/p/")).match(self.url)):
#             image_links = []
#             video_links = []
#             try:
#                 element = wait.until(presence_of_element_located(
#                     (By.CLASS_NAME, self.ul_class)))

#                 while True:
#                     sub_element = element.find_elements(
#                         By.CLASS_NAME, self.image_class)
#                     for i in sub_element:
#                         url = i.get_attribute("src")
#                         image_links.append(url)

#                     sub_element = element.find_elements(
#                         By.CLASS_NAME, self.video_class)
#                     for i in sub_element:
#                         url = i.get_attribute("src")
#                         video_links.append(url)

#                     try:
#                         driver.find_element(
#                             By.CSS_SELECTOR, self.next_button).click()
#                     except:  # Failed to either find the element or click on next i.e. no more media left in post
#                         break
#             except:
#                 element = wait.until(presence_of_element_located(
#                     (By.CSS_SELECTOR, self.article)))
#                 try:
#                     sub_element = element.find_element(By.TAG_NAME, "img")
#                     image_links.append(sub_element.get_attribute("src"))
#                 except:
#                     sub_element = element.find_element(By.TAG_NAME, "video")
#                     video_links.append(sub_element.get_attribute("src"))

#             self.driver_close(driver)
#             # To remove duplicates here I am converting into set
#             if image_links:
#                 image_links = list(set(image_links))
#             if video_links:
#                 video_links = list(set(video_links))
#                 for i in video_links:
#                     image_links.remove(i)

#             self.return_dict.get("image").extend(image_links)
#             self.return_dict.get("video").extend(video_links)
#             return self.return_dict

#         else:
#             return {}

class INSTAGRAM:
    def __init__(self, url):
        self.url = url

    def is_correct_url(self):
        return bool((re.compile(r"^https?://(?:www\.)?instagram\.com/")).match(self.url))

    def get_media(self):
        try:
            return httpx.post(
                f"https://api.qewertyy.dev/downloaders/instagram?url={self.url}"
            ).json()
        except httpx.ReadTimeout:
            try:
                curr_timeout = 10
                timeout = httpx.Timeout(curr_timeout)
                return httpx.post(
                            f"https://api.qewertyy.dev/downloaders/instagram?url={self.url}",
                            timeout=timeout
                        ).json()
            except httpx.ReadTimeout:
                return {"code": 69, "message": "Please retry after few seconds"}
            except Exception as e:
                LOGGER.error(e)
                LOGGER.error(format_exc())
                return {"code": 69, "message": e}

        except Exception as e:
            LOGGER.error(e)
            LOGGER.error(format_exc())
            return {"code": 69, "message": e}
