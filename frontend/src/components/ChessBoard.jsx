// src/components/ChessBoard.jsx
import React, { useEffect, useState } from 'react';
import { Chessboard } from 'react-chessboard';
import PropTypes from 'prop-types';
import { makeStyles } from '@material-ui/core/styles';
import axios from '../services/api';

const useStyles = makeStyles({
    boardContainer: {
        width: '100%',
        maxWidth: '600px',
        margin: 'auto',
    },
    lightSquare: {
        backgroundColor: '#f0d9b5', // Lighter color for light squares
    },
    darkSquare: {
        backgroundColor: '#b58863',
    },
});

const ChessBoardComponent = ({ gameMode, onMove, capturedPieces = { white: [], black: [] }, setCapturedPieces, setFen }) => {
    const classes = useStyles();
    const [position, setPosition] = useState('start');
    const [history, setHistory] = useState([]);

    useEffect(() => {
        // Reset board when game mode changes
        setPosition('start');
        setHistory([]);
    }, [gameMode]);

    const handleMove = async (sourceSquare, targetSquare) => {
        const move = `${sourceSquare}${targetSquare}`;
        console.log(`Attempting move: ${move}`);
        try {
            const response = await axios.post(`/make_move`, { move });
            console.log('Move response:', response.data);
            if (response.data.isCapture) {
                const captureSound = new Audio('/assets/sounds/capture.mp3');
                captureSound.play();
            } else {
                const moveSound = new Audio('/assets/sounds/move.mp3');
                moveSound.play();
            }
            if (response.data.error) {
                console.error('Move error:', response.data.error);
                alert(response.data.error);
                return false;
            }
            setPosition(response.data.fen);
            setHistory((prevHistory) => [...prevHistory, response.data.moves]);
            setCapturedPieces(response.data.capturedPieces || { white: [], black: [] });
            setFen(response.data.fen);
            onMove(response.data);
            return true;
        } catch (error) {
            console.error('Error making move:', error);
            alert('An error occurred while making the move.');
            return false;
        }
    };

    return (
        <div className={classes.boardContainer}>
            <Chessboard
                position={position}
                onPieceDrop={(sourceSquare, targetSquare) => handleMove(sourceSquare, targetSquare)}
                boardStyle={{
                    lightSquareStyle: classes.lightSquare,
                    darkSquareStyle: classes.darkSquare,
                }}
            />
        </div>
    );
};

ChessBoardComponent.propTypes = {
    gameMode: PropTypes.string.isRequired,
    onMove: PropTypes.func.isRequired,
    capturedPieces: PropTypes.object,
    setCapturedPieces: PropTypes.func.isRequired,
    setFen: PropTypes.func.isRequired,
};

export default ChessBoardComponent;
