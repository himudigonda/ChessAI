// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import ChessBoard from './components/ChessBoard';
import LandingPage from './components/LandingPage';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/game/:mode" element={<ChessBoard />} />
      </Routes>
    </Router>
  );
}

export default App;
