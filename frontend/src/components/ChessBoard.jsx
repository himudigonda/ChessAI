import React, { useState } from 'react';
import { Chessboard } from 'react-chessboard';
import PropTypes from 'prop-types';
import { makeStyles } from '@material-ui/core/styles';
import axios from '../services/api';

const useStyles = makeStyles({
    boardContainer: {
        width: '100%',
        maxWidth: '700px',
        margin: 'auto',
    }
});

const ChessBoardComponent = ({
    gameMode,
    onMove,
    capturedPieces,
    setCapturedPieces,
    setFen,
    onStatusChange // Add this prop
}) => {
    const classes = useStyles();
    const [position, setPosition] = useState('start');

    useEffect(() => {
        // Reset board when game mode changes
        setPosition('start');
    }, [gameMode]);

    const handleMove = async (sourceSquare, targetSquare) => {
        const move = `${sourceSquare}${targetSquare}`;
        console.log(`Attempting move: ${move}`);
        try {
            const response = await axios.post('/make_move', { move });
            console.log('Move response:', response.data);
            if (response.data.isCapture) {
                const captureSound = new Audio('/assets/sounds/capture.mp3');
                captureSound.play();
            }
            if (response.data.error) {
                console.error('Move error:', response.data.error);
                alert(response.data.error);
                return false;
            }
            setPosition(response.data.fen);
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
    onStatusChange: PropTypes.func.isRequired // Add this prop type
};

export default ChessBoardComponent;
