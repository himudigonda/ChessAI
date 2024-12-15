// frontend/src/App.js
import React, { useState, useCallback } from 'react';
import ModeSelection from './components/ModeSelection';
import GameScreen from './components/GameScreen';
import StatusDisplay from './components/StatusDisplay';
import './style.css'
import axios from 'axios';

function App() {
  const [statusMessage, setStatusMessage] = useState('');
  const [statusType, setStatusType] = useState('info');
  const [gameMode, setGameMode] = useState(null);
  const [boardData, setBoardData] = useState(null)

  const handleStatusChange = (message, type) => {
    const timestamp = Date.now();
    console.log(`[${timestamp}] Status changed: ${message}, type: ${type}`);
    setStatusMessage(message)
    setStatusType(type)
  }

  const handleModeSelect = (data) => {
    const timestamp = Date.now();
    console.log(`[${timestamp}] Game mode selected:`, data);
    setGameMode(true);
    setBoardData(data)
  };

  const handleNewBoardData = async () => {
    const timestamp = Date.now()
    console.log(`[${timestamp}] Fetching new board data`)
    try {
      const response = await axios.get('http://127.0.0.1:6009/api/get_board')
      if (response.data) {
        setBoardData(response.data)
      }

    }
    catch (error) {
      console.error(`[${timestamp}] Error fetching board data: `, error);
      handleStatusChange(`Error fetching board data: ${error.message}`, 'error')
    }
  }



  const renderContent = () => {
    if (!gameMode) {
      return <ModeSelection onModeSelect={handleModeSelect} onStatusChange={handleStatusChange} />;
    } else {
      return <GameScreen onStatusChange={handleStatusChange} boardData={boardData} onNewBoardData={handleNewBoardData} />;
    }
  };


  return (
    <div className="app-container">
      <h1>Chess AI</h1>
      {renderContent()}
      <StatusDisplay
        message={statusMessage}
        type={statusType}
      />
    </div>
  );
}

export default App;