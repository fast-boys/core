from pydantic import BaseModel
from typing import Optional, List


class SpotBaseDto(BaseModel):
    """
    모든 관광지 DTO에서 공통적으로 사용되는 기본 필드
    """

    spot_id: str  # 관광지 고유 식별자
    name: str  # 관광지 이름
    address: str  # 관광지 주소
    image_url: str  # 관광지 대표 이미지 URL


class SimpleSpotDto(SpotBaseDto):
    """
    자동완성 및 간단한 정보제공을 위한 DTO
    """


# class ResultSpotDto(SpotBaseDto):
#     """
#     검색 결과에 표시되는 관광지 정보 DTO
#     """
#     lat: str   # 위도
#     long: str  # 경도


class DetailSpotDto(SpotBaseDto):
    """
    관광지 상세 정보 페이지에 사용되는 DTO
    선택적으로 제공되는 필드 ( ex. parking 등 ) 이 있으며, Optional 객체로 관리됨
    """

    image_urls: List[str]  # 관광지 대표 이미지 URL 목록
    description: str  # 관광지 설명
    lat: str  # 위도
    long: str  # 경도

    # ------ 아래부터는 있을수도, 없을수도 있음 (Optional) ------
    tel: Optional[str] = None  # 전화번호
    credit_card: Optional[str] = None  # 신용카드 사용 가능 여부
    parking: Optional[str] = None  # 주차시설 정보
    open_time: Optional[str] = None  # 영업 시간
    pets_available: Optional[str] = None  # 애완동물 동반 가능 여부
    baby_equipment_rental: Optional[str] = None  # 유모차 대여 서비스 여부
    closed_for_the_day: Optional[str] = None  # 쉬는 날
    play_area_for_children: Optional[str] = None  # 어린이 놀이방 여부
    best_menu: Optional[str] = None  # 대표 메뉴
    rest_date: Optional[str] = None  # 정기 휴일
    time_available: Optional[str] = None  # 이용 가능 시간
    sale_items: Optional[str] = None  # 판매품목
    take_out: Optional[str] = None  # 포장 가능 여부
    fair_day: Optional[str] = None  # 장서는날
    smoking_section_available: Optional[str] = None  # 금연/흡연
    reservation: Optional[str] = None  # 예약안내
    fee: Optional[str] = None  # 이용요금
    occupancy: Optional[str] = None  # 수용가능인원
    age_limit: Optional[str] = None  # 체험가능연령
    scale: Optional[str] = None  # 규모
    start_date: Optional[str] = None  # 이벤트의 시작일
    end_date: Optional[str] = None  # 종료일
    show_time: Optional[str] = None  # 공연시간
    parking_fee: Optional[str] = None  # 주차요금
    travel_time: Optional[str] = None  # 관람소요시간
    discount: Optional[str] = None  # 할인정보
    age_available: Optional[str] = None  # 관람 가능 연령
    seasons: Optional[str] = None  # 이용시기
    time_required: Optional[str] = None  # 관람소요시간
    program: Optional[str] = None  # 행사프로그램
