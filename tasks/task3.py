import os
import re
import json
from datetime import datetime, timezone
from typing import Optional
import bs4
import requests
from fake_headers import Headers
from selenium.common import NoSuchElementException
from tqdm import tqdm

from config.config import Config_
from logger.logger import logger_func, logger_func_flag

path_ = Config_.get_path_file_log_into_dir()


@logger_func(path_)
def save_file_json(path, data):
    try:
        with open(path, 'w', encoding='utf-8', newline='') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except FileNotFoundError as e:
        print(f'FileNotFoundError: {e}')


@logger_func_flag(path_, flag_args=False)
def get_number_pages(soup) -> int:
    div_pagination = soup.select('div.tm-pagination__page-group')
    return 1 if len(div_pagination) < 2 else int(
        div_pagination[len(div_pagination) - 1].select_one('a').text.strip())


@logger_func_flag(path_, flag_args=False)
def get_link_next_page(soup) -> Optional[str]:
    next_page = soup.select_one('a#pagination-next-page')['href']
    return 'https://habr.com' + next_page if next_page else None


def find_element_(soup, value):
    try:
        return soup.select_one(value)
    except NoSuchElementException:
        return None


@logger_func_flag(path_)
def get_datetime(s_time: str):
    try:
        dt = datetime.strptime(s_time, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
        return dt.strftime('%Y-%d-%m')
    except ValueError:
        return s_time


@logger_func_flag(path_)
def add_article_to_list(list_dict: list[dict], dict_: dict):
    link = dict_.get('link')
    if not link:
        return
    for item in list_dict:
        if item.get('link') == link:
            print(f'{link=}')
            return
    list_dict.append(dict_)


@logger_func(path_)
def main_bs4():
    words = Config_.get_search_words()
    escaped = [re.escape(k) for k in words]
    pattern = re.compile(r"\b(" + '|'.join(escaped) + r")\b", re.IGNORECASE)

    url = Config_.get_url()
    headers = Headers(browser='chrome', os='win').generate()

    articles: list[dict] = []
    response = requests.get(url, headers=headers)
    soup = bs4.BeautifulSoup(response.text, features='lxml')

    number_pages = get_number_pages(soup)
    link_next_page = None
    if number_pages > 1:
        link_next_page = get_link_next_page(soup)
    i = 0
    np = Config_.get_number_pages()
    if number_pages > np:
        number_pages = np

    with tqdm(total=number_pages, desc=f"Page link {url} {i}/{number_pages}", colour="green", ncols=100, position=0,
              leave=True) as pbar:
        while i < number_pages:
            pbar_info_link = link_next_page
            if i > 0:
                if not link_next_page:
                    break
                response = requests.get(link_next_page, headers=headers)
                soup = bs4.BeautifulSoup(response.text, features='lxml')
                link_next_page = get_link_next_page(soup)

            div_tag_articles = soup.select('div.article-snippet')
            if not div_tag_articles:
                i += 1
                continue
            for article in div_tag_articles:
                p = pattern.search(article.text)
                if p:
                    time_attr = None
                    time_element = find_element_(article, 'time')
                    if time_element:
                        time_attr = time_element['datetime']
                    h2_tag = find_element_(article, 'h2.tm-title_h2')
                    a_tag = find_element_(h2_tag, 'a')
                    if time_attr and a_tag:
                        link = url + a_tag['href']
                        title_span = find_element_(a_tag, 'span')
                        title = title_span.text.strip() if title_span else a_tag.text.strip()
                        date_time = get_datetime(time_attr)

                        dict_ = {
                            'link': link,
                            'title': title,
                            'date': date_time
                        }
                        add_article_to_list(articles, dict_)
            i += 1
            soup = None
            pbar.set_description(f"Page link {pbar_info_link} {i}/{number_pages}")
            pbar.update(1)

    # отфильтровать по дате
    articles.sort(key=lambda x: x['date'], reverse=True)
    print('--------------------------------------------------------------------')
    for image in articles:
        print(f"{image.get('date')} - {image.get('title')} - {image.get('link')}")

    save_file_json(os.path.join('files', 'articles.json'), articles)
