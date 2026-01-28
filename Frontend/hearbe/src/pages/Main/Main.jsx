import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Volume2, Zap, Users, Shield, ChevronRight } from 'lucide-react';
import hLogo from '../../assets/h-logo.png';
import './Main.css';

export default function Main() {
    const navigate = useNavigate();
    const [showMcpModal, setShowMcpModal] = useState(false);

    const handleModeClick = (mode) => {
        if (mode === 'common') navigate('/login-c');
        else if (mode === 'sharing') navigate('/login-s');
        else if (mode === 'big') navigate('/login-b');
        else navigate('/login-a');
    };

    return (
        <div className="theme-c">
            <div className="main-page">
                <header className="main-header">
                    <div className="header-inner">
                        <img src={hLogo} alt="HearBe Logo" className="logo" />
                        <div className="header-btns">
                            <button className="btn-secondary" onClick={() => { localStorage.clear(); window.location.reload(); }}>
                                🔄 테스트 초기화
                            </button>
                            <button className="btn-primary" onClick={() => setShowMcpModal(true)}>
                                <Shield size={16} /> MCP 다운로드
                            </button>
                        </div>
                    </div>
                </header>

                <main className="main-body">
                    <section className="hero-card">
                        <div className="hero-content">
                            <div className="hero-badge">
                                <Volume2 size={14} /> 음성 기반 쇼핑 플랫폼
                            </div>
                            <h1 className="hero-title">
                                모든 사람을 위한<br />접근 가능한 쇼핑
                            </h1>
                            <p className="hero-subtitle">
                                시각장애인, 고령자, 일반 사용자 모두를 위한<br />
                                4가지 맞춤형 쇼핑 모드.
                            </p>
                        </div>
                        <div className="hero-visual">
                            <div className="visual-circle" />
                        </div>
                    </section>

                    <section className="mode-selection">
                        <h2 className="section-title">쇼핑 모드 선택</h2>
                        <p className="section-desc">아래 4가지 모드 중 원하는 방식을 선택하세요</p>

                        <div className="mode-list">
                            <button className="mode-item" onClick={() => handleModeClick('audio')}>
                                <div className="mode-icon-box orange">
                                    <Volume2 size={24} />
                                </div>
                                <div className="mode-text">
                                    <span className="mode-label orange-text">A형 · 시각장애인 전용</span>
                                    <h3 className="mode-name">음성 안내 쇼핑</h3>
                                    <div className="mode-tags">
                                        <span>음성 안내</span><span>고대비</span>
                                    </div>
                                </div>
                                <ChevronRight className="arrow" />
                            </button>

                            <button className="mode-item" onClick={() => handleModeClick('big')}>
                                <div className="mode-icon-box blue">
                                    <Zap size={24} />
                                </div>
                                <div className="mode-text">
                                    <span className="mode-label blue-text">B형 · 저시력자 전용</span>
                                    <h3 className="mode-name">큰 글씨 쇼핑</h3>
                                    <div className="mode-tags">
                                        <span>큰 글씨</span><span>간편 UI</span>
                                    </div>
                                </div>
                                <ChevronRight className="arrow" />
                            </button>

                            <button className="mode-item" onClick={() => handleModeClick('common')}>
                                <div className="mode-icon-box green">
                                    <Users size={24} />
                                </div>
                                <div className="mode-text">
                                    <span className="mode-label green-text">C형 · 일반 사용자용</span>
                                    <h3 className="mode-name">일반 쇼핑</h3>
                                    <div className="mode-tags">
                                        <span>빠른 탐색</span><span>표준 UI</span>
                                    </div>
                                </div>
                                <ChevronRight className="arrow" />
                            </button>

                            <button className="mode-item" onClick={() => handleModeClick('sharing')}>
                                <div className="mode-icon-box purple">
                                    <Shield size={24} />
                                </div>
                                <div className="mode-text">
                                    <span className="mode-label purple-text">S형 · 원격 지원</span>
                                    <h3 className="mode-name">공유 쇼핑</h3>
                                    <div className="mode-tags">
                                        <span>화면 공유</span><span>실시간 지원</span>
                                    </div>
                                </div>
                                <ChevronRight className="arrow" />
                            </button>
                        </div>
                    </section>
                </main>
            </div>
        </div>
    );
}