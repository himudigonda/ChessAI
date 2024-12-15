// src/components/MoveList.jsx
import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import PropTypes from 'prop-types';
import { List, ListItem, ListItemText } from '@material-ui/core';

const useStyles = makeStyles({
  moveList: {
    maxHeight: '200px',
    overflowY: 'auto',
    backgroundColor: '#f0f0f0',
    padding: '10px',
    borderRadius: '5px',
  },
});

const MoveList = ({ moves }) => {
  const classes = useStyles();

  return (
    <div className={classes.moveList}>
      <List>
        {moves.map((move, index) => (
          <ListItem key={index}>
            <ListItemText primary={`${index + 1}. ${move}`} />
          </ListItem>
        ))}
      </List>
    </div>
  );
};

MoveList.propTypes = {
  moves: PropTypes.arrayOf(PropTypes.string).isRequired,
};

export default MoveList;
