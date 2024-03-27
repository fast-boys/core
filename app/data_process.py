from database import get_m_db


db = next(get_m_db())
city_dict = {}
datas = list(
    db.find(
        {
            "address": {
                "$exists": True,
                "$ne": "",
                "$ne": None,
            }
        },
        {"address": 1},
    )
)
for data in datas:
    city = data["address"].split(" ")
    if city[0] not in city_dict:
        city_dict[f"{city[0]}"] = set()
    if len(city) >= 2:
        city_dict[f"{city[0]}"].add(city[1])
    else:
        city_dict[f"{city[0]}"].add("")
print(city_dict)
