import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { format } from 'date-fns';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [appointmentDetails, setAppointmentDetails] = useState(null);
  const chatEndRef = useRef(null);

  const API_URL = 'http://localhost:8000/api/v1';

  useEffect(() => {
    // Initial greeting
    setMessages([{
      role: 'assistant',
      content: 'Hello! I\'m your medical scheduling assistant. How can I help you today?',
      timestamp: new Date()
    }]);
  }, []);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        role: 'user',
        content: input
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date(),
        metadata: response.data
      };

      setMessages(prev => [...prev, assistantMessage]);

      // If slots are available, show them
      if (response.data.available_slots && response.data.available_slots.length > 0) {
        setAppointmentDetails({
          slots: response.data.available_slots,
          intent: response.data.intent
        });
      }

    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSlotSelect = async (slot) => {
    // Handle slot selection
    setIsLoading(true);
    
    // In real implementation, would collect patient info
    const patientInfo = {
      name: "John Doe", // Would come from form
      email: "john@example.com",
      phone: "555-0123",
      reason_for_visit: appointmentDetails?.intent?.reason || "General Consultation"
    };

    try {
      const response = await axios.post(`${API_URL}/schedule`, {
        patient_info: patientInfo,
        appointment_type: appointmentDetails?.intent?.appointment_type || "General Consultation",
        slot: slot
      });

      if (response.data.success) {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `Appointment confirmed! Your confirmation code is: ${response.data.confirmation_code}`,
          timestamp: new Date()
        }]);
        setAppointmentDetails(null);
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow p-4">
        <h1 className="text-2xl font-bold text-blue-600">Medical Appointment Scheduler</h1>
        <p className="text-gray-600">AI-powered scheduling assistant</p>
      </header>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs md:max-w-md lg:max-w-lg rounded-lg p-3 ${
                msg.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-white text-gray-800 shadow'
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
              <p className="text-xs opacity-75 mt-1">
                {format(new Date(msg.timestamp), 'hh:mm a')}
              </p>
            </div>
          </div>
        ))}
        
        {/* Available Slots */}
        {appointmentDetails?.slots && (
          <div className="bg-white rounded-lg shadow p-4 mt-4">
            <h3 className="font-semibold mb-2">Available Time Slots:</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {appointmentDetails.slots.map((slot, index) => (
                <button
                  key={index}
                  onClick={() => handleSlotSelect(slot)}
                  className="p-3 border border-blue-300 rounded hover:bg-blue-50 transition-colors"
                >
                  <div className="font-medium">
                    {format(new Date(slot.start_time), 'EEE, MMM d')}
                  </div>
                  <div className="text-sm text-gray-600">
                    {format(new Date(slot.start_time), 'h:mm a')} - 
                    {format(new Date(slot.end_time), 'h:mm a')}
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white rounded-lg shadow p-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-75"></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-150"></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={chatEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t bg-white p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your message here..."
            className="flex-1 border rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="bg-blue-600 text-white rounded-lg px-6 py-3 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
        
        {/* Quick Prompts */}
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            onClick={() => setInput("I need to see the doctor for headaches")}
            className="text-sm bg-gray-100 hover:bg-gray-200 rounded-full px-3 py-1"
          >
            Headache Consultation
          </button>
          <button
            onClick={() => setInput("I need a follow-up appointment")}
            className="text-sm bg-gray-100 hover:bg-gray-200 rounded-full px-3 py-1"
          >
            Follow-up Visit
          </button>
          <button
            onClick={() => setInput("Afternoon appointment this week")}
            className="text-sm bg-gray-100 hover:bg-gray-200 rounded-full px-3 py-1"
          >
            This Week Afternoon
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;