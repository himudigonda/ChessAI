// src/components/CapturedPieces.jsx
import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import PropTypes from 'prop-types';

const useStyles = makeStyles({
  capturedContainer: {
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: '20px',
  },
  capturedList: {
    display: 'flex',
    flexWrap: 'wrap',
    width: '45%',
  },
  pieceImage: {
    width: '30px',
    height: '30px',
    margin: '2px',
  },
  title: {
    textAlign: 'center',
    marginBottom: '5px',
  },
});

const CapturedPieces = ({ capturedWhite, capturedBlack }) => {
  const classes = useStyles();

  return (
    <div className={classes.capturedContainer}>
      <div>
        <div className={classes.title}>Captured by Black</div>
        <div className={classes.capturedList}>
          {capturedWhite.map((piece, index) => (
            <img
              key={index}
              src={`/assets/images/${piece}.png`}
              alt={piece}
              className={classes.pieceImage}
            />
          ))}
        </div>
      </div>
      <div>
        <div className={classes.title}>Captured by White</div>
        <div className={classes.capturedList}>
          {capturedBlack.map((piece, index) => (
            <img
              key={index}
              src={`/assets/images/${piece}.png`}
              alt={piece}
              className={classes.pieceImage}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

CapturedPieces.propTypes = {
  capturedWhite: PropTypes.arrayOf(PropTypes.string).isRequired,
  capturedBlack: PropTypes.arrayOf(PropTypes.string).isRequired,
};

export default CapturedPieces;
