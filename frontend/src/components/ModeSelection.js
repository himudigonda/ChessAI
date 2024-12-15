// frontend/src/components/ModeSelection.js
import React from 'react';
import axios from 'axios';

function ModeSelection({ onModeSelect, onStatusChange }) {

    const handleModeClick = async (mode) => {
        const timestamp = Date.now();
        console.log(`[${timestamp}] Mode selected:`, mode);
        try {
            const response = await axios.post(`http://127.0.0.1:6009/api/start_game/${mode}`)
            console.log(`[${timestamp}] API call successful to start game`, response.data)
            onModeSelect(response.data);
        }
        catch (error) {
            console.error(`[${timestamp}] Error starting game in ${mode} mode`, error);
            onStatusChange(`Error starting game in ${mode} mode: ${error.message}`, "error")
        }
    };


    return (
        <div className="mode-selection">
            <h2>Choose Game Mode</h2>
            <button onClick={() => handleModeClick('2players')}>2 Players</button>
            <button onClick={() => handleModeClick('vs_stockfish')}>vs Stockfish</button>
            <button onClick={() => handleModeClick('vs_cai')}>vs AI Model</button>
            <button onClick={() => handleModeClick('sf_vs_cai')}>Watch Stockfish vs AI</button>
        </div>
    );
}

export default ModeSelection;