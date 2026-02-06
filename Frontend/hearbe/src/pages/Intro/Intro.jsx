import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import Spline from '@splinetool/react-spline';
import './Intro.css';

// 오디오 파일 경로
import guideAudio1 from '../../assets/audio/guide/intro_guide_1.mp3';
import guideAudio2 from '../../assets/audio/guide/intro_guide_2.mp3';
import guideAudio3 from '../../assets/audio/guide/intro_guide_3.mp3';

const STEPS = [
    {
        title: "소리로 쇼핑하는 세상",
        desc: "HearBe와 함께라면 쇼핑이 즐거워집니다.",
        audio: guideAudio1,
        duration: 4000
    },
    {
        title: "당신의 목소리로",
        desc: "찾고 싶은 상품을 말해보세요.",
        audio: guideAudio2,
        duration: 4000
    },
    {
        title: "가장 쉬운 시작",
        desc: "지금 바로 HearBe를 경험해보세요.",
        audio: guideAudio3,
        duration: 4000
    }
];

const Intro = () => {
    const [currentStep, setCurrentStep] = useState(0);
    const [isTransitioning, setIsTransitioning] = useState(false);
    const [hasStarted, setHasStarted] = useState(false);
    const [splineFailed, setSplineFailed] = useState(false);
    const splineLoadedRef = useRef(false);
    const navigate = useNavigate();

    // 오디오와 타이머 객체 관리
    const audioRef = useRef(null);
    const timerRef = useRef(null);
    const isMountedRef = useRef(true);

    // Spline 로딩 타임아웃
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
        setTimeout(() => {
            navigate('/main');
        }, 8000);
    };

    const handleNext = () => {
        if (currentStep < STEPS.length - 1) {
            setCurrentStep(prev => prev + 1);
        } else {
            goToMain();
        }
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
                    handleNext();
                }
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [hasStarted, currentStep]);

    // 스텝 변경 및 오디오 재생 로직
    useEffect(() => {
        if (!hasStarted || isTransitioning) return;

        // 이전 오디오 중지 및 새로 재생
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current = null;
        }

        const audio = new Audio(STEPS[currentStep].audio);
        audioRef.current = audio;
        audio.play().catch(e => console.log("Audio play deferred:", e));

        // 타이머 설정
        if (timerRef.current) clearTimeout(timerRef.current);

        timerRef.current = setTimeout(() => {
            if (isMountedRef.current) {
                handleNext();
            }
        }, STEPS[currentStep].duration);

        return () => {
            if (audioRef.current) {
                audioRef.current.pause();
                audioRef.current = null;
            }
            if (timerRef.current) {
                clearTimeout(timerRef.current);
                timerRef.current = null;
            }
        };
    }, [currentStep, hasStarted, isTransitioning]);

    // 시작 화면
    if (!hasStarted) {
        return (
            <div className="intro-container start-screen" onClick={handleStart}>
                <div className="start-content">
                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="start-title"
                    >
                        HearBe 서비스 시작하기
                    </motion.h1>
                    <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 0.7 }}
                        transition={{ delay: 0.5 }}
                        className="start-hint"
                    >
                        스페이스바 또는 화면을 클릭하여 시작하세요
                    </motion.p>
                </div>
            </div>
        );
    }

    return (
        <div className="intro-container">
            <button
                className="skip-btn"
                onClick={() => navigate('/guide')}
            >
                skip
            </button>

            <AnimatePresence>
                {isTransitioning && (
                    <motion.div
                        className="transition-overlay"
                        initial={{ scale: 0 }}
                        animate={{ scale: 4 }}
                        transition={{ duration: 0.8 }}
                    />
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
                        onLoad={() => {
                            splineLoadedRef.current = true;
                        }}
                        onError={() => setSplineFailed(true)}
                    />
                )}
            </div>

            <div className="action-section">
                <div className="dot-indicator">
                    {STEPS.map((_, i) => (
                        <div key={i} className={`dot ${i === currentStep ? 'active' : ''}`} />
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Intro;