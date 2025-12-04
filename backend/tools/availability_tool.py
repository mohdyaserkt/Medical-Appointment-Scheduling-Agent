import os
import httpx
from datetime import datetime
from typing import List, Optional
from functools import lru_cache
from ..models.schemas import TimeSlot, AppointmentType
from dotenv import load_dotenv
load_dotenv()

class CalendlyClient:
    def __init__(self):
        self.api_key = os.getenv("CALENDLY_API_KEY")
        self.base_url = "https://api.calendly.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    # Pure function - no side effects
    def parse_duration(self, appointment_type: str) -> int:
        durations = {
            "General Consultation": 30,
            "Follow-up": 15,
            "Physical Exam": 45,
            "Specialist Consultation": 60
        }
        return durations.get(appointment_type, 30)

    @lru_cache(maxsize=128)
    async def get_available_slots(
        self,
        start_date: str,
        end_date: str,
        event_type: str
    ) -> List[TimeSlot]:
       
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                
                response = await client.get(
                    f"{self.base_url}/event_type_available_times",
                    headers=self.headers,
                    params={
                        "start_time": start_date,
                        "end_time": end_date,
                        "event_type": event_type,
                    }
                )

                response.raise_for_status()
                data = response.json()

                return [
                    TimeSlot(
                        start_time=datetime.fromisoformat(
                            slot["start_time"].replace("Z", "+00:00")
                        ),
                        end_time=datetime.fromisoformat(
                            slot["end_time"].replace("Z", "+00:00")
                        ),
                    )
                    for slot in data.get("collection", [])
                ]

        except httpx.HTTPError as e:
            print(f"Calendly API error: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []

    # Pure function - filtering logic only
    def filter_slots_by_preference(
        self,
        slots: List[TimeSlot],
        time_range: Optional[str] = None
    ) -> List[TimeSlot]:

        if not time_range:
            return slots

        def is_in_range(slot: TimeSlot) -> bool:
            hour = slot.start_time.hour
            if time_range == "morning" and 6 <= hour < 12:
                return True
            elif time_range == "afternoon" and 12 <= hour < 17:
                return True
            elif time_range == "evening" and 17 <= hour < 21:
                return True
            return False

        return list(filter(is_in_range, slots))
