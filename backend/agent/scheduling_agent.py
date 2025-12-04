import google.generativeai as genai
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from functools import partial
from .prompts import SCHEDULING_AGENT_PROMPT
from dotenv import load_dotenv
load_dotenv()


# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(model_name=os.getenv("GEMINI_MODEL"))

class SchedulingAgent:
    def __init__(self):
        self.conversation_history = []
    
    def _add_to_history(self, role: str, content: str) -> None:
       
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def extract_intent(self, user_message: str) -> Dict[str, Any]:
        
        prompt = f"""
        Analyze this patient message and extract:
        1. Appointment type needed (General Consultation, Follow-up, Physical Exam, Specialist)
        2. Time preference (morning, afternoon, evening, specific date)
        3. Urgency level (urgent, routine)
        4. Reason for visit summary
        
        Message: {user_message}
        
        Return as JSON format.
        """
        
        try:
            response = model.generate_content(prompt)
            # Parse response to extract structured data
            # This would be more sophisticated in production
            return {
                "appointment_type": self._classify_appointment_type(user_message),
                "time_preference": self._extract_time_preference(user_message),
                "reason": user_message
            }
        except Exception as e:
            print(f"Error extracting intent: {e}")
            return {}
    
    def _classify_appointment_type(self, message: str) -> str:
       
        message_lower = message.lower()
        if any(word in message_lower for word in ['headache', 'fever', 'cough', 'general']):
            return "General Consultation"
        elif any(word in message_lower for word in ['follow', 'check', 'routine']):
            return "Follow-up"
        elif any(word in message_lower for word in ['physical', 'exam', 'complete']):
            return "Physical Exam"
        elif any(word in message_lower for word in ['specialist', 'cardio', 'neuro', 'dermat']):
            return "Specialist Consultation"
        return "General Consultation"
    
    def _extract_time_preference(self, message: str) -> Optional[str]:
     
        message_lower = message.lower()
        if 'morning' in message_lower:
            return 'morning'
        elif 'afternoon' in message_lower:
            return 'afternoon'
        elif 'evening' in message_lower:
            return 'evening'
        return None
    
    async def generate_response(self, 
                               user_message: str,
                               available_slots: List[Dict] = None,
                               context: Dict = None) -> str:
      
        self._add_to_history("user", user_message)
        
        # Build context for the AI
        context_str = ""
        if available_slots:
            context_str += f"Available time slots: {available_slots}\n"
        if context:
            context_str += f"Patient context: {context}\n"
        
        full_prompt = f"""
        {SCHEDULING_AGENT_PROMPT}
        
        Current conversation context:
        {context_str}
        
        Patient's latest message: {user_message}
        
        Previous conversation:
        {self.conversation_history[-5:] if len(self.conversation_history) > 5 else self.conversation_history}
        
        Generate a helpful, natural response.
        """
        
        try:
            response = model.generate_content(full_prompt)
            response_text = response.text
            
            self._add_to_history("assistant", response_text)
            return response_text
        except Exception as e:
            error_msg = "I apologize, but I'm having trouble processing your request. Could you please try again?"
            self._add_to_history("assistant", error_msg)
            return error_msg