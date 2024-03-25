from schemas.spot_dto import SimpleSpotDto


# response 후처리 후 List[dto] 변환
def extract_similar_spots(knn_response, collection):
    similar_spots = []

    for hit in knn_response["hits"]["hits"][1:]:
        spot_id = hit["_source"]["spot_id"]
        spot = collection.find_one({"spot_id": {"$eq": spot_id}})
        if spot:  # MongoDB에서 해당 spot_id를 가진 문서가 있는지 확인
            spot_dto = SimpleSpotDto(
                spot_id=spot_id,
                name=spot.get("name", None),
                address=spot.get("address", ""),
                image_url=spot.get("depiction")[0] if spot.get("depiction") else "",
            )
            similar_spots.append(spot_dto)

    return similar_spots
