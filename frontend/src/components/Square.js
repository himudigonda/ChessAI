// frontend/src/components/Square.js
import React from 'react';

const Square = ({
    piece,
    isLight,
    onClick,
    isSelected,
}) => {
    const squareClass = `square ${isLight ? 'light' : 'dark'} ${isSelected ? 'selected' : ''}`;

    return (
        <div
            className={squareClass}
            onClick={onClick}
        >
            {piece}
        </div>
    );
};
export default Square;