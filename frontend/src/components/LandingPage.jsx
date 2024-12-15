// src/components/LandingPage.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Container, makeStyles } from '@material-ui/core';

const useStyles = makeStyles((theme) => ({
    landingPage: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        background: 'linear-gradient(45deg, #e6f7ff 30%, #ccebff 90%)',
        textAlign: 'center',
    },
    button: {
        margin: theme.spacing(2),
        padding: theme.spacing(2, 4),
        fontSize: '1.2rem',
        background: 'linear-gradient(to right, #5cb8ff, #337ab7)', // Example gradient
        color: 'white',
        '&:hover': {
            background: 'linear-gradient(to right, #337ab7, #5cb8ff)',
        },
    },
    title: {
        marginBottom: theme.spacing(4)
    }
}));

const LandingPage = () => {
    const classes = useStyles();
    const navigate = useNavigate();

    const handleGameModeSelect = (mode) => {
        navigate(`/game/${mode}`);
    };

    return (
        <Container className={classes.landingPage}>
            <h1 className={classes.title}>Welcome to ChessAI</h1>
            <Button className={classes.button} onClick={() => handleGameModeSelect('user_vs_user')}>User vs User</Button>
            <Button className={classes.button} onClick={() => handleGameModeSelect('user_vs_stockfish')}>User vs Stockfish</Button>
            <Button className={classes.button} onClick={() => handleGameModeSelect('user_vs_cai')}>User vs cAI</Button>
            <Button className={classes.button} onClick={() => handleGameModeSelect('watch_cai_vs_stockfish')}>Watch cAI vs Stockfish</Button>
        </Container>
    );
};

export default LandingPage;
