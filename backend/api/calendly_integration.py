from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import List
from ..tools.availability_tool import CalendlyClient

router = APIRouter()
client = CalendlyClient()

@router.get("/availability")
async def get_availability(
    start_date: str,
    end_date: str,
    appointment_type: str = "https://api.calendly.com/event_types/ec19aed1-b6ad-45e6-974c-1302f33564b9"
):
   
    try:
        slots = await client.get_available_slots(start_date, end_date, appointment_type)
        return {
            "appointment_type": appointment_type,
            "available_slots": slots,
            "total_slots": len(slots)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/appointment-types")
async def get_appointment_types():

    types = [
        {"name": "General Consultation", "duration": 30},
        {"name": "Follow-up", "duration": 15},
        {"name": "Physical Exam", "duration": 45},
        {"name": "Specialist Consultation", "duration": 60}
    ]
    return types