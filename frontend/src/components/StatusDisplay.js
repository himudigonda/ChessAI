// frontend/src/components/StatusDisplay.js
import React from 'react';

function StatusDisplay({ message, type }) {
    const statusClass = `status-message ${type || 'info'}`;
    return <div className={statusClass}>{message}</div>;
}
export default StatusDisplay;