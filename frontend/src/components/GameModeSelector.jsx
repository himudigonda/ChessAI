// src/components/GameModeSelector.jsx
import React from 'react';
import { Button, ButtonGroup } from '@material-ui/core';
import PropTypes from 'prop-types';

const GameModeSelector = ({ setGameMode }) => {
  return (
    <ButtonGroup variant="outlined" color="primary">
      <Button onClick={() => setGameMode('user_vs_user')}>User vs User</Button>
      <Button onClick={() => setGameMode('user_vs_stockfish')}>User vs Stockfish</Button>
      <Button onClick={() => setGameMode('user_vs_cai')}>User vs cAI</Button>
      <Button onClick={() => setGameMode('watch_cai_vs_stockfish')}>Watch cAI vs Stockfish</Button>
    </ButtonGroup>
  );
};

GameModeSelector.propTypes = {
  setGameMode: PropTypes.func.isRequired,
};

export default GameModeSelector;
