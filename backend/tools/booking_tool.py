import os
import httpx
from datetime import datetime
from typing import Dict, Optional
from ..models.schemas import PatientInfo
from dotenv import load_dotenv
load_dotenv()

class BookingManager:
    def __init__(self):
        self.api_key = os.getenv("CALENDLY_API_KEY")
        self.base_url = "https://api.calendly.com/scheduled_events"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_appointment(self,
                               patient: PatientInfo,
                               start_time: datetime,
                               appointment_type: str) -> Optional[Dict]:
       
        try:
            appointment_data = {
                "event_type": self._map_appointment_type(appointment_type),
                "start_time": start_time.isoformat(),
                "invitees": [{
                    "email": patient.email,
                    "first_name": patient.name.split()[0],
                    "last_name": patient.name.split()[-1] if len(patient.name.split()) > 1 else "",
                }]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=appointment_data
                )
                response.raise_for_status()
                
                return {
                    "confirmation_code": response.json().get("uri", "").split("/")[-1],
                    "details": response.json()
                }
                
        except Exception as e:
            print(f"Error creating appointment: {e}")
            return None
    
    def _map_appointment_type(self, appointment_type: str) -> str:
     
        mapping = {
            "General Consultation": os.getenv("CALENDLY_GENERAL_CONSULTATION_URI"),
            "Follow-up": os.getenv("CALENDLY_FOLLOWUP_URI"),
            "Physical Exam": os.getenv("CALENDLY_PHYSICAL_EXAM_URI"),
            "Specialist Consultation": os.getenv("CALENDLY_SPECIALIST_URI")
        }
        return mapping.get(appointment_type, os.getenv("CALENDLY_GENERAL_CONSULTATION_URI"))