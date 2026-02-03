import React, { useState, useEffect } from 'react';
import Spline from '@splinetool/react-spline';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import './Intro.css';
import introAudio from '../../assets/Intro/intro1.wav';

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
    },
    {
        title: "눈이 아닌 귀로 만나는 상품 정보",
        desc: "이미지 속 작은 글자까지 HearBe가 다정하게 읽어드려요.",
    },
    {
        title: "장벽 없는 쇼핑, HearBe와 함께",
        desc: "쇼핑의 즐거움에서 누구도 소외되지 않도록.",
    }
];

export default function Intro() {
    const [currentStep, setCurrentStep] = useState(0);
    const [isTransitioning, setIsTransitioning] = useState(false);
    const navigate = useNavigate();

    const goToMain = () => {
        if (isTransitioning) return;
        setIsTransitioning(true);

        // 보라색 확산 애니메이션 후 /main으로 이동
        setTimeout(() => {
            navigate('/main');
        }, 850);
    };

    useEffect(() => {
        if (isTransitioning) return;

        const timer = setInterval(() => {
            if (currentStep < STEPS.length - 1) {
                setCurrentStep((prev) => prev + 1);
            } else {
                goToMain();
            }
        }, 4000);

        return () => clearInterval(timer);
    }, [currentStep, isTransitioning]);

    // Intro Voice Logic
    useEffect(() => {
        const audio = new Audio(introAudio);

        // Try to play immediately
        const playPromise = audio.play();

        if (playPromise !== undefined) {
            playPromise.catch((error) => {
                console.log("Autoplay prevented. Audio will play on first click.", error);

                // Fallback: Play on first user interaction (click)
                const playOnInteraction = () => {
                    audio.play();
                    document.removeEventListener('click', playOnInteraction);
                };
                document.addEventListener('click', playOnInteraction);
            });
        }

        // Stop after 4 seconds (Sync with slide transition)
        const stopTimer = setTimeout(() => {
            audio.pause();
            audio.currentTime = 0;
        }, 4000);

        return () => {
            clearTimeout(stopTimer);
            audio.pause();
        };
    }, []);



    return (
        <div className="intro-container">
            {!isTransitioning && (
                <button className="skip-btn" onClick={goToMain}>Skip</button>
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