import React, { useState } from 'react';
import Spline from '@splinetool/react-spline';

function hasWebGLSupport() {
    try {
        const canvas = document.createElement('canvas');
        return Boolean(
            canvas.getContext('webgl2') ||
            canvas.getContext('webgl') ||
            canvas.getContext('experimental-webgl')
        );
    } catch {
        return false;
    }
}

function WebGLFallback() {
    return (
        <div style={{ width: '100vw', height: '100vh', backgroundColor: '#000', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: '2rem' }}>
            <div>
                <h2 style={{ marginBottom: '0.75rem' }}>WebGL is unavailable</h2>
                <p style={{ opacity: 0.75 }}>현재 환경에서는 Spline 3D 렌더링을 사용할 수 없습니다.</p>
            </div>
        </div>
    );
}

export default function AudioPage() {
    const [canRenderSpline, setCanRenderSpline] = useState(() => hasWebGLSupport());

    if (!canRenderSpline) {
        return <WebGLFallback />;
    }

    return (
        <div style={{ width: '100vw', height: '100vh', overflow: 'hidden', backgroundColor: 'black' }}>
            <div style={{ width: '100%', height: '100%' }}>
                <Spline
                    scene="https://prod.spline.design/IaDdv3c70ekbtAdf/scene.splinecode"
                    onError={() => setCanRenderSpline(false)}
                />
            </div>
        </div>
    );
}
