// frontend/src/components/ChessBoard.js
import api from '../services/api';
import { DndProvider, useDrag } from 'react-dnd';
import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import Square from './Square';
import './ChessBoard.css';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { useParams } from 'react-router-dom';
import ControlPanel from './ControlPanel';
import StatusBar from './StatusBar';
import CapturedPieces from './CapturedPieces';
import MoveList from './MoveList';

const ItemTypes = {
    PIECE: 'piece',
};

function Piece({ piece, square, onMove }) {
    const [, drag] = useDrag({
        type: ItemTypes.PIECE,
        item: { piece, square },
    });

    const renderPiece = () => {
        const handleImageError = (e) => {
            console.error(`Error loading image for piece: ${piece}`, e);
        };

        const handleImageLoad = () => {
            console.log(`Successfully loaded image for piece: ${piece}`);
        };

        // Add CSS class for proper sizing
        const imgStyle = {
            width: '50px',
            height: '50px',
            userSelect: 'none',
            WebkitUserDrag: 'none'
        };

        try {
            switch (piece) {
                case 'r': return <img src="/frontend/public/assets/images/Black_rook.png" alt="black rook" style={imgStyle} onError={handleImageError} onLoad={handleImageLoad} />;
                case 'n': return <img src="/frontend/public/assets/images/Black_knight.png" alt="black knight" style={imgStyle} onError={handleImageError} onLoad={handleImageLoad} />;
                case 'b': return <img src="/frontend/public/assets/images/Black_bishop.png" alt="black bishop" style={imgStyle} onError={handleImageError} onLoad={handleImageLoad} />;
                case 'q': return <img src="/frontend/public/assets/images/Black_queen.png" alt="black queen" style={imgStyle} onError={handleImageError} onLoad={handleImageLoad} />;
                case 'k': return <img src="/frontend/public/assets/images/Black_king.png" alt="black king" style={imgStyle} onError={handleImageError} onLoad={handleImageLoad} />;
                case 'p': return <img src="/frontend/public/assets/images/Black_pawn.png" alt="black pawn" style={imgStyle} onError={handleImageError} onLoad={handleImageLoad} />;
                case 'R': return <img src="/frontend/public/assets/images/White_rook.png" alt="white rook" style={imgStyle} onError={handleImageError} onLoad={handleImageLoad} />;
                case 'N': return <img src="/frontend/public/assets/images/White_knight.png" alt="white knight" style={imgStyle} onError={handleImageError} onLoad={handleImageLoad} />;
                case 'B': return <img src="/frontend/public/assets/images/White_bishop.png" alt="white bishop" style={imgStyle} onError={handleImageError} onLoad={handleImageLoad} />;
                case 'Q': return <img src="/frontend/public/assets/images/White_queen.png" alt="white queen" style={imgStyle} onError={handleImageError} onLoad={handleImageLoad} />;
                case 'K': return <img src="/frontend/public/assets/images/White_king.png" alt="white king" style={imgStyle} onError={handleImageError} onLoad={handleImageLoad} />;
                case 'P': return <img src="/frontend/public/assets/images/White_pawn.png" alt="white pawn" style={imgStyle} onError={handleImageError} onLoad={handleImageLoad} />;
                default: return '';
            }
        } catch (error) {
            console.error(`Error rendering piece: ${piece}`, error);
            return '';
        }
    };

    return (
        <div
            ref={drag}
            style={{
                display: 'inline-block',
                cursor: 'grab',
            }}
        >
            {renderPiece()}
        </div>
    );
}

