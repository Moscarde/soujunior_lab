import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re


class DataHandler:
    def __init__(self, dataframe_path, data_bs4):
        self.data_bs4 = data_bs4
        self.dataframe = pd.read_csv(dataframe_path)
        self.dataframe_post_ids = self.dataframe["linkedin_id"].tolist()
        self.today_date = datetime.now()

    def process_data_to_dataframe(self):
        processed_posts = []
        for post in self.data_bs4:
            publish_date = self.get_published_date(post, self.today_date)

            post_url = self.get_post_url(post)

            linkedin_post_id = post_url.split(":")[-1]

            if (
                int(linkedin_post_id) in self.dataframe_post_ids
            ) or publish_date == None:
                continue

            shared_post = self.is_shared_post(post)

            author_name = self.get_author_name(post)

            author_profile_url = self.get_author_profile_url(post)

            post_type = self.get_post_type(post)

            post_content = self.get_post_content(post, post_type)

            qtd_reaction = self.get_qtd_reaction(post)

            qtd_comment = self.get_qtd_comment(post)

            qtd_share = self.get_qtd_share(post)

            processed_posts.append(
                [
                    publish_date,
                    shared_post,
                    author_name,
                    author_profile_url,
                    post_type,
                    post_url,
                    post_content,
                    qtd_reaction,
                    qtd_comment,
                    qtd_share,
                    linkedin_post_id,
                ]
            )

        columns = [
            "publish_date",
            "shared_post",
            "author_name",
            "author_profile_url",
            "post_type",
            "post_url",
            "post_content",
            "qtd_reaction",
            "qtd_comment",
            "qtd_share",
            "linkedin_post_id",
        ]

        df = pd.DataFrame(processed_posts, columns=columns)
        df.sort_values(by="publish_date", ascending=False, inplace=True)

        return df

    def get_published_date(self, post, today_date):
        actor_meta = post.find_all(class_="update-components-actor__meta")

        # if actor_meta:
        #     raw_post_date = (
        #         actor_meta[0].find_all(class_="visually-hidden").text.split("•")[0]
        #     )
        #     return self.define_date(raw_post_date, self.today_date)
        if actor_meta:
            raw_post_date = actor_meta[0].find_all(class_="visually-hidden")

            if raw_post_date:
                raw_post_date = raw_post_date[-1].text.split("•")[0]
                return self.define_date(raw_post_date, self.today_date)

        if (
            post.find(class_="update-components-promo-v1__text-container")
            or len(post.find_all(tag="div")) <= 7
        ):
            return None

        return "Unknown"

    def define_date(self, raw_date, today_date):
        num, mult, _ = raw_date.split(" ")
        if mult == "d":
            publish_date = today_date - timedelta(days=int(num))
        elif mult == "sem":
            publish_date = today_date - timedelta(days=int(num) * 7)
        elif mult == "m":
            publish_date = today_date - timedelta(days=int(num) * 30)
        elif mult == "h":
            publish_date = today_date

        return publish_date.date()

    def is_shared_post(self, post):
        if (post.find(class_="update-components-header__text-view") is not None) or (
            "feed-shared-update-v2__update-content-wrapper"
            in post.find(
                class_="feed-shared-update-v2__description-wrapper"
            ).find_next_sibling()["class"]
        ):
            return True
        else:
            return False

    def get_author_name(self, post):
        return post.find(class_="update-components-actor__name").span.span.text

    def get_author_profile_url(self, post):
        return post.find(class_="update-components-actor__meta-link")["href"]

    def get_post_type(self, post):
        if (post.find(class_="update-components-header__text-view") is not None) or (
            "feed-shared-update-v2__update-content-wrapper"
            in post.find(
                class_="feed-shared-update-v2__description-wrapper"
            ).find_next_sibling()["class"]
        ):
            return "Shared Content"

        elif post.find(class_="update-components-poll") is not None:
            return "Poll"

        elif (
            post.find(class_="update-components-scheduled-live-content__event-link")
            is not None
        ):
            return "Scheduled Event"

        elif post.find(class_="video-live") is not None:
            return "Live"

        elif post.find(class_="update-components-image--single-image") is not None:
            return "Single Image"

        elif (
            "update-v2-social-activity"
            in post.find(
                class_="feed-shared-update-v2__description-wrapper"
            ).find_next_sibling()["class"]
        ):
            return "Text Only"

        else:
            return "Unknown type"

    def get_post_url(self, post):
        return (
            "https://www.linkedin.com/feed/update/"
            + post.find(class_="feed-shared-update-v2")["data-urn"]
        )

    def get_post_content(self, post, post_type):
        if post_type == "Shared Content":
            return post.find(
                class_="update-components-update-v2__commentary"
            ).span.span.text
        else:
            return post.find(class_="update-components-text").span.span.text

    def get_qtd_reaction(self, post):
        if post.find(class_="social-details-social-counts__reactions-count") != None:
            return post.find(
                class_="social-details-social-counts__reactions-count"
            ).text.strip()

        else:
            qtd_reactions = post.find(
                class_="social-details-social-counts__social-proof-text"
            ).text.strip()

            re_pattern_reactions = r"\b(\d+)\s+pessoas\b"

            return 1 + int(re.findall(re_pattern_reactions, qtd_reactions)[0])

    def get_qtd_comment(self, post):
        if post.find(class_="social-details-social-counts__comments") != None:
            return (
                post.find(class_="social-details-social-counts__comments")
                .button.span.text.strip()
                .split(" ")[0]
            )
        else:
            return "0"

    def get_qtd_share(self, post):
        if (
            len(
                post.find_all(
                    class_="social-details-social-counts__item--right-aligned"
                )
            )
            <= 1
        ):
            return 0
        else:
            return (
                post.find_all(
                    class_="social-details-social-counts__item--right-aligned"
                )[1]
                .button.span.text.strip()
                .split(" ")[0]
            )

    def backup_dataframe(self):
        date = self.today_date.strftime("%Y-%m-%d_%H-%M-%S")
        self.dataframe.to_csv(
            f"linkedin_page/dataframes/backup/main_dataframe_backup_{date}.csv",
            index=False,
        )

    def append_data_to_dataframe_and_save(self, processed_dataframe):
        concated_df = pd.concat(
            [processed_dataframe, self.dataframe], ignore_index=True
        )
        concated_df.to_csv("linkedin_page/dataframes/main_dataframe.csv", index=False)


if __name__ == "__main__":
    staged_data_path = "linkedin_page/staged_data/"
    staged_filenames = os.listdir(staged_data_path)
    soup_list = []
    for filename in staged_filenames:
        with open(staged_data_path + filename, "r", encoding="utf8") as file:
            soup_list.append(BeautifulSoup(file, "html.parser"))

    print(type(soup_list[0]))
    # main_dataframe_path = "linkedin_page/dataframes/main_dataframe.csv"

    # data_handler = DataHandler(main_dataframe_path, soup_list)
    # processed_data = data_handler.process_data_to_dataframe()
    # data_handler.backup_dataframe()
    # data_handler.append_data_to_dataframe_and_save(processed_data)
