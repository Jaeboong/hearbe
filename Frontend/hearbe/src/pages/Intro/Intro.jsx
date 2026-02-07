import React, { useState, useEffect } from 'react';
import Spline from '@splinetool/react-spline';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import './Intro.css';

import introAudio1 from '../../assets/audio/intro/intro_guide_1.wav';
import introAudio2 from '../../assets/audio/intro/intro_guide_2.wav';
import introAudio3 from '../../assets/audio/intro/intro_guide_3.wav';

const STEPS = [
    {
        title: "목소리만으로 완성하는 새로운 쇼핑 경험",
        desc: "복잡한 화면 대신 당신의 목소리에 집중하는 스마트 쇼핑 파트너",
        audioSrc: introAudio1,
        duration: 4000
    },
    {
        title: "보이지 않아도, 스스로 선택하는 즐거움",
        desc: "원하는 상품을 말해보세요. 당신의 목소리로 완벽한 쇼핑을 완성합니다.",
        audioSrc: introAudio2,
        duration: 4000
    },
    {
        title: "검색부터 결제까지, 당신의 목소리와 함께",
        desc: "모든 과정을 친절한 음성으로 안내하여 스스로 완성하는 쇼핑을 지원합니다.",
        audioSrc: introAudio3,
        duration: 4000
    },
];

export default function Intro() {
    const [currentStep, setCurrentStep] = useState(0);
    const [isTransitioning, setIsTransitioning] = useState(false);
    const [hasStarted, setHasStarted] = useState(false);
    const [splineFailed, setSplineFailed] = useState(false);
    const splineLoadedRef = React.useRef(false);
    const navigate = useNavigate();

    const audioRef = React.useRef(null);
    const timerRef = React.useRef(null);
    const isMountedRef = React.useRef(true);

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
        // [프로세스 유지]: Intro -> Guide (BrandLanding) 흐름 유지
        setTimeout(() => navigate('/guide'), 850);
    };

    const handleStart = () => {
        setHasStarted(true);
    };

    useEffect(() => {
        const handleKeyDown = (e) => {
            if (e.code === 'Space' || e.key === ' ' || e.code === 'Tab' || e.key === 'Tab') {
                e.preventDefault();
                if (!hasStarted) {
                    handleStart();
                } else {
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

    useEffect(() => {
        if (!hasStarted || isTransitioning) return;

        if (timerRef.current) return;

        const handleNext = () => {
            if (!isMountedRef.current) return;
            if (currentStep < STEPS.length - 1) {
                setCurrentStep(prev => prev + 1);
            } else {
                goToMain();
            }
        };

        const audio = new Audio(STEPS[currentStep].audioSrc);
        audioRef.current = audio;

        const playPromise = audio.play();
        if (playPromise !== undefined) {
            playPromise.catch(error => {
                console.warn(`Audio Auto-play blocked.`);
            });
        }

        timerRef.current = setTimeout(() => {
            timerRef.current = null;
            handleNext();
        }, STEPS[currentStep].duration);

        return () => {
            isMountedRef.current = false;
            if (audioRef.current) {
                audioRef.current.pause();
                audioRef.current = null;
            }
            if (timerRef.current) {
                clearTimeout(timerRef.current);
                timerRef.current = null;
            }
            setTimeout(() => {
                isMountedRef.current = true;
            }, 0);
        };
    }, [currentStep, hasStarted, isTransitioning]);

    if (!hasStarted) {
        return (
            <div className="intro-container cursor-pointer" onClick={handleStart} style={{ justifyContent: 'center' }}>
                <div className="text-section" style={{ marginTop: 0 }}>
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 1 }}
                    >
                        <h1 className="main-copy">HearBe 서비스 시작하기</h1>
                        <p className="sub-copy">스페이스바 또는 화면을 클릭하여 시작하세요</p>
                    </motion.div>
                </div>
                {/* 배경에 은은한 오버레이 추가 전용 클래스 활용 가능 */}
                <div className="purple-aura" style={{ opacity: 0.2 }} />
            </div>
        );
    }

    return (
        <div className="intro-container">
            {/* [디자인 우선]: 프리미엄 Skip 버튼 스타일 유지 */}
            <button
                className="fixed top-10 right-10 z-50 cursor-pointer px-6 py-2 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-white/60 text-[14px] font-semibold hover:bg-white/20 hover:text-white transition-all duration-300 shadow-sm"
                onClick={() => navigate('/guide')}
            >
                skip
            </button>

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