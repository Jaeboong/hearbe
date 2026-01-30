import React from 'react';
import './BackButtonA.css';

const BackButton = ({ onClick, style, variant = 'yellow' }) => {
    return (
        <div className={`global-back-button ${variant}`} onClick={onClick} style={style}>
            <svg viewBox="0 0 24 24" className="back-arrow-svg">
                <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z" />
            </svg>
        </div>
    );
};

export default BackButton;
