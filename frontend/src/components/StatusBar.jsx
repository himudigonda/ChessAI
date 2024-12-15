// src/components/StatusBar.jsx
import React from 'react';
import { Typography, makeStyles } from '@material-ui/core';
import PropTypes from 'prop-types';

const useStyles = makeStyles({
    statusBar: {
        marginTop: '20px',
        textAlign: 'center',
    },
    message: {
        fontSize: '1.2em',
    },
});

const StatusBar = ({ message, color = 'black' }) => { // Default parameter
    const classes = useStyles();

    return (
        <div className={classes.statusBar}>
            <Typography className={classes.message} style={{ color }}>
                {message}
            </Typography>
        </div>
    );
};

StatusBar.propTypes = {
    message: PropTypes.string.isRequired,
    color: PropTypes.string,
};

export default StatusBar;
