import { useRef, useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Mic, Eye, Command, ArrowRight, ChevronRight, ChevronDown, Download } from 'lucide-react';
import '../App.css';
import '../index.css'
import logoC from '../assets/logoC.png';
import guideAudio1 from '../assets/Guide/guide1.wav';
import guideAudio2 from '../assets/Guide/guide2.wav';
import guideAudio3 from '../assets/Guide/guide3.wav';


const WaveBackground = () => (
    <div className="absolute inset-x-0 bottom-0 h-[30vh] pointer-events-none opacity-50 z-0 overflow-hidden">
        <svg width="0" height="0">
            <defs>
                <linearGradient id="flowGradient1" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#A78BFA" stopOpacity="0.4" />
                    <stop offset="50%" stopColor="#8B5CF6" stopOpacity="0.8" />
                    <stop offset="100%" stopColor="#A78BFA" stopOpacity="0.4" />
                </linearGradient>
                <linearGradient id="flowGradient2" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#818CF8" stopOpacity="0.4" />
                    <stop offset="50%" stopColor="#6366F1" stopOpacity="0.8" />
                    <stop offset="100%" stopColor="#818CF8" stopOpacity="0.4" />
                </linearGradient>
            </defs>
        </svg>

        {/* Wave 1 */}
        <motion.div
            className="absolute bottom-0 left-0 h-full w-[200%] flex"
            animate={{ x: ["0%", "-50%"] }}
            transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
        >
            <svg className="w-1/2 h-full" viewBox="0 0 1000 100" preserveAspectRatio="none">
                <path d="M0,50 C200,40 300,80 500,50 C700,20 800,60 1000,50" stroke="url(#flowGradient1)" strokeWidth="1.5" fill="none" />
            </svg>
            <svg className="w-1/2 h-full" viewBox="0 0 1000 100" preserveAspectRatio="none">
                <path d="M0,50 C200,40 300,80 500,50 C700,20 800,60 1000,50" stroke="url(#flowGradient1)" strokeWidth="1.5" fill="none" />
            </svg>
        </motion.div>

        {/* Wave 2 */}
        <motion.div
            className="absolute bottom-0 left-0 h-full w-[200%] flex"
            animate={{ x: ["-50%", "0%"] }}
            transition={{ duration: 55, repeat: Infinity, ease: "linear" }}
            style={{ opacity: 0.6 }}
        >
            <svg className="w-1/2 h-full" viewBox="0 0 1000 100" preserveAspectRatio="none">
                <path d="M0,50 C150,70 350,30 500,50 C650,70 850,30 1000,50" stroke="url(#flowGradient2)" strokeWidth="1.5" fill="none" />
            </svg>
            <svg className="w-1/2 h-full" viewBox="0 0 1000 100" preserveAspectRatio="none">
                <path d="M0,50 C150,70 350,30 500,50 C650,70 850,30 1000,50" stroke="url(#flowGradient2)" strokeWidth="1.5" fill="none" />
            </svg>
        </motion.div>
    </div>
);

