// frontend/src/components/ChessBoard.js
import { DndProvider, useDrag } from 'react-dnd';
import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import Square from './Square';
import './ChessBoard.css';
import { HTML5Backend } from 'react-dnd-html5-backend';

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

function ChessBoard({ mode, onMove, onStatusChange, playSound, boardData }) {
    const [selectedPiece, setSelectedPiece] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [apiError, setApiError] = useState(null);
    const [localBoardData, setLocalBoardData] = useState(boardData);
    const isMounted = useRef(false);
    const [piecePositions, setPiecePositions] = useState({});
    const [showCoordinates, setShowCoordinates] = useState(false)

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

    const handleSquareClick = async (square) => {
        const timestamp = Date.now();
        console.log(`[${timestamp}] Square clicked:`, square);
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
            onStatusChange('', "info");
            if (response.data.gameOver) {
                onStatusChange(`Game Over. ${response.data.winner} won the game`, "info");
            }
            if (response.data.legalMoves && response.data.legalMoves.length === 0 && !response.data.gameOver) {
                onStatusChange('Stalemate!', "info");
            }
            if (response.data) {
                setLocalBoardData(response.data);
            }
            playSound(move);
            if (response.data.fen.split(' ')[1] === 'b' && !response.data.gameOver) {
                return;
            }
        } catch (error) {
            console.error(`[${timestamp}] Error making move`, error);
            onStatusChange(`Error making move: ${error.message}`, "error");
            setApiError(`Error making move: ${error.message}`);
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
            onMove(null);
            if (response.data.gameOver) {
                onStatusChange(`Game Over. ${response.data.winner} won the game`, "info");
            }
            if (response.data.legalMoves && response.data.legalMoves.length === 0 && !response.data.gameOver) {
                onStatusChange('Stalemate!', "info");
            }
            playSound(null, 'move');
        } catch (error) {
            console.error(`[${timestamp}] Error making AI move`, error);
            onStatusChange(`Error making AI move: ${error.message}`, "error");
            setApiError(`Error making AI move: ${error.message}`);
        }
    }, [onMove, onStatusChange, playSound, setApiError]);

    const handlePieceDrop = async (square, item) => {
        const timestamp = Date.now();
        console.log(`[${timestamp}] Piece dropped on:`, square, item);
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
                onStatusChange(`Illegal move: ${move}`, "error");
            }
        } catch (error) {
            console.error(`[${timestamp}] Error validating drop`, error);
            onStatusChange(`Error validating drop: ${error.message}`, "error");
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
            <button onClick={toggleCoordinates}>Toggle Coordinates</button></div>;
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

    return (
        <DndProvider backend={HTML5Backend}>
            {renderBoard()}
        </DndProvider>
    );
}

export default ChessBoard;
