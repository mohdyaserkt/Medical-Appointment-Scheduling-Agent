import React from 'react';
import ChatInterface from './components/ChatInterface';
import './App.css';

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-cyan-50">
      <div className="container mx-auto max-w-6xl p-4">
        <ChatInterface />
        
        {/* Information Footer */}
        <footer className="mt-8 text-center text-gray-600 text-sm">
          <p>Medical Appointment Scheduling Agent v1.0</p>
          <p className="mt-1">Powered by AI and Calendly Integration</p>
          <p className="mt-2 text-xs">Note: This is a demo application. For real medical appointments, contact healthcare providers directly.</p>
        </footer>
      </div>
    </div>
  );
}

export default App;