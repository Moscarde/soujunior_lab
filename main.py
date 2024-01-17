from webscraping.get_data import LinkedInScraper
from webscraping.process_data import DataHandler

from dotenv import load_dotenv
import os


def main():
    login_linkedin, password_linkedin = load_env_variables()

    new_data = scrap_linkedin_posts(
        login_linkedin,
        password_linkedin,
        page_posts_url="https://www.linkedin.com/company/soujunior/posts/?feedView=all",
        headless=True,
        scroll_to_load_posts=15,
    )

    process_and_save_data(new_data)


def load_env_variables():
    load_dotenv()

    login_linkedin = os.environ["LOGIN_LINKEDIN"]
    password_linkedin = os.environ["PASSWORD_LINKEDIN"]

    return login_linkedin, password_linkedin


def scrap_linkedin_posts(
    login_linkedin,
    password_linkedin,
    page_posts_url,
    headless,
    scroll_to_load_posts,
):
    print("Starting driver...")
    scraper = LinkedInScraper(login_linkedin, password_linkedin, headless)

    print("Logging in...")
    scraper.login()

    print("Navigating to posts...")
    scraper.navigate_to_posts(page_posts_url)

    print("Sorting by date...")
    scraper.sort_by_date()

    print("Scrolling to load posts...")
    scraper.scroll_to_load_posts(scroll_to_load_posts)

    print("Scraping posts...")
    new_data = scraper.scrape_posts()
    print(f"{len(new_data)} new posts scraped.")

    print("Staging data...")
    scraper.stage_data(new_data)

    return new_data


def process_and_save_data(new_data):
    main_dataframe_path = "linkedin_page/dataframes/main_dataframe.csv"

    print("Starting data processing...")
    dh = DataHandler(main_dataframe_path, new_data)
    processed_data = dh.process_data_to_dataframe()

    print("Creating backup...")
    dh.backup_dataframe()

    print("Saving dataframe with new data...")
    dh.append_data_to_dataframe_and_save(processed_data)


if __name__ == "__main__":
    main()
