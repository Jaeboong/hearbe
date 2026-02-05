import React, { useState, useEffect } from 'react';
import Spline from '@splinetool/react-spline';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import './Intro.css';

import introAudio1 from '../../assets/Intro/intro1.wav';
import introAudio2 from '../../assets/Intro/intro2.wav';
import introAudio3 from '../../assets/Intro/intro3.wav';

const STEPS = [
    { title: "목소리만으로 완성하는 새로운 쇼핑 경험", desc: "복잡한 화면 대신 당신의 목소리에 귀를 기울입니다.", audioSrc: introAudio1, duration: 5000 },
    { title: "보이지 않아도, 스스로 선택하는 쇼핑", desc: "복잡한 상품 정보도 HearBe가 알기 쉽게 읽어드립니다.", audioSrc: introAudio2, duration: 5000 },
    { title: "검색부터 결제까지, HearBe와 함께 시작해보세요", desc: "찾고 싶은 물건을 말하면 결제까지 한 번에 도와드려요.", audioSrc: introAudio3, duration: 5000 },
];

export default function Intro() {
    const [currentStep, setCurrentStep] = useState(0);
    const [isTransitioning, setIsTransitioning] = useState(false);
    const [hasStarted, setHasStarted] = useState(false); // 시작 화면 제어
    const [splineFailed, setSplineFailed] = useState(false);
    const splineLoadedRef = React.useRef(false);
    const navigate = useNavigate();

    // 오디오와 타이머 객체 관리 (중복 실행 방지)
    const audioRef = React.useRef(null);
    const timerRef = React.useRef(null);
    const isMountedRef = React.useRef(true);

    // Spline 로딩 타임아웃: 일정 시간 내 로드 안 되면 fallback 표시
    useEffect(() => {
        const timeout = setTimeout(() => {
            if (!splineLoadedRef.current) {
                setSplineFailed(true);
            }
        }, 8000);
        return () => clearTimeout(timeout);
    }, []);

    const goToMain = () => {
        if (isTransitioning) return;
        setIsTransitioning(true);
        setTimeout(() => navigate('/guide'), 850);
    };

    const handleStart = () => {
        setHasStarted(true);
    };

    // 스페이스바, 탭키로 시작 및 다음 단계 이동
    useEffect(() => {
        const handleKeyDown = (e) => {
            if (e.code === 'Space' || e.key === ' ' || e.code === 'Tab' || e.key === 'Tab') {
                e.preventDefault();
                if (!hasStarted) {
                    handleStart();
                } else {
                    // 다음 단계로 이동 (마지막 단계면 Skip)
                    if (currentStep < STEPS.length - 1) {
                        setCurrentStep(prev => prev + 1);
                    } else {
                        navigate('/guide');
                    }
                }
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [hasStarted, navigate, currentStep]);

    // 스텝 변경 및 오디오 재생 로직
    useEffect(() => {
        if (!hasStarted || isTransitioning) return;

        // Strict Mode 중복 실행 방지
        if (timerRef.current) {
            return; // 이미 타이머가 돌고 있으면 추가 실행 안 함
        }

        const handleNext = () => {
            if (!isMountedRef.current) return; // 언마운트됐으면 무시

            if (currentStep < STEPS.length - 1) {
                setCurrentStep(prev => prev + 1);
            } else {
                goToMain();
            }
        };

        // 새 오디오 설정
        const audio = new Audio(STEPS[currentStep].audioSrc);
        audioRef.current = audio;

        const playPromise = audio.play();
        if (playPromise !== undefined) {
            playPromise.catch(error => {
                console.warn(`Audio Auto-play blocked.`);
            });
        }

        // 각 페이지의 duration만큼 유지 후 다음으로 이동
        timerRef.current = setTimeout(() => {
            timerRef.current = null;
            handleNext();
        }, STEPS[currentStep].duration);

        return () => {
            // cleanup
            isMountedRef.current = false;

            if (audioRef.current) {
                audioRef.current.pause();
                audioRef.current = null;
            }
            if (timerRef.current) {
                clearTimeout(timerRef.current);
                timerRef.current = null;
            }

            // cleanup 후 다시 mounted 상태로
            setTimeout(() => {
                isMountedRef.current = true;
            }, 0);
        };
    }, [currentStep, hasStarted, isTransitioning]);

    // 시작 화면
    if (!hasStarted) {
        return (
            <div className="intro-container" style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                cursor: 'pointer'
            }} onClick={handleStart}>
                <div style={{ textAlign: 'center', color: 'white' }}>
                    <h1 style={{
                        fontSize: '4rem',
                        fontWeight: 'bold',
                        marginBottom: '2rem',
                        animation: 'pulse 2s infinite'
                    }}>
                        HearBe 서비스 시작하기
                    </h1>
                    <p style={{ fontSize: '1.5rem', opacity: 0.9 }}>
                        스페이스바 또는 화면을 클릭하여 시작하세요
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="intro-container">
            <button className="skip-btn" onClick={() => navigate('/guide')}>Skip</button>

            <AnimatePresence>
                {isTransitioning && (
                    <motion.div className="transition-overlay" initial={{ scale: 0 }} animate={{ scale: 4 }} transition={{ duration: 0.8 }} />
                )}
            </AnimatePresence>

            <div className="text-section">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={currentStep}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.8 }}
                    >
                        <h1 className="main-copy">{STEPS[currentStep].title}</h1>
                        <p className="sub-copy">{STEPS[currentStep].desc}</p>
                    </motion.div>
                </AnimatePresence>
            </div>

            <div className="object-section">
                {splineFailed ? (
                    <div className="abstract-orb" />
                ) : (
                    <Spline
                        scene="https://prod.spline.design/IaDdv3c70ekbtAdf/scene.splinecode"
                        onError={() => setSplineFailed(true)}
                        onLoad={(splineApp) => {
                            if (splineApp) {
                                splineLoadedRef.current = true;
                            } else {
                                setSplineFailed(true);
                            }
                        }}
                    />
                )}
            </div>

            <div className="action-section">
                <div className="dot-indicator">
                    {STEPS.map((_, i) => <div key={i} className={`dot ${i === currentStep ? 'active' : ''}`} />)}
                </div>
            </div>
        </div>
    );
}