const BrandLanding = () => {
    const navigate = useNavigate();
    const [currentStep, setCurrentStep] = useState(0);
    const SECTION_DURATION = 6000;

    const [hasStarted, setHasStarted] = useState(false);

    // Strict Mode 방지용
    const timerRef = useRef(null);
    const audioRef = useRef(null);
    const isMountedRef = useRef(true);

    const goToMain = () => {
        navigate('/main');
    };

    const handleStart = () => {
        setHasStarted(true);
    };

    const totalSteps = 3;

    const GUIDE_STEPS = [
        {
            id: 'speciality',
            audioSrc: guideAudio2,
            duration: 8000,
            content: (
                <section className="min-w-screen h-full flex flex-col justify-center items-center relative px-8 shrink-0">
                    <div className="max-w-7xl w-full z-10">
                        <div className="text-center mb-16">
                            <h2 className="text-5xl font-black mb-6 text-gray-900">HearBe의 특별함</h2>
                            <p className="text-xl text-gray-500">평등한 쇼핑 가치를 전달하는 핵심 기술</p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                            <div className="bg-white rounded-[2rem] p-10 shadow-xl border border-purple-50 hover:-translate-y-2 transition-transform duration-300">
                                <div className="w-16 h-16 rounded-2xl bg-purple-100 text-purple-600 flex items-center justify-center mb-6">
                                    <Mic size={32} />
                                </div>
                                <h3 className="text-2xl font-bold mb-4 text-gray-900">보이스 컨트롤</h3>
                                <p className="text-gray-500 leading-relaxed">
                                    검색부터 결제까지,<br />손 하나 까딱하지 않고<br />오직 목소리만으로.
                                </p>
                            </div>
                            <div className="bg-white rounded-[2rem] p-10 shadow-xl border border-purple-50 hover:-translate-y-2 transition-transform duration-300">
                                <div className="w-16 h-16 rounded-2xl bg-indigo-100 text-indigo-600 flex items-center justify-center mb-6">
                                    <Eye size={32} />
                                </div>
                                <h3 className="text-2xl font-bold mb-4 text-gray-900">초고대비 모드</h3>
                                <p className="text-gray-500 leading-relaxed">
                                    저시력 사용자를 위한<br />최적의 명암비와<br />글자 크기를 제공합니다.
                                </p>
                            </div>
                            <div className="bg-white rounded-[2rem] p-10 shadow-xl border border-purple-50 hover:-translate-y-2 transition-transform duration-300">
                                <div className="w-16 h-16 rounded-2xl bg-pink-100 text-pink-600 flex items-center justify-center mb-6">
                                    <Command size={32} />
                                </div>
                                <h3 className="text-2xl font-bold mb-4 text-gray-900">음성 명령 브릿지</h3>
                                <p className="text-gray-500 leading-relaxed">
                                    사용자의 의도를 파악해<br />스스로 화면을 제어하는<br />지능형 인터페이스.
                                </p>
                            </div>
                        </div>
                    </div>
                </section>
            )
        },
        {
            id: 'how-to',
            audioSrc: guideAudio1,
            duration: 14000,
            content: (
                <section className="min-w-screen h-full flex flex-col justify-center items-center relative px-8 z-10 shrink-0">
                    <div className="max-w-7xl w-full grid grid-cols-1 lg:grid-cols-2 gap-16 items-center z-10">
                        <div className="text-left">
                            <motion.div
                                initial={{ opacity: 0, y: 30 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.8 }}
                            >
                                <span className="text-purple-600 font-bold tracking-widest uppercase mb-4 block">User Guide</span>
                                <h2 className="text-5xl md:text-7xl font-black text-gray-900 mb-8 leading-[1.1] tracking-tight">
                                    간단하게,<br />
                                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-indigo-600">시작하세요.</span>
                                </h2>
                                <p className="text-2xl text-gray-600 font-medium leading-relaxed max-w-md">
                                    복잡한 절차 없이 세 단계만으로.<br />
                                    누구나 쉽게 쇼핑할 수 있습니다.
                                </p>
                            </motion.div>
                        </div>
                        <div className="space-y-6">
                            {[
                                { num: "01", text: "쇼핑 모드 선택", desc: "사용자에게 맞는 최적의 UI를 선택하세요." },
                                { num: "02", text: "음성 대화", desc: "목소리로 상품을 찾고 설명을 들어보세요." },
                                { num: "03", text: "간편 구매", desc: "결제까지 대화하듯 자연스럽게 완료됩니다." }
                            ].map((step, i) => (
                                <div
                                    key={i}
                                    className="flex items-center gap-6 p-6 rounded-3xl bg-white/80 backdrop-blur-sm shadow-xl shadow-purple-100/50 border border-white/50"
                                >
                                    <span className="text-4xl font-black text-purple-300">{step.num}</span>
                                    <div>
                                        <h3 className="text-2xl font-bold text-gray-900">{step.text}</h3>
                                        <p className="text-gray-500">{step.desc}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>
            )
        },
        {
            id: 'cta',
            audioSrc: guideAudio3,
            duration: 4000,
            content: (
                <section className="min-w-[100vw] h-full flex flex-col justify-center items-center relative px-6 z-10 bg-gradient-to-br from-gray-900 to-black text-white shrink-0">
                    <div className="text-center">
                        <h2 className="text-6xl md:text-8xl font-black mb-12 tracking-tight">
                            Ready to<br />
                            <span className="text-purple-400">HearBe?</span>
                        </h2>
                        <button
                            onClick={goToMain}
                            className="group relative px-12 py-6 rounded-full bg-white text-black font-black text-xl overflow-hidden transition-transform hover:scale-105"
                        >
                            <span className="relative z-10 group-hover:text-purple-600 transition-colors flex items-center gap-3">
                                쇼핑 시작하기 <ArrowRight size={24} />
                            </span>
                        </button>
                        <p className="mt-12 text-gray-500 text-sm">© 2026 HearBe Corp. All rights reserved.</p>
                    </div>
                </section>
            )
        }
    ];

    // Spacebar로 Click to Start (첫 화면)
    useEffect(() => {
        if (hasStarted) return;

        const handleKeyDown = (e) => {
            if (e.code === 'Space' || e.key === ' ') {
                e.preventDefault();
                handleStart();
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [hasStarted]);

    // Audio와 화면 전환 동기화 로직
    useEffect(() => {
        if (!hasStarted) return;

        // Strict Mode 중복 실행 방지
        if (timerRef.current) {
            return;
        }

        const stepData = GUIDE_STEPS[currentStep];

        const handleMove = () => {
            if (!isMountedRef.current) return;

            if (currentStep < totalSteps - 1) {
                setCurrentStep(prev => prev + 1);
            } else {
                navigate('/main');
            }
        };

        // 타이머 설정 (각 단계별 duration 적용)
        timerRef.current = setTimeout(() => {
            timerRef.current = null;
            handleMove();
        }, stepData.duration);

        // 오디오 재생
        if (stepData.audioSrc) {
            const audio = new Audio(stepData.audioSrc);
            audioRef.current = audio;
            audio.play().catch(e => {
                console.warn("Auto-play blocked:", e);
            });
        }

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
    }, [currentStep, navigate, hasStarted]);

    // Spacebar로 쇼핑 시작하기 (마지막 단계에서만)
    useEffect(() => {
        const handleKeyDown = (e) => {
            if (currentStep === totalSteps - 1 && (e.code === 'Space' || e.key === ' ')) {
                e.preventDefault();
                goToMain();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [currentStep]);

    const handleNext = () => {
        if (currentStep < totalSteps - 1) setCurrentStep(prev => prev + 1);
    };

    const handlePrev = () => {
        if (currentStep > 0) setCurrentStep(prev => prev - 1);
    };


    if (!hasStarted) {
        return (
            <div className="fixed inset-0 z-[100] bg-black flex flex-col items-center justify-center cursor-pointer" onClick={handleStart}>
                <h1 className="text-white text-6xl font-black mb-8 animate-pulse">Click to Start</h1>
                <p className="text-gray-400 text-xl">화면을 클릭하여 가이드를 시작하세요</p>
                <div className="mt-12 w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    return (
        <div className="relative w-full h-screen overflow-hidden bg-white selection:bg-purple-200">
            <WaveBackground />

            {/* Header */}
            <header className="fixed top-0 left-0 right-0 z-50 bg-transparent h-32 flex items-center">
                <div className="max-w-7xl w-full mx-auto px-8 flex items-center justify-between">
                    <img src={logoC} alt="HearBe" className="h-24 object-contain cursor-pointer drop-shadow-sm opacity-90 hover:opacity-100 transition-opacity" onClick={() => window.scrollTo(0, 0)} />
                    <button
                        onClick={goToMain}
                        className="px-10 py-4 rounded-full font-bold text-xl text-white flex items-center gap-3 bg-gradient-to-r from-purple-600 via-indigo-600 to-purple-600 bg-[length:200%_auto] hover:bg-right transition-all duration-500 shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50 hover:-translate-y-1"
                    >
                        Skip Guide <ArrowRight size={24} />
                    </button>
                </div>
            </header>

            {/* Slider Container */}
            <div
                className="flex w-full h-full transition-transform duration-1000 ease-in-out will-change-transform"
                style={{ transform: `translateX(-${currentStep * 100}vw)` }}
            >
                {GUIDE_STEPS.map((step, index) => (
                    <div key={step.id}>
                        {step.content}
                    </div>
                ))}
            </div>

            {/* Bottom Controls */}
            <div className="fixed bottom-12 left-1/2 transform -translate-x-1/2 flex items-center gap-6 z-50">
                <button
                    onClick={handlePrev}
                    disabled={currentStep === 0}
                    className={`p-3 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-gray-600 transition-all ${currentStep === 0 ? 'opacity-30 cursor-not-allowed' : 'hover:bg-white hover:text-purple-600 hover:scale-110 shadow-lg'}`}
                >
                    <ChevronDown className="rotate-90" size={20} />
                </button>

                <div className="flex gap-3">
                    {Array.from({ length: totalSteps }).map((_, i) => (
                        <button
                            key={i}
                            onClick={() => setCurrentStep(i)}
                            className={`h-2 rounded-full transition-all duration-500 cursor-pointer ${i === currentStep ? 'w-12 bg-purple-600' : 'w-2 bg-gray-300 hover:bg-purple-300'}`}
                        />
                    ))}
                </div>

                <button
                    onClick={handleNext}
                    disabled={currentStep === totalSteps - 1}
                    className={`p-3 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-gray-600 transition-all ${currentStep === totalSteps - 1 ? 'opacity-30 cursor-not-allowed' : 'hover:bg-white hover:text-purple-600 hover:scale-110 shadow-lg'}`}
                >
                    <ChevronRight size={20} />
                </button>
            </div>
        </div>
    );
};

export default BrandLanding;
