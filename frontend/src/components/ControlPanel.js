// frontend/src/components/ControlPanel.js
import React from 'react';
import axios from 'axios';

function ControlPanel({ onNewGame, onStatusChange }) {
    const startNewGame = async () => {
        const timestamp = Date.now();
        console.log(`[${timestamp}] Starting new game`);
        try {
            const response = await axios.post('http://127.0.0.1:6009/api/new_game')
            onNewGame(response.data)
            onStatusChange("New Game started", "success");
        } catch (error) {
            console.error(`[${timestamp}] Error starting new game`, error)
            onStatusChange(`Error starting new game: ${error.message}`, "error")
        }
    }


    return (
        <div className="controls">
            <button onClick={startNewGame}>New Game</button>
        </div>
    );
}

export default ControlPanel;