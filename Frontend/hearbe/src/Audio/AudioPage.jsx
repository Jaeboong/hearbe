import React from 'react';
import Spline from '@splinetool/react-spline';


export default function AudioPage() {
    return (
        <div style={{ width: '100vw', height: '100vh', overflow: 'hidden', backgroundColor: 'black' }}>
            <div style={{ width: '100%', height: '100%' }}>
                <Spline scene="https://prod.spline.design/IaDdv3c70ekbtAdf/scene.splinecode" />
            </div>
        </div>
    );
}
