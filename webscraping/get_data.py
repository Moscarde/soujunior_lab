from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import time


class LinkedInScraper:
    def __init__(self, login, password, headless=False):
        self.driver = self.initialize_driver(headless)
        self.login_linkedin = login
        self.password_linkedin = password

    def initialize_driver(self, headless):
        options = Options()
        options.headless = headless
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

    def login(self):
        url = "https://www.linkedin.com/login/pt"
        self.driver.get(url)

        xpath_login = '//*[@id="username"]'
        xpath_password = '//*[@id="password"]'
        xpath_submit = '//*[@id="organic-div"]/form/div[3]/button'

        input_login = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath_login))
        )
        input_password = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath_password))
        )
        input_submit = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath_submit))
        )

        input_login.clear()
        input_password.clear()

        input_login.send_keys(self.login_linkedin)
        input_password.send_keys(self.password_linkedin)
        input_submit.click()

        if WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="global-nav"]'))
        ):
            print("Login successful")
        else:
            print("Login failed")

    def navigate_to_posts(self):
        linkedin_page_url = (
            "https://www.linkedin.com/company/soujunior/posts/?feedView=all"
        )
        self.driver.get(linkedin_page_url)

    def sort_by_date(self):
        class_sort = "sort-dropdown__dropdown"
        sort_div = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, class_sort))
        )
        sort_button = sort_div.find_element(By.TAG_NAME, "button")
        sort_button.click()

        time.sleep(1)
        sort_by_date = sort_div.find_elements(By.TAG_NAME, "li")[1]
        sort_by_date.click()

        time.sleep(2)

    def scroll_to_load_posts(self, scrolls=5):
        body = self.driver.find_element(By.TAG_NAME, "body")
        for _ in range(scrolls):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(2)

    def collect_posts(self):
        class_feed_posts = "scaffold-finite-scroll__content"
        feed_posts = self.driver.find_element(By.CLASS_NAME, class_feed_posts)
        return feed_posts.find_elements(By.XPATH, "./div")

    def scrape_posts(self):
        posts = self.collect_posts()

        output_folder = "data"
        screenshoted_author_list = [
            file.split(".png")[0]
            for file in os.listdir("linkedin_page\dataframes\profile_pics")
        ]
        new_posts = []

        for post in posts:
            author = post.find_elements(By.CLASS_NAME, "update-components-actor__name")

            if author:
                author_name = (
                    author[0].find_element(By.CLASS_NAME, "visually-hidden").text
                )
            else:
                continue

            if author_name not in screenshoted_author_list:
                img = post.find_element(
                    By.CLASS_NAME, "update-components-actor__avatar-image"
                )
                img_path = f"linkedin_page\dataframes\profile_pics/{author_name}.png"
                img.screenshot(img_path)
                screenshoted_author_list.append(author_name)

            new_posts.append(
                BeautifulSoup(post.get_attribute("outerHTML"), "html.parser")
            )

        return new_posts

    def stage_data(self, data):
        # delete old data
        for file in os.listdir("linkedin_page/staged_data"):
            os.remove(f"linkedin_page/staged_data/{file}")
        # save post
        for index, post in enumerate(data, 1):
            with open(
                f"linkedin_page/staged_data/post_{index}.html", "w", encoding="utf-8"
            ) as file:
                file.write(str(post))


def main():
    load_dotenv()

    login_linkedin = os.environ["LOGIN_LINKEDIN"]
    password_linkedin = os.environ["PASSWORD_LINKEDIN"]

    print('Starting driver...')
    scraper = LinkedInScraper(login_linkedin, password_linkedin, headless=True)
    print('Logging in...')
    scraper.login()
    print('Navigating to posts...')
    scraper.navigate_to_posts()
    print('Sorting by date...')
    scraper.sort_by_date()
    print('Scrolling to load posts...')
    scraper.scroll_to_load_posts()

    print('Scraping posts...')
    new_posts = scraper.scrape_posts()

    print('Staging data...')
    scraper.stage_data(new_posts)
    return new_posts


if __name__ == "__main__":
    new_posts = main()
