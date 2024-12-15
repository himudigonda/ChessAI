// frontend/src/components/Square.jsx
import React from 'react';
import PropTypes from 'prop-types';
import { makeStyles } from '@material-ui/core/styles';
import { useDrop } from 'react-dnd';

const useStyles = makeStyles({
    square: {
        width: '60px',
        height: '60px',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        cursor: 'pointer',
        position: 'relative',
        transition: 'all 0.2s ease',
        '&:hover': {
            opacity: 0.8,
            transform: 'scale(1.02)',
        }
    },
    selected: {
        backgroundColor: '#7ea9e0 !important',
        boxShadow: 'inset 0 0 10px rgba(0,0,0,0.2)',
    },
    dropTarget: {
        backgroundColor: '#90EE90 !important',
        boxShadow: 'inset 0 0 10px rgba(0,0,0,0.2)',
    },
    light: {
        backgroundColor: '#ffffff',
        '&:hover': {
            backgroundColor: '#e6e6e6',
        }
    },
    dark: {
        backgroundColor: '#b58863',
        '&:hover': {
            backgroundColor: '#a57853',
        }
    },
    coordinates: {
        position: 'absolute',
        fontSize: '12px',
        opacity: 0.7,
        userSelect: 'none',
        '&.file': {
            bottom: '2px',
            right: '2px',
        },
        '&.rank': {
            top: '2px',
            left: '2px',
        }
    }
});

const Square = ({
    isLight,
    children,
    onClick,
    isSelected = false,  // Default parameter instead of defaultProps
    onDrop,
    coordinate = '',     // Default parameter instead of defaultProps
    showCoordinates = false  // Default parameter instead of defaultProps
}) => {
    const classes = useStyles();

    // Add useDrop hook
    const [{ isOver }, drop] = useDrop({
        accept: 'piece',
        drop: (item) => handleDrop(item),
        collect: (monitor) => ({
            isOver: !!monitor.isOver()
        })
    });

    // Handle drop with error boundary
    const handleDrop = (item) => {
        try {
            onDrop(item);
        } catch (error) {
            console.error('Error handling piece drop:', error);
        }
    };

    return (
        <div
            ref={drop}
            onClick={onClick}
            className={`${classes.square}
                     ${isLight ? classes.light : classes.dark}
                     ${isSelected ? classes.selected : ''}
                     ${isOver ? classes.dropTarget : ''}`}
            data-square={coordinate}
        >
            {children}
            {showCoordinates && coordinate && (
                <>
                    {coordinate.charAt(1) === '1' && (
                        <span className={`${classes.coordinates} file`}>
                            {coordinate.charAt(0)}
                        </span>
                    )}
                    {coordinate.charAt(0) === 'a' && (
                        <span className={`${classes.coordinates} rank`}>
                            {coordinate.charAt(1)}
                        </span>
                    )}
                </>
            )}
        </div>
    );
};
Square.propTypes = {
    isLight: PropTypes.bool.isRequired,
    children: PropTypes.node,
    onClick: PropTypes.func.isRequired,
    isSelected: PropTypes.bool,
    onDrop: PropTypes.func.isRequired,
    coordinate: PropTypes.string,
    showCoordinates: PropTypes.bool
};

Square.defaultProps = {
    isSelected: false,
    showCoordinates: false,
    coordinate: ''
};

export default Square;
