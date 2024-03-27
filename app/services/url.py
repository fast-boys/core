import requests
from bs4 import BeautifulSoup


# 메타데이터 파싱해서 title, desc, image 추출
def fetch_og_data(url):
    headers = {  # 요청 헤더 설정
        "User-Agent": 'data-useragent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
        'like Gecko) Chrome/122.0.0.0 Safari/537.36"'
    }

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
