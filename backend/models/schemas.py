from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# Functional data models
class AppointmentType(BaseModel):
    name: str
    duration_minutes: int
    description: str

class TimeSlot(BaseModel):
    start_time: datetime
    end_time: datetime
    is_available: bool = True

class PatientInfo(BaseModel):
    name: str
    email: str
    phone: str
    reason_for_visit: str

class AppointmentRequest(BaseModel):
    patient_info: PatientInfo
    appointment_type: str
    preferred_date: Optional[str] = None
    preferred_time_range: Optional[str] = None

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

# Pure functions for data transformation
def create_appointment_types() -> List[AppointmentType]:
    return [
        AppointmentType(
            name="General Consultation",
            duration_minutes=30,
            description="For general health concerns and initial assessments"
        ),
        AppointmentType(
            name="Follow-up",
            duration_minutes=15,
            description="For routine follow-up appointments"
        ),
        AppointmentType(
            name="Physical Exam",
            duration_minutes=45,
            description="For comprehensive physical examinations"
        ),
        AppointmentType(
            name="Specialist Consultation",
            duration_minutes=60,
            description="For specialized medical consultations"
        )
    ]

def validate_patient_info(patient: dict) -> Optional[PatientInfo]:
   
    required_fields = ['name', 'email', 'phone', 'reason_for_visit']
    if all(field in patient for field in required_fields):
        return PatientInfo(**patient)
    return None