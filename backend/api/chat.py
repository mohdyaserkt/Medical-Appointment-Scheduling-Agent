from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict
from ..models.schemas import ChatMessage, AppointmentRequest
from ..agent.scheduling_agent import SchedulingAgent
from ..tools.availability_tool import CalendlyClient
from ..tools.booking_tool import BookingManager
from datetime import datetime, timedelta
import asyncio

router = APIRouter()
agent = SchedulingAgent()
calendly_client = CalendlyClient()
booking_manager = BookingManager()

@router.post("/chat")
async def chat_endpoint(message: ChatMessage):
    
    try:
        # Extract patient intent
        intent = agent.extract_intent(message.content)
        
        # Get available slots 
        available_slots = []
        if intent.get("time_preference"):
            today = datetime.utcnow().date()
            end_date = today + timedelta(days=6)  # total 7 days including today

         
            available_slots = await calendly_client.get_available_slots(
                start_date=today,
                end_date=end_date,
                event_type="https://api.calendly.com/event_types/ec19aed1-b6ad-45e6-974c-1302f33564b9"
            )
           
        # Generate AI response
        response = await agent.generate_response(
            user_message=message.content,
            available_slots=available_slots, 
            context=intent
        )
        
        return {
            "response": response,
            "intent": intent,
            "available_slots": available_slots[:3] if available_slots else [],
            "next_step": _determine_next_step(intent, len(available_slots))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schedule")
async def schedule_appointment(request: AppointmentRequest):
  
    try:
        # Validate patient info
        if not request.patient_info:
            raise HTTPException(status_code=400, detail="Patient information required")
        
       
        booking_result = await booking_manager.create_appointment(
            patient=request.patient_info,
            start_time=datetime.now(),  # Would be actual selected time
            appointment_type=request.appointment_type
        )
        
        if booking_result:
            return {
                "success": True,
                "confirmation_code": booking_result["confirmation_code"],
                "message": "Appointment scheduled successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to schedule appointment")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _determine_next_step(intent: Dict, available_slots_count: int) -> str:
    
    if not intent:
        return "greet"
    elif "appointment_type" not in intent:
        return "ask_appointment_type"
    elif available_slots_count == 0:
        return "suggest_alternatives"
    elif "time_preference" not in intent:
        return "ask_time_preference"
    else:
        return "collect_patient_info"