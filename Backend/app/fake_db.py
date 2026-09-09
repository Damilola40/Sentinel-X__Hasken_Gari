from datetime import datetime, timezone
import uuid

incidents = [
    {
        "data": {
            "id": str(uuid.uuid4()),
            "title": "Fire outbreak",
            "description": "There is a fire in a residential building",
            "category": "fire",
            "severity": "high",
            "status": "reported",
            "location": {
                "latitude": 10.5105,
                "longitude": 7.4165,
                "address": "Barnawa, Kaduna",
                "city": "Kaduna",
                "state": "Kaduna"
            },
            "created_at": datetime.now(timezone.utc)
        },
    }
]