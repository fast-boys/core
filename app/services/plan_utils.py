from fastapi import Depends, HTTPException
from pymongo import MongoClient

from database import get_m_db
from schemas.spot_dto import DetailSpotDto


async def get_spot_detail(spot_id: str, collection: MongoClient):
    spot = collection.find_one({"spot_id": {"$eq": str(spot_id)}})
    if spot is None:  # 해당 spot_id를 가진 문서를 찾을 수 없음
        raise HTTPException(
            status_code=404, detail=f"Spot ID {spot_id}에 해당하는 관광지를 찾을 수 없습니다."
        )

    properties = spot.get("properties", {})

    tour_spot = DetailSpotDto(
        # 반드시 필요한 데이터
        spot_id=str(spot_id),
        name=spot.get("name"),
        address=spot.get("address", ""),
        image_url=spot.get("depiction")[0] if spot.get("depiction") else "",
        image_urls=spot.get("depiction") if spot.get("depiction") else [],
        lat=spot.get("lat", ""),
        long=spot.get("long", ""),
        category=spot.get("category"),
        # 상세 정보 고유 데이터
        description=spot.get("description", ""),
        tel=properties.get("tel"),
        credit_card=properties.get("creditCard"),
        parking=properties.get("parking"),
        open_time=properties.get("openTime"),
        pets_available=properties.get("petsAvailable"),
        baby_equipment_rental=properties.get("babyEquipmentRental"),
        closed_for_the_day=properties.get("closedForTheDay"),
        play_area_for_children=properties.get("playAreaForChildren"),
        best_menu=properties.get("bestMenu"),
        rest_date=properties.get("restDate"),
        time_available=properties.get("timeAvailable"),
        sale_items=properties.get("saleItems"),
        take_out=properties.get("takeOut"),
        fair_day=properties.get("fairDay"),
        smoking_section_available=properties.get("smokingSectionAvailable"),
        reservation=properties.get("reservation"),
        fee=properties.get("fee"),
        occupancy=properties.get("occupancy"),
        age_limit=properties.get("ageLimit"),
        scale=properties.get("scale"),
        start_date=properties.get("startDate"),
        end_date=properties.get("endDate"),
        show_time=properties.get("showTime"),
        parking_fee=properties.get("parkingFee"),
        travel_time=properties.get("travelTime"),
        discount=properties.get("discount"),
        age_available=properties.get("ageAvailable"),
        seasons=properties.get("seasons"),
        time_required=properties.get("timeRequired"),
        program=properties.get("program"),
    )

    return tour_spot