function ChessBoard() {
    const { mode } = useParams();
    const [selectedPiece, setSelectedPiece] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [apiError, setApiError] = useState(null);
    const [localBoardData, setLocalBoardData] = useState(null);
    const isMounted = useRef(false);
    const [piecePositions, setPiecePositions] = useState({});
    const [showCoordinates, setShowCoordinates] = useState(false)
    const [statusMessage, setStatusMessage] = useState('Welcome to ChessAI!');
    const [statusColor, setStatusColor] = useState('black');
    const [capturedWhite, setCapturedWhite] = useState([]);
    const [capturedBlack, setCapturedBlack] = useState([]);
    const [moves, setMoves] = useState([]);

    const handleMove = useCallback(async (move) => {
        console.log('=== handleMove Start ===');
        console.log('Formatted Move:', move, 'Type:', typeof move);

        try {
            console.log('Making API request to:', `${axios.defaults.baseURL}/api/make_move`);
            console.log('Request payload:', { move });
            const response = await axios.post('/api/make_move', { move });
            console.log('API Response:', {
                status: response.status,
                statusText: response.statusText,
                headers: response.headers,
                data: response.data
            });
            if (response.data.error) {
                console.error('Move error:', response.data.error);
                console.error('Full error response:', response.data);
                setStatusMessage(response.data.error);
                setStatusColor('red');
                return false;
            }

            if (response.data.gameOver) {
                setStatusMessage(`Game Over. ${response.data.winner} won the game`);
                setStatusColor('green');
            }
            if (response.data.legalMoves && response.data.legalMoves.length === 0 && !response.data.gameOver) {
                setStatusMessage('Stalemate!');
                setStatusColor('blue');
            }
            console.log('Setting new board state:', {
                fen: response.data.fen,
                moves: response.data.moves,
                capturedWhite: response.data.capturedPieces?.white,
                capturedBlack: response.data.capturedPieces?.black
            });

            setLocalBoardData(response.data);
            setCapturedWhite(response.data.capturedPieces?.white || []);
            setCapturedBlack(response.data.capturedPieces?.black || []);
            setMoves(response.data.moves || []);
            console.log('=== handleMove Success ===');
            return true;

        } catch (error) {
            console.error('=== handleMove Error ===');
            console.error('Error type:', error.name);
            console.error('Error message:', error.message);
            console.error('Error stack:', error.stack);
            if (error.response) {
                console.error('Response data:', error.response.data);
                console.error('Response status:', error.response.status);
                console.error('Response headers:', error.response.headers);
            } else if (error.request) {
                console.error('Request made but no response received');
                console.error('Request details:', error.request);
            }
            console.error('Error config:', error.config);
            setStatusMessage('An error occurred while making the move.');
            setStatusColor('red');
            return false;
        }
    }, []);
    const startGame = useCallback(async (mode) => {
        console.log('Start game requested');
        try {
            // Update the URL to use the correct port
            const response = await axios.post(`http://127.0.0.1:6009/api/start_game/${mode}`);
            if (response.data.message === 'Game started') {
                setStatusMessage('Game started.');
                setStatusColor('green');
            }
        } catch (error) {
            console.error('Error starting game:', error);
            setStatusMessage('Error starting game.');
            setStatusColor('red');
        }
    }, []);
    const undoMove = useCallback(async () => {
        console.log('Undo move requested');
        try {
            const response = await axios.post('/api/undo_move');
            if (response.data.error) {
                console.error('Undo move failed:', response.data);
                setStatusMessage(response.data.error);
                setStatusColor('red');
                return false;
            }
            console.log('Setting new board state after undo:', {
                fen: response.data.fen,
                moves: response.data.moves,
            });
            setLocalBoardData(response.data);
            setMoves(response.data.moves || []);
            setStatusMessage('Move undone.');
            setStatusColor('blue');
            return true
        } catch (error) {
            console.error('Error undoing move:', error);
            setStatusMessage('Error undoing move.');
            setStatusColor('red');
            return false
        }
    }, []);
    const redoMove = useCallback(async () => {
        console.log('Redo move requested');
        try {
            const response = await axios.post('/api/redo_move');
            if (response.data.error) {
                console.error('Redo move failed:', response.data);
                setStatusMessage(response.data.error);
                setStatusColor('red');
            }
            console.log('Setting new board state after redo:', {
                fen: response.data.fen,
                moves: response.data.moves,
            });
            setLocalBoardData(response.data);
            setMoves(response.data.moves || []);
            setStatusMessage('Move redone.');
            setStatusColor('blue');
            return true;
        } catch (error) {
            console.error('Error redoing move:', error);
            setStatusMessage('Error redoing move.');
            setStatusColor('red');
            return false;
        }
    }, []);


    const saveGame = useCallback(async () => {
        console.log('Save game requested');
        try {
            const response = await axios.post('/api/save_game', { fen: localBoardData.fen });
            if (response.data.success) {
                setStatusMessage('Game saved successfully!');
                setStatusColor('green');
            } else {
                console.error('Save game failed:', response.data);
                setStatusMessage(response.data.message || 'Failed to save game.');
                setStatusColor('red');
            }
        } catch (error) {
            console.error('Error saving game:', error);
            setStatusMessage('Error saving game.');
            setStatusColor('red');
        }
    }, [localBoardData]);

    const loadGame = useCallback(async () => {
        console.log('Load game requested');
        try {
            const response = await axios.get('/api/load_game');
            if (response.data.fen) {
                setLocalBoardData({ ...localBoardData, fen: response.data.fen });
                setMoves(response.data.moves || []);
                setStatusMessage('Game loaded successfully!');
                setStatusColor('green');
            } else {
                console.error('Load game failed:', response.data);
                setStatusMessage(response.data.message || 'Failed to load game.');
                setStatusColor('red');
            }
        } catch (error) {
            console.error('Error loading game:', error);
            setStatusMessage('Error loading game.');
            setStatusColor('red');
        }
    }, [localBoardData]);

    const resign = useCallback(async () => {
        console.log('Resign game requested');
        try {
            const response = await axios.post('/api/resign_game');
            if (response.data.success) {
                setStatusMessage('You resigned. You lose.');
                setStatusColor('red');
                setLocalBoardData(null);
            } else {
                console.error('Resign game failed:', response.data);
                setStatusMessage('Failed to resign.');
                setStatusColor('red');
            }
        } catch (error) {
            console.error('Error resigning game:', error);
            setStatusMessage('Error resigning game.');
            setStatusColor('red');
        }
    }, []);

    const offerDraw = useCallback(async () => {
        console.log('Offer draw requested');
        try {
            const response = await axios.post('/api/offer_draw');
            if (response.data.success) {
                setStatusMessage('Draw offered.');
                setStatusColor('blue');
            } else {
                console.error('Offer draw failed:', response.data);
                setStatusMessage('Failed to offer draw.');
                setStatusColor('red');
            }
        } catch (error) {
            console.error('Error offering draw:', error);
            setStatusMessage('Error offering draw.');
            setStatusColor('red');
        }
    }, []);

    const fetchBoard = useCallback(async () => {
        const timestamp = Date.now();
        console.log(`[${timestamp}] Fetching board data...`);
        setIsLoading(true);
        setApiError(null);
        try {
            const response = await axios.get('http://127.0.0.1:6009/api/get_board');
            console.log(`[${timestamp}] Board data fetched:`, response.data);
            setLocalBoardData(response.data);
            if (response.data && response.data.fen) {
                const fen = response.data.fen.split(' ')[0];
                const newPiecePositions = {};
                let file = 0;
                let rank = 7;
                let pieceIndex = 0;
                for (const char of fen) {
                    if (char === '/') {
                        rank--;
                        file = 0;
                    } else if (isNaN(parseInt(char))) {
                        for (let i = 0; i < parseInt(char); i++) {
                            const square = `${String.fromCharCode(97 + file)}${8 - rank}`;
                            newPiecePositions[`${square}-${pieceIndex}`] = null;
                            file++;
                            pieceIndex++;
                        }
                    } else {
                        const square = `${String.fromCharCode(97 + file)}${8 - rank}`;
                        newPiecePositions[`${square}-${pieceIndex}`] = char;
                        file++;
                        pieceIndex++;
                    }
                }
                setPiecePositions(newPiecePositions);
            }
        } catch (error) {
            console.error(`[${timestamp}] Error fetching board data`, error);
            setApiError(`Error fetching board: ${error.message}`);
            setStatusMessage(`Error fetching board: ${error.message}`, "error");
        } finally {
            setIsLoading(false);
        }
    }, [setStatusMessage]);

    useEffect(() => {
        if (isMounted.current) {
            return;
        }
        isMounted.current = true;
        const timestamp = Date.now();
        console.log(`[${timestamp}] useEffect called`);
        fetchBoard();
        startGame(mode)
    }, [fetchBoard, mode, startGame]);

    useEffect(() => {
        if (localBoardData && localBoardData.fen) {
            const timestamp = Date.now();
            console.log(`[${timestamp}] Updating piece position after localBoardData update`);
            const fen = localBoardData.fen.split(' ')[0];
            const newPiecePositions = {};
            let file = 0;
            let rank = 7;
            let pieceIndex = 0;
            for (const char of fen) {
                if (char === '/') {
                    rank--;
                    file = 0;
                } else if (isNaN(parseInt(char))) {
                    for (let i = 0; i < parseInt(char); i++) {
                        const square = `${String.fromCharCode(97 + file)}${8 - rank}`;
                        newPiecePositions[`${square}-${pieceIndex}`] = null;
                        file++;
                        pieceIndex++;
                    }
                } else {
                    const square = `${String.fromCharCode(97 + file)}${8 - rank}`;
                    newPiecePositions[`${square}-${pieceIndex}`] = char;
                    file++;
                    pieceIndex++;
                }
            }
            setPiecePositions(newPiecePositions);
        }
    }, [localBoardData]);
    const makeMove = async (move) => {
        const timestamp = Date.now();
        console.log(`[${timestamp}] Making move:`, move);

        try {
            // First validate the move
            const validateResponse = await api.post('/validate_move', { move });
            if (!validateResponse.data.isLegal) {
                setStatusMessage(`Illegal move: ${move}`);
                setStatusColor('red');
                return false;
            }

            // Then make the move
            const response = await api.post('/make_move', { move });
            if (response.data.error) {
                throw new Error(response.data.error);
            }

            // Update board state
            setLocalBoardData(response.data);

            // Update captured pieces if any
            if (response.data.capturedPieces) {
                setCapturedWhite(response.data.capturedPieces.white || []);
                setCapturedBlack(response.data.capturedPieces.black || []);
            }

            // Update move list
            if (response.data.moves) {
                setMoves(response.data.moves);
            }

            // Handle game over conditions
            if (response.data.gameOver) {
                setStatusMessage(`Game Over. ${response.data.winner} won the game`);
                setStatusColor('green');
            } else if (response.data.legalMoves && response.data.legalMoves.length === 0) {
                setStatusMessage('Stalemate!');
                setStatusColor('blue');
            }

            // Play move sound
            playSound(move);
            return true;

        } catch (error) {
            console.error(`[${timestamp}] Error making move`, error);
            setStatusMessage(`Error making move: ${error.message}`);
            setStatusColor('red');
            return false;
        } finally {
            setSelectedPiece(null);
        }
    };


    const handleSquareClick = async (square) => {
        const timestamp = Date.now();
        console.log(`[${timestamp}] Square clicked:`, square);

        if (selectedPiece === null) {
            setSelectedPiece(square);
            console.log(`[${timestamp}] Piece selected:`, square);
            return;
        }

        // If the same square is clicked twice, deselect the piece and return
        if (selectedPiece === square) {
            setSelectedPiece(null);
            console.log(`[${timestamp}] Piece deselected:`, square);
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
                setStatusMessage(`Illegal move: ${move}`, "error");
            }
        } catch (error) {
            console.error(`[${timestamp}] Error validating move`, error);
            setStatusMessage(`Error validating move: ${error.message}`, "error");
            setApiError(`Error validating move: ${error.message}`);
        } finally {
            setSelectedPiece(null);
        }
    };

    const makeAIMove = useCallback(async () => {
        const timestamp = Date.now();
        console.log(`[${timestamp}] Making AI move...`);
        try {
            const response = await axios.post('http://127.0.0.1:6009/api/ai_move');
            console.log(`[${timestamp}] AI move made, response:`, response.data);
            if (response.data) {
                setLocalBoardData(response.data);
            }
            handleMove(null);
            if (response.data.gameOver) {
                setStatusMessage(`Game Over. ${response.data.winner} won the game`, "info");
            }
            if (response.data.legalMoves && response.data.legalMoves.length === 0 && !response.data.gameOver) {
                setStatusMessage('Stalemate!', "info");
            }
            playSound(null, 'move');
        } catch (error) {
            console.error(`[${timestamp}] Error making AI move`, error);
            setStatusMessage(`Error making AI move: ${error.message}`, "error");
            setApiError(`Error making AI move: ${error.message}`);
        }
    }, [handleMove, setStatusMessage, setApiError]);

    const handlePieceDrop = async (square, item) => {
        const timestamp = Date.now();
        console.log(`[${timestamp}] Piece dropped on:`, square, item);

        // If dropping on the same square, do nothing
        if (item.square === square) {
            console.log(`[${timestamp}] Piece dropped on same square, ignoring`);
            return;
        }

        const move = item.square + square;
        try {
            const validateResponse = await axios.post(
                'http://127.0.0.1:6009/api/validate_move',
                { move: move }
            );
            console.log(`[${timestamp}] Move validation response:`, validateResponse.data);
            if (validateResponse.data.isLegal) {
                makeMove(move);
            } else {
                setStatusMessage(`Illegal move: ${move}`, "error");
            }
        } catch (error) {
            console.error(`[${timestamp}] Error validating drop`, error);
            setStatusMessage(`Error validating drop: ${error.message}`, "error");
            setApiError(`Error validating drop: ${error.message}`);
        }
    };

    const toggleCoordinates = () => {
        setShowCoordinates(!showCoordinates);
        console.log('show coordinate' + showCoordinates)
    }
    const renderBoard = () => {
        const timestamp = Date.now();
        console.log(`[${timestamp}] Rendering board...`);

        if (isLoading) {
            return <div>Loading...</div>;
        }

        if (apiError) {
            return <div>{apiError}</div>;
        }
        if (!localBoardData || !localBoardData.fen) {
            return <div>No board data available.</div>;
        }

        const fen = localBoardData.fen.split(' ')[0];
        const rows = fen.split('/').map((row, rowIndex) => {
            const squares = row.split('').reduce((acc, char, fileIndex) => {
                if (isNaN(parseInt(char))) {
                    const square = `${String.fromCharCode(97 + fileIndex)}${8 - rowIndex}`;
                    const isSelected = square === selectedPiece;
                    const pieceKey = `${square}-${rowIndex}-${fileIndex}`;
                    acc.push(
                        <Square
                            key={pieceKey}
                            isLight={(rowIndex + fileIndex) % 2 === 0}
                            onClick={() => handleSquareClick(square)}
                            isSelected={isSelected}
                            onDrop={(item) => handlePieceDrop(square, item)}
                            coordinate={square}
                            showCoordinates={showCoordinates}
                        >
                            {piecePositions[pieceKey] && (
                                <Piece
                                    piece={piecePositions[pieceKey]}
                                    square={square}
                                    onMove={() => { }}
                                />
                            )}
                        </Square>
                    );
                } else {
                    for (let i = 0; i < parseInt(char); i++) {
                        const currentFileIndex = fileIndex + i;
                        const square = `${String.fromCharCode(97 + currentFileIndex)}${8 - rowIndex}`;
                        const isSelected = square === selectedPiece;
                        const pieceKey = `${square}-${rowIndex}-${currentFileIndex}`;
                        acc.push(
                            <Square
                                key={pieceKey}
                                isLight={(rowIndex + currentFileIndex) % 2 === 0}
                                onClick={() => handleSquareClick(square)}
                                isSelected={isSelected}
                                onDrop={(item) => handlePieceDrop(square, item)}
                                coordinate={square}
                                showCoordinates={showCoordinates}

                            >
                                {piecePositions[pieceKey] && (
                                    <Piece
                                        piece={piecePositions[pieceKey]}
                                        square={square}
                                        onMove={() => { }}
                                    />
                                )}
                            </Square>
                        );
                    }
                    fileIndex += parseInt(char);
                }

                return acc;
            }, []);
            return <div key={rowIndex} className='board-row'>{squares}</div>;
        });
        return <div className="chessboard">{rows}
            <button onClick={toggleCoordinates}>Toggle Coordinates</button>
        </div>;
    };


    useEffect(() => {
        if (localBoardData &&
            localBoardData.fen &&
            localBoardData.fen.split(' ')[1] === 'b' &&
            !localBoardData.gameOver &&
            mode !== 'user_vs_user') {
            makeAIMove();
        }
    }, [localBoardData, mode, makeAIMove]); // Added makeAIMove to dependencies

    const playSound = (move) => {
        if (move === null) {
            const moveSound = new Audio('/frontend/public/assets/sounds/move.mp3');
            moveSound.play().catch(err => console.error('Sound play error:', err));
            return
        }
        if (localBoardData.moves && localBoardData.moves.length > 0) {
            const capturedPieces = localBoardData.capturedPieces;
            if (capturedPieces && capturedPieces.white.length > capturedWhite.length || capturedPieces && capturedPieces.black.length > capturedBlack.length) {
                const captureSound = new Audio('/frontend/public/assets/sounds/capture.mp3');
                captureSound.play().catch(err => console.error('Sound play error:', err));
            } else {
                const moveSound = new Audio('/frontend/public/assets/sounds/move.mp3');
                moveSound.play().catch(err => console.error('Sound play error:', err));
            }
        }
        setMoves(localBoardData.moves)
    }
    return (
        <DndProvider backend={HTML5Backend}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <StatusBar message={statusMessage} color={statusColor} />
                <div style={{ display: 'flex' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                        {renderBoard()}
                        <ControlPanel
                            undoMove={undoMove}
                            redoMove={redoMove}
                            saveGame={saveGame}
                            loadGame={loadGame}
                            resign={resign}
                            offerDraw={offerDraw}
                            setGameMode={() => { }}
                            toggleTheme={() => { }}
                            startGame={() => { }}
                        />
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', maxWidth: '300px', minWidth: '200px', alignItems: 'center' }}>
                        <CapturedPieces capturedWhite={capturedWhite} capturedBlack={capturedBlack} />
                        <MoveList moves={moves} />
                    </div>
                </div>
            </div>
        </DndProvider>
    );
}

export default ChessBoard;
