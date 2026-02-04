import React, { useState, useEffect, useRef } from 'react';
import Spline from '@splinetool/react-spline';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import './Intro.css';
import introAudio1 from '../../assets/Intro/intro1.wav';
import introAudio2 from '../../assets/Intro/intro2.wav';
import introAudio3 from '../../assets/Intro/intro3.wav';
import introAudio4 from '../../assets/Intro/intro4.wav';

// Error Boundary to catch WebGL context failures
class SplineErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        console.error("Spline Error Boundary Caught:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return <div className="abstract-orb" />;
        }
        return this.props.children;
    }
}

const STEPS = [
    {
        title: "목소리만으로 완성하는 새로운 쇼핑 경험",
        desc: "복잡한 화면 대신 당신의 목소리에 귀를 기울입니다.",
        audioSrc: introAudio1
    },
    {
        title: "보이지 않아도, 스스로 선택하는 쇼핑",
        desc: "복잡한 상품 정보도 HearBe가 알기 쉽게 읽어드립니다.",
        audioSrc: introAudio2
    },
    {
        title: "검색부터 결제까지, 당신의 목소리로",
        desc: "찾고 싶은 물건을 말하면 결제까지 한 번에 도와드려요.",
        audioSrc: introAudio3
    },
    {
        title: "HearBe와 함께, 지금 바로 시작해보세요",
        desc: "누구나 즐거운 쇼핑, HearBe가 함께합니다.",
        audioSrc: introAudio4
    }
];

export default function Intro() {
    const [currentStep, setCurrentStep] = useState(0);
    const [isTransitioning, setIsTransitioning] = useState(false);
    const navigate = useNavigate();
    const audioRef = useRef(null);

    const goToMain = () => {
        if (isTransitioning) return;
        setIsTransitioning(true);

        // 오디오 정지
        if (audioRef.current) {
            audioRef.current.pause();
        }

        // 보라색 확산 애니메이션 후 /main으로 이동
        setTimeout(() => {
            navigate('/main');
        }, 850);
    };

    // Step Timer Logic
    useEffect(() => {
        if (isTransitioning) return;

        // 4초마다 다음 스텝으로 자동 이동
        const timer = setInterval(() => {
            if (currentStep < STEPS.length - 1) {
                setCurrentStep((prev) => prev + 1);
            } else {
                goToMain();
            }
        }, 4000);

        return () => clearInterval(timer);
    }, [currentStep, isTransitioning]);

    // Audio Playback Logic per Step
    useEffect(() => {
        // 이전 오디오 정지 및 초기화
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current.currentTime = 0;
        }

        // 현재 단계의 오디오 설정 및 재생
        const currentAudioSrc = STEPS[currentStep].audioSrc;
        const newAudio = new Audio(currentAudioSrc);
        audioRef.current = newAudio;

        const playPromise = newAudio.play();
        if (playPromise !== undefined) {
            playPromise.catch((error) => {
                console.log(`Step ${currentStep + 1} autoplay prevented:`, error);
                // 자동 재생 정책에 의해 막히면 인터랙션 대기
            });
        }

        return () => {
            // cleanup
            newAudio.pause();
        };
    }, [currentStep]);

    // 사용자 인터랙션 발생 시 오디오 재생 시도 (자동재생 실패 대응)
    const handleUserInteraction = () => {
        if (audioRef.current && audioRef.current.paused) {
            audioRef.current.play().catch(e => console.log("Manual play failed:", e));
        }
    };

    return (
        <div className="intro-container" onClick={handleUserInteraction}>
            {!isTransitioning && (
                <button className="skip-btn" onClick={(e) => { e.stopPropagation(); goToMain(); }}>Skip</button>
            )}

            <AnimatePresence>
                {isTransitioning && (
                    <motion.div
                        className="transition-overlay"
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 4, opacity: 1 }}
                        transition={{ duration: 0.8, ease: [0.76, 0, 0.24, 1] }}
                    />
                )}
            </AnimatePresence>

            <div className="bg-watermark">HEARBE</div>

            <div className="text-section">
                <AnimatePresence mode="wait">
                    {!isTransitioning && (
                        <motion.div
                            key={currentStep}
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 1.05 }}
                            transition={{ duration: 0.8 }}
                        >
                            <h1 className="main-copy">{STEPS[currentStep].title}</h1>
                            <p className="sub-copy">{STEPS[currentStep].desc}</p>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            <div className="object-section">
                <SplineErrorBoundary>
                    <Spline scene="https://prod.spline.design/IaDdv3c70ekbtAdf/scene.splinecode" />
                </SplineErrorBoundary>
            </div>

            <div className="action-section">
                <div className="dot-indicator">
                    {STEPS.map((_, i) => (
                        <div key={i} className={`dot ${i === currentStep ? 'active' : ''}`} />
                    ))}
                </div>
            </div>

            <div className="purple-aura" />
        </div>
    );
}