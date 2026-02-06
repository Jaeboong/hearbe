import React from 'react';
import Spline from '@splinetool/react-spline';

export default function SplinePage() {
    return (
        <div style={{ width: '100vw', height: '100vh', overflow: 'hidden' }}>
            <Spline scene="https://prod.spline.design/IaDdv3c70ekbtAdf/scene.splinecode" />
        </div>
    );
}
