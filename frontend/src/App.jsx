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

  // In App.jsx, enhance the handleMove function
  const handleMove = async (sourceSquare, targetSquare) => {
    console.log('=== handleMove Start ===');
    console.log('Source Square:', sourceSquare, 'Type:', typeof sourceSquare);
    console.log('Target Square:', targetSquare, 'Type:', typeof targetSquare);

    const move = sourceSquare + targetSquare;
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

      if (response.data.isCapture) {
        console.log('Capture detected, playing sound');
        const captureSound = new Audio('/assets/sounds/capture.mp3');
        captureSound.play().catch(err => console.error('Sound play error:', err));
      }

      if (response.data.error) {
        console.error('Move error:', response.data.error);
        console.error('Full error response:', response.data);
        alert(response.data.error);
        return false;
      }

      console.log('Setting new board state:', {
        fen: response.data.fen,
        moves: response.data.moves,
        capturedWhite: response.data.capturedPieces?.white,
        capturedBlack: response.data.capturedPieces?.black
      });

      setFen(response.data.fen);
      setHistory((prevHistory) => {
        console.log('Previous history:', prevHistory);
        const newHistory = [...prevHistory, response.data.moves];
        console.log('New history:', newHistory);
        return newHistory;
      });
      setCapturedWhite(response.data.capturedPieces?.white || []);
      setCapturedBlack(response.data.capturedPieces?.black || []);

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
            onStatusChange={(message, color) => {
              console.log('Status change:', message, color);
              setStatusMessage(message);
              setStatusColor(color);
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
