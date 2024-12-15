// src/App.jsx
import React, { useState } from 'react';
import { Container, Grid } from '@material-ui/core';
import ChessBoard from './components/ChessBoard';
import ControlPanel from './components/ControlPanel';
import StatusBar from './components/StatusBar';
import CapturedPieces from './components/CapturedPieces';
import MoveList from './components/MoveList';
import axios from './services/api';
import './App.css';

function App() {
  const [gameMode, setGameMode] = useState('user_vs_user');
  const [statusMessage, setStatusMessage] = useState('Welcome to ChessAI!');
  const [statusColor, setStatusColor] = useState('black');
  const [capturedWhite, setCapturedWhite] = useState([]);
  const [capturedBlack, setCapturedBlack] = useState([]);
  const [moves, setMoves] = useState([]);
  const [fen, setFen] = useState('start');
  const [history, setHistory] = useState([]);

  const handleMove = async (sourceSquare, targetSquare) => {
    const move = `${sourceSquare}${targetSquare}`;
    console.log(`Attempting move: ${move}`);
    try {
      const response = await axios.post(`/api/make_move`, { move });
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
      setFen(response.data.fen);
      setHistory((prevHistory) => [...prevHistory, response.data.moves]);
      setCapturedWhite(response.data.capturedPieces.white || []);
      setCapturedBlack(response.data.capturedPieces.black || []);
      return true;
    } catch (error) {
      console.error('Error making move:', error);
      alert('An error occurred while making the move.');
      return false;
    }
  };

  const undoMove = () => {
    console.log('Undo move requested');
    try {
      // Implement undo functionality by calling backend API or managing state
      alert('Undo Move functionality to be implemented.');
    } catch (error) {
      console.error('Error undoing move:', error);
    }
  };

  const redoMove = () => {
    console.log('Redo move requested');
    try {
      // Implement redo functionality by calling backend API or managing state
      alert('Redo Move functionality to be implemented.');
    } catch (error) {
      console.error('Error redoing move:', error);
    }
  };

  const saveGame = async () => {
    console.log('Save game requested');
    try {
      const response = await axios.post('/save_game', { fen });
      if (response.data.success) {
        setStatusMessage('Game saved successfully!');
        setStatusColor('green');
      } else {
        console.error('Save game failed:', response.data);
        setStatusMessage('Failed to save game.');
        setStatusColor('red');
      }
    } catch (error) {
      console.error('Error saving game:', error);
      setStatusMessage('Error saving game.');
      setStatusColor('red');
    }
  };

  const loadGame = async () => {
    console.log('Load game requested');
    try {
      const response = await axios.get('/load_game');
      if (response.data.fen) {
        setFen(response.data.fen);
        setMoves(response.data.moves || []);
        setStatusMessage('Game loaded successfully!');
        setStatusColor('green');
      } else {
        console.error('Load game failed:', response.data);
        setStatusMessage('Failed to load game.');
        setStatusColor('red');
      }
    } catch (error) {
      console.error('Error loading game:', error);
      setStatusMessage('Error loading game.');
      setStatusColor('red');
    }
  };

  const resign = async () => {
    console.log('Resign game requested');
    try {
      const response = await axios.post('/resign_game');
      if (response.data.success) {
        setStatusMessage('You resigned. You lose.');
        setStatusColor('red');
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
  };

  const offerDraw = async () => {
    console.log('Offer draw requested');
    try {
      const response = await axios.post('/offer_draw');
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
  };

  const toggleTheme = () => {
    console.log('Toggle theme requested');
    try {
      // Implement theme toggling logic
      alert('Theme toggling to be implemented.');
    } catch (error) {
      console.error('Error toggling theme:', error);
    }
  };

  return (
    <Container className="App">
      <h1>ChessAI</h1>
      <ControlPanel
        startGame={() => {
          console.log('Start game requested');
          alert('Start Game functionality to be implemented.');
        }}
        undoMove={undoMove}
        redoMove={redoMove}
        saveGame={saveGame}
        loadGame={loadGame}
        resign={resign}
        offerDraw={offerDraw}
        toggleTheme={toggleTheme}
        setGameMode={(mode) => {
          console.log(`Game mode set to: ${mode}`);
          setGameMode(mode);
        }}
      />
      <StatusBar message={statusMessage} color={statusColor} />
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <ChessBoard
            gameMode={gameMode}
            onMove={handleMove}
            capturedPieces={{ white: capturedWhite, black: capturedBlack }}
            setCapturedPieces={(captured) => {
              console.log('Setting captured pieces:', captured);
              setCapturedWhite(captured.white);
              setCapturedBlack(captured.black);
            }}
            setFen={(newFen) => {
              console.log('Setting FEN:', newFen);
              setFen(newFen);
            }}
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <CapturedPieces capturedWhite={capturedWhite} capturedBlack={capturedBlack} />
          <MoveList moves={moves} />
        </Grid>
      </Grid>
    </Container>
  );
}

export default App;
