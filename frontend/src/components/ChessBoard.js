// frontend/src/components/ChessBoard.js
import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import Square from './Square';

function ChessBoard({ onMove, onStatusChange }) {
    const [boardData, setBoardData] = useState(null);
    const [selectedPiece, setSelectedPiece] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [apiError, setApiError] = useState(null);
    const isMounted = useRef(false);

    const fetchBoard = useCallback(async () => {
        const timestamp = Date.now();
        console.log(`[${timestamp}] Fetching board data...`);
        setIsLoading(true);
        setApiError(null);
        try {
            const response = await axios.get('http://127.0.0.1:6009/api/get_board');
            console.log(`[${timestamp}] Board data fetched:`, response.data);
            setBoardData(response.data);
        } catch (error) {
            console.error(`[${timestamp}] Error fetching board data`, error);
            setApiError(`Error fetching board: ${error.message}`);
            onStatusChange(`Error fetching board: ${error.message}`, "error");
        } finally {
            setIsLoading(false);
        }
    }, [onStatusChange]);

    useEffect(() => {
        if (isMounted.current) {
            return;
        }
        isMounted.current = true;
        const timestamp = Date.now();
        console.log(`[${timestamp}] useEffect called`);
        fetchBoard();
    }, [fetchBoard]);

    const handleSquareClick = async (square) => {
        const timestamp = Date.now();
        console.log(`[${timestamp}] Square clicked:`, square);
        try {
            if (selectedPiece === null) {
                setSelectedPiece(square);
                console.log(`[${timestamp}] Piece selected:`, square);
                return;
            }

            const move = selectedPiece + square;
            console.log(`[${timestamp}] Attempting move:`, move);

            try {
                const validateResponse = await axios.post(
                    'http://127.0.0.1:6009/api/validate_move',
                    { move: move }
                );
                console.log(`[${timestamp}] Move validation response:`, validateResponse.data);
                if (validateResponse.data.isLegal) {
                    makeMove(move);
                } else {
                    onStatusChange(`Illegal move: ${move}`, "error");
                }
            } catch (error) {
                console.error(`[${timestamp}] Error validating move`, error);
                onStatusChange(`Error validating move: ${error.message}`, "error");
                setApiError(`Error validating move: ${error.message}`);
            }
        } catch (error) {
            console.error(`[${timestamp}] Error during square click:`, error);
            onStatusChange(`Error during square click: ${error.message}`, "error")
            setApiError(`Error during square click: ${error.message}`);

        } finally {
            setSelectedPiece(null);
        }
    };


    const makeMove = async (move) => {
        const timestamp = Date.now();
        console.log(`[${timestamp}] Making move:`, move);
        try {
            const response = await axios.post(
                'http://127.0.0.1:6009/api/make_move',
                { move: move }
            );
            console.log(`[${timestamp}] Move made, response:`, response.data);
            setBoardData(response.data);
            onStatusChange('', "info");
            onMove();
            if (response.data.gameOver) {
                onStatusChange(`Game Over. ${response.data.winner} won the game`, "info");
            }
            if (response.data.legalMoves && response.data.legalMoves.length === 0 && !response.data.gameOver) {
                onStatusChange('Stalemate!', "info");
            }
            if (response.data.fen.split(' ')[1] === 'b' && !response.data.gameOver) {
                makeAIMove();
            }
        } catch (error) {
            console.error(`[${timestamp}] Error making move`, error);
            onStatusChange(`Error making move: ${error.message}`, "error");
            setApiError(`Error making move: ${error.message}`);
        }
    };

    const makeAIMove = async () => {
        const timestamp = Date.now();
        console.log(`[${timestamp}] Making AI move...`);
        try {
            const response = await axios.post('http://127.0.0.1:6009/api/ai_move');
            console.log(`[${timestamp}] AI move made, response:`, response.data);
            setBoardData(response.data);
            onMove();
            if (response.data.gameOver) {
                onStatusChange(`Game Over. ${response.data.winner} won the game`, "info");
            }
            if (response.data.legalMoves && response.data.legalMoves.length === 0 && !response.data.gameOver) {
                onStatusChange('Stalemate!', "info");
            }

        } catch (error) {
            console.error(`[${timestamp}] Error making AI move`, error);
            onStatusChange(`Error making AI move: ${error.message}`, "error");
            setApiError(`Error making AI move: ${error.message}`);
        }
    };


    const renderBoard = () => {
        const timestamp = Date.now();
        console.log(`[${timestamp}] Rendering board...`);
        if (isLoading) {
            return <div>Loading...</div>;
        }

        if (apiError) {
            return <div>{apiError}</div>;
        }
        if (!boardData) return <div>No board data available.</div>;
        const fen = boardData.fen.split(' ')[0];
        const rows = fen.split('/').map((row, rowIndex) => {
            const squares = row.split('').reduce((acc, char, fileIndex) => {
                if (isNaN(parseInt(char))) {
                    const square = `${String.fromCharCode(97 + fileIndex)}${8 - rowIndex}`;
                    const isSelected = square === selectedPiece;
                    acc.push(
                        <Square
                            key={square}
                            piece={renderPiece(char)}
                            isLight={(rowIndex + fileIndex) % 2 === 0}
                            onClick={() => handleSquareClick(square)}
                            isSelected={isSelected}
                        />
                    );
                } else {
                    for (let i = 0; i < parseInt(char); i++) {
                        const currentFileIndex = fileIndex + i;
                        const square = `${String.fromCharCode(97 + currentFileIndex)}${8 - rowIndex}`;
                        const isSelected = square === selectedPiece;
                        acc.push(
                            <Square
                                key={square}
                                isLight={(rowIndex + currentFileIndex) % 2 === 0}
                                onClick={() => handleSquareClick(square)}
                                isSelected={isSelected}
                            />
                        );
                    }
                    fileIndex += parseInt(char) - 1;
                }

                return acc;
            }, []);
            return <div key={rowIndex}>{squares}</div>;
        });
        return <div className="chessboard">{rows}</div>;
    };


    const renderPiece = (piece) => {
        const timestamp = Date.now();
        console.log(`[${timestamp}] Rendering piece:`, piece);
        switch (piece) {
            case 'r': return '♖';
            case 'n': return '♘';
            case 'b': return '♗';
            case 'q': return '♕';
            case 'k': return '♔';
            case 'p': return '♙';
            case 'R': return '♜';
            case 'N': return '♞';
            case 'B': return '♝';
            case 'Q': return '♛';
            case 'K': return '♚';
            case 'P': return '♟';
            default: return '';
        }
    };

    return (
        <div>
            {renderBoard()}
        </div>
    );
}

export default ChessBoard;