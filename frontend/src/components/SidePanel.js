// frontend/src/components/SidePanel.js
import React, { useState, useEffect } from 'react';
import axios from 'axios'

function SidePanel({ onStatusChange, boardData }) {
    const [moves, setMoves] = useState([]);
    const [whiteTime, setWhiteTime] = useState(300)
    const [blackTime, setBlackTime] = useState(300)

    useEffect(() => {
        if (boardData && boardData.moves) {
            setMoves(boardData.moves);
        }
    }, [boardData]);

    const handleDraw = () => {
        onStatusChange("Draw offered", "info")
    };

    const handleResign = () => {
        onStatusChange("Resigned Game", "info")
    }

    const handleUndo = async () => {
        const timestamp = Date.now();
        console.log(`[${timestamp}] Undoing move`);
        try {
            const response = await axios.get('http://127.0.0.1:6009/api/get_board')
            if (response.data) {
                onStatusChange("Undone last move", "info")
            }
        } catch (error) {
            console.error(`[${timestamp}] Error undoing move: `, error);
            onStatusChange(`Error undoing move: ${error.message}`, "error")
        }
    };

    const handleRedo = async () => {
        const timestamp = Date.now();
        console.log(`[${timestamp}] Redoing move`);
        try {
            const response = await axios.get('http://127.0.0.1:6009/api/get_board')
            if (response.data) {
                onStatusChange("Redone last move", "info")
            }
        } catch (error) {
            console.error(`[${timestamp}] Error redoing move:`, error);
            onStatusChange(`Error redoing move: ${error.message}`, "error")
        }
    };


    return (
        <div className="side-panel">
            <div className='timer'>
                <p>White: {Math.floor(whiteTime / 60)}:{String(whiteTime % 60).padStart(2, '0')} </p>
                <p>Black: {Math.floor(blackTime / 60)}:{String(blackTime % 60).padStart(2, '0')} </p>
            </div>

            <div className="move-list">
                <h3>Moves</h3>
                <ul>
                    {moves.map((move, index) => (
                        <li key={index}>{move}</li>
                    ))}
                </ul>
            </div>

            <div className="controls">
                <button onClick={handleDraw}>Draw</button>
                <button onClick={handleResign}>Resign</button>
                <button onClick={handleUndo}>Undo</button>
                <button onClick={handleRedo}>Redo</button>
                <button>Rematch</button>
            </div>
        </div>
    );
}
export default SidePanel;