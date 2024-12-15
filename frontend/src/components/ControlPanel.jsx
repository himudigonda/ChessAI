// src/components/ControlPanel.jsx
import React, { useRef } from 'react';
import { Button, ButtonGroup, makeStyles } from '@material-ui/core';
import PropTypes from 'prop-types';

const useStyles = makeStyles({
  controlPanel: {
    margin: '20px 0',
    display: 'flex',
    justifyContent: 'center',
    flexWrap: 'wrap',
  },
  buttonGroup: {
    margin: '10px',
  },
});

const ControlPanel = ({
  startGame,
  undoMove,
  redoMove,
  saveGame,
  loadGame,
  resign,
  offerDraw,
  toggleTheme,
  setGameMode,
}) => {
  const classes = useStyles();
  const buttonGroupRef = useRef(null); // Create a ref

  return (
    <div className={classes.controlPanel}>
      <ButtonGroup
        variant="contained"
        color="primary"
        ref={buttonGroupRef} // Attach ref directly
        className={classes.buttonGroup}
      >
        <Button onClick={() => setGameMode('user_vs_user')}>User vs User</Button>
        <Button onClick={() => setGameMode('user_vs_stockfish')}>User vs Stockfish</Button>
        <Button onClick={() => setGameMode('user_vs_cai')}>User vs cAI</Button>
        <Button onClick={() => setGameMode('watch_cai_vs_stockfish')}>Watch cAI vs Stockfish</Button>
      </ButtonGroup>
      <ButtonGroup
        variant="contained"
        color="secondary"
        className={classes.buttonGroup}
      >
        <Button onClick={undoMove}>Undo</Button>
        <Button onClick={redoMove}>Redo</Button>
        <Button onClick={saveGame}>Save</Button>
        <Button onClick={loadGame}>Load</Button>
        <Button onClick={resign}>Resign</Button>
        <Button onClick={offerDraw}>Offer Draw</Button>
        <Button onClick={toggleTheme}>Toggle Theme</Button>
      </ButtonGroup>
    </div>
  );
};

ControlPanel.propTypes = {
  startGame: PropTypes.func.isRequired,
  undoMove: PropTypes.func.isRequired,
  redoMove: PropTypes.func.isRequired,
  saveGame: PropTypes.func.isRequired,
  loadGame: PropTypes.func.isRequired,
  resign: PropTypes.func.isRequired,
  offerDraw: PropTypes.func.isRequired,
  toggleTheme: PropTypes.func.isRequired,
  setGameMode: PropTypes.func.isRequired,
};

export default ControlPanel;
