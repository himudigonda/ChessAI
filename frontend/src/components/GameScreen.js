// frontend/src/components/GameScreen.js
import React from 'react';
import ChessBoard from './ChessBoard';
import SidePanel from './SidePanel';

function GameScreen({ onStatusChange, boardData, onNewBoardData }) {
    const handleMove = () => {
        if (boardData) {
            onNewBoardData()
        }

    };
    return (
        <div className="game-screen">
            <ChessBoard
                onMove={handleMove}
                onStatusChange={onStatusChange}
            />
            <SidePanel onStatusChange={onStatusChange} boardData={boardData} />
        </div>
    );
}

export default GameScreen;