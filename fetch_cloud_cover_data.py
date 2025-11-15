import requests
import pandas as pd
from requests import RequestException

class STACData:
    def __init__(self, url, bbox):
        self.url = url
        self.bbox = bbox

    def get_cloud_cover_data_by_month(self, year=2025, limit=500):
        all_data = []
        for month in range(1, 13):
            start = f"{year}-{month:02d}-01T00:00:00Z"
            if month == 12:
                end = f"{year}-12-31T23:59:59Z"
            else:
                end = f"{year}-{month+1:02d}-01T00:00:00Z"
            query = {
                "collections": ["sentinel-s2-l2a"],
                "bbox": self.bbox,
                "datetime": f"{start}/{end}",
                "query": {"eo:cloud_cover": {"lt": 100}},
                "limit": limit
            }
            try:
                response = requests.post(self.url, json=query)
                response.raise_for_status()
                features = response.json().get("features", [])
                for info in features:
                    data = {
                        "datetime": pd.to_datetime(info["properties"]["created"], utc=True),
                        "cloud_cover": info["properties"]["eo:cloud_cover"],
                        "month": month
                    }
                    all_data.append(data)
            except RequestException as e:
                print(f"Request failed for {year}-{month:02d}: {e}")

        return pd.DataFrame(all_data)


url = "https://earth-search.aws.element84.com/v0/search"
ghana_bbox = [-3.2604, 4.7108, 1.1996, 11.1786]

client = STACData(url, ghana_bbox)
df = client.get_cloud_cover_data_by_month(year=2025, limit=500)
df.to_csv("ghana_cloud_cover_2025.csv", index=False)

