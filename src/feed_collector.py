import feedparser
import pprint
import re
import json
from bs4 import BeautifulSoup
from src import topics_watcher


class feed_collector:
    def __init__(self):
        self.urls = {}
        self.keywords = {}
        self.config_path = ""
        topics_watcher.init_db()

    def load_config(self, config_path):
        self.config_path = config_path
        with open(config_path, "r") as f:
            d = json.load(f)
            
            self.keywords = d["keywords"]
            self.urls = d["favorites"]
    
    def update_config(self):
        self.load_config(self.config_path)

    def get_topics(self):
        ret_topics = []

        # 正規表現のための単語パターンを作成.
        words = []
        for keyword in self.keywords:
            words.append(keyword["word"])
        pattern = "|".join(re.escape(word) for word in words)
        exp = "^(?=.*({}))".format(pattern)
        p = re.compile(exp, re.IGNORECASE)

        # RSS のリンクから情報を取得.
        for url in self.urls:
            if not url["type"] == "rss":
                continue
            f = feedparser.parse(url["url"])
            entries = f["entries"]
            for e in entries:
                is_in_title = False
                if not e.get("title") == None:
                    is_in_title = p.search(e["title"])

                is_in_summary = False
                if not e.get("summary") == None:
                    is_in_summary = p.search(e["summary"])

                if is_in_title or is_in_summary:
                    if topics_watcher.is_posted(e["link"]):
                        continue

                    topics_watcher.mark_as_sended(e["link"])

                    title = self.removal_html_tag(e["title"])
                    summary = self.removal_html_tag(e["summary"])

                    print(f"- {title}")
                    topic = {
                                "title": title,
                                "url": e["link"],
                                "summary": summary,
                                "type": "RSS",
                                "name": url["name"]
                            }
                    ret_topics.append(topic)
        return ret_topics

    def removal_html_tag(self, text):
        out_text = BeautifulSoup(text, "html.parser").get_text(
                separator = "",
                strip = True
                )
        return out_text



if __name__ == "__main__":
    f = feed_collector()
    f.load_config("../.config/config.json")
    topics = f.get_topics()
    print(topics)

