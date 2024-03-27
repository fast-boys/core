const dummyData: { data: ITravelDetail } = {
    data: {
        id: "1",
        info: {
            name: "우와여행",
            profileImage: "",
            startDate: "2024.07.12",
            endDate: "2024.07.15",
            travelTags: ["태그1", "태그2"],
            cities: ["도시1", "도시2", "도시3"],
        },
        plan: {
            places: {
                1000981: {
                    id: "1000981",
                    name: "place 1",
                    category: ["분류"],
                    lat: "34.8333722569",
                    long: "128.4161841816",
                },
            },
            days: {
                "07.12": { id: "1", day: "금", placeIds: ["1000981", "1917811", "2575406"] },
                "07.13": { id: "2", day: "토", placeIds: ["2514027", "2514751"] },
            },
            dayOrder: ["07.12", "07.13", "07.14", "07.15"],
        },
    },
};

export interface ITravelDetail {
    id: string;
    info: {
        name: string;
        profileImage: string;
        startDate: string;
        endDate: string;
        travelTags: string[];
        cities: string[];
    };
    plan: IPlan;
}

export interface IPlan {
    places: Record<string, IPlace>;
    days: Record<string, IDay>;
    dayOrder: string[];
}

interface IPlace {
    id: string;
    name: string;
    category: string[];
    lat: string;
    long: string;
}

interface IDay {
    id: string;
    day: string;
    placeIds: string[];
}
