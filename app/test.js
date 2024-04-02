//request 1
const request1 = {
    "planId": 5,
    "plans": [
        {
            "spotId": "1000981",
            "date": "2024-03-31"
        },
        {
            "spotId": "2575406",
            "date": "2024-04-01"
        }
    ]
}

//response 1
const response1 = {
    "id": 5,
    "info": {
        "info": {
        "name": "현재여행중",
        "profileImage": null,
        "startDate": "2024-03-31",
        "endDate": "2024-04-01",
        "cities": [
                4,
                5
            ]
        }
    },
    "plan": {
        "places": {
        "1000981": {
            "id": 1000981,
            "name": "김춘수 유품전시관",
            "category": [
            3
            ],
            "lat": "34.8333722569",
            "long": "128.4161841816"
        },
        "2575406": {
            "id": 2575406,
            "name": "한려숯불갈비",
            "category": [
            5
            ],
            "lat": "34.8418130104",
            "long": "128.4178838118"
        }
        },
        "days": {
        "2024-03-31": [], //여기 1000981 들어있어야하고
        "2024-04-01": []  //여기 2572406 들어있어야함
        },
        "dayOrder": [
        "2024-04-01",
        "2024-03-31"
        ]
    }
}


//request 2
const request2 = {
    "planId": 5,
    "plans": [
        {
            "spotId": "1000981",
            "date": "2024-03-31"
        },
        {
            "spotId": "2575406",
            "date": "2024-04-01"
        },
        {
            "spotId": "1917811",
            "date": "2024-04-01"
        }
    ]
}


//response 2
const response2 = {
    "id": 5,
    "info": {
        "info": {
        "name": "현재여행중",
        "profileImage": null,
        "startDate": "2024-03-31",
        "endDate": "2024-04-01",
        "cities": [
            4,
            5
        ]
        }
    },
    "plan": {
        "places": {
        "1000981": {
            "id": 1000981,
            "name": "김춘수 유품전시관",
            "category": [
            3
            ],
            "lat": "34.8333722569",
            "long": "128.4161841816"
        },
        "1917811": {
            "id": 1917811,
            "name": "동경호텔",
            "category": [
            6
            ],
            "lat": "34.8854859532",
            "long": "128.4206990848"
        },
        "2575406": {
            "id": 2575406,
            "name": "한려숯불갈비",
            "category": [
            5
            ],
            "lat": "34.8418130104",
            "long": "128.4178838118"
        }
        },
        "days": {
        "2024-03-31": [],
        "2024-04-01": [    // 대체 spot_id가 어쩌다 저기 들어간거지...
            "spot_id"
        ]
        },
        "dayOrder": [
        "2024-04-01",
        "2024-03-31"
        ]
    }
}

// request 3
const request3 = {
    "planId": 5,
    "plans": [
        {
            "spotId": "1000981",
            "date": "2024-04-01"
        },
        {
            "spotId": "2575406",
            "date": "2024-04-01"
        },
        {
            "spotId": "1917811",
            "date": "2024-04-01"
        }
    ]
}

// response 3
const response3 = {
    "id": 5,
    "info": {
        "info": {
        "name": "현재여행중",
        "profileImage": null,
        "startDate": "2024-03-31",
        "endDate": "2024-04-01",
        "cities": [
            4,
            5
        ]
        }
    },
    "plan": {
        "places": {
        "1000981": {
            "id": 1000981,
            "name": "김춘수 유품전시관",
            "category": [
            3
            ],
            "lat": "34.8333722569",
            "long": "128.4161841816"
        },
        "1917811": {
            "id": 1917811,
            "name": "동경호텔",
            "category": [
            6
            ],
            "lat": "34.8854859532",
            "long": "128.4206990848"
        },
        "2575406": {
            "id": 2575406,
            "name": "한려숯불갈비",
            "category": [
            5
            ],
            "lat": "34.8418130104",
            "long": "128.4178838118"
        }
        },
        "days": {
        "2024-04-01": [
            "spot_id",	// spot_id의 value 대신 key가 들어가는 듯
            "spot_id"
        ]
        },
        "dayOrder": [
        "2024-04-01"
        ]
    }
}
