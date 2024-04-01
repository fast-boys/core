import requests
from bs4 import BeautifulSoup
import re


# 메타데이터 파싱해서 title, desc, image 추출
def fetch_og_data(url):
    headers = {  # 요청 헤더 설정
        "User-Agent": 'data-useragent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
        'like Gecko) Chrome/122.0.0.0 Safari/537.36"'
    }

    # 네이버 PC 기본 도메인은 URL이 숨겨져있음, iframe 제거된 링크 반환 필요
    # ([^/]+) - "/"가 아닌 하나 이상의 문자에 해당하는 부분을 user_id로 캡처
    # (\d+) - 하나 이상의 숫자에 해당하는 부분을 post_id로 캡처
    if re.match(r"https?://blog\.naver\.com/([^/]+)/(\d+)", url):
        url = delete_iframe(url)

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    # Open Graph 데이터 추출
    og_title = soup.find("meta", property="og:title")
    if not og_title:
        raise ValueError("og:title 정보가 없습니다.")

    og_description = (
        soup.find("meta", property="og:description")["content"]
        if soup.find("meta", property="og:description")
        else None
    )

    og_image = (
        soup.find("meta", property="og:image")["content"]
        if soup.find("meta", property="og:image")
        else None
    )

    og_url = (
        soup.find("meta", property="og:url")["content"]
        if soup.find("meta", property="og:url")
        else None
    )

    og_data = {
        "og_title": og_title["content"],
        "og_description": og_description,
        "og_image": og_image,
        "og_url": og_url,
    }

    return og_data


# 소스 URL로 변환 (네이버 PC 사이트의 경우 suorce url 이 감춰져있음)
def delete_iframe(url):
    headers = {  # 요청 헤더 설정
        "User-Agent": 'data-useragent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
        'like Gecko) Chrome/122.0.0.0 Safari/537.36"'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    source_url = "https://blog.naver.com/" + soup.iframe["src"]

    return source_url


def crawl_naver_blog(url):
    headers = {  # 요청 헤더 설정
        "User-Agent": 'data-useragent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
        'like Gecko) Chrome/122.0.0.0 Safari/537.36"'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.find("div", attrs={"class": "se-title-text"}).get_text()
    title = title.replace("\n", "")
    text = soup.find("div", attrs={"class": "se-main-container"}).get_text()
    # 필요없는 데이터들 전처리
    text = (
        text.replace("\n", "")
        .replace("\u200b", "")
        .replace("Previous image", "")
        .replace("Next image", "")
    )

    return " ".join([title, text])


def crawl_tistory(url):
    headers = {  # 요청 헤더 설정
        "User-Agent": 'data-useragent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
        'like Gecko) Chrome/122.0.0.0 Safari/537.36"'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    title = (
        soup.find("article", attrs={"id": "content"})
        .find("div", attrs={"class": "inner"})
        .find("h1")
        .get_text()
    )
    title = title.replace("\n", "")
    text = soup.find("div", attrs={"id": "article-view"}).get_text()

    # 필요없는 데이터들 전처리
    text = (
        text.replace("\n", "")
        .replace("\u200b", "")
        .replace("Previous image", "")
        .replace("Next image", "")
    )

    return " ".join([title, text])
