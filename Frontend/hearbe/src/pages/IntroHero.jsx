import { motion } from 'framer-motion';
import { ChevronDown } from 'lucide-react';
import React from 'react';

const IntroHero = ({ onScrollDown }) => {
    return (
        <section className="snap-start w-full min-h-screen flex flex-col justify-center items-center bg-white relative px-6 pt-32 pb-20 overflow-hidden">
            {/* Continuous Flowing Voice Wave - Ultra Slowed */}
            <div className="absolute inset-x-0 bottom-[10%] h-48 pointer-events-none opacity-90 z-0 overflow-hidden">
                {/* Gradient Definitions - Softer Contrast */}
                <svg width="0" height="0">
                    <defs>
                        <linearGradient id="flowGradient1" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stopColor="#7C3AED" stopOpacity="0.4" />
                            <stop offset="50%" stopColor="#7C3AED" stopOpacity="0.9" />
                            <stop offset="100%" stopColor="#7C3AED" stopOpacity="0.4" />
                        </linearGradient>
                        <linearGradient id="flowGradient2" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stopColor="#3B82F6" stopOpacity="0.4" />
                            <stop offset="50%" stopColor="#3B82F6" stopOpacity="0.9" />
                            <stop offset="100%" stopColor="#3B82F6" stopOpacity="0.4" />
                        </linearGradient>
                        <filter id="neonGlow" x="-20%" y="-20%" width="140%" height="140%">
                            <feGaussianBlur stdDeviation="5" result="coloredBlur" />
                            <feMerge>
                                <feMergeNode in="coloredBlur" />
                                <feMergeNode in="SourceGraphic" />
                            </feMerge>
                        </filter>
                    </defs>
                </svg>

                {/* Wave 1: Fast Flowing Purple - Ultra Slowed */}
                <motion.div
                    className="absolute top-0 left-0 h-full w-[200%] flex"
                    animate={{ x: ["0%", "-50%"] }}
                    transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
                >
                    <svg className="w-1/2 h-full" viewBox="0 0 1000 100" preserveAspectRatio="none">
                        <path d="M0,50 C200,80 300,20 500,50 C700,80 800,20 1000,50" stroke="url(#flowGradient1)" strokeWidth="4" fill="none" filter="url(#neonGlow)" />
                    </svg>
                    <svg className="w-1/2 h-full" viewBox="0 0 1000 100" preserveAspectRatio="none">
                        <path d="M0,50 C200,80 300,20 500,50 C700,80 800,20 1000,50" stroke="url(#flowGradient1)" strokeWidth="4" fill="none" filter="url(#neonGlow)" />
                    </svg>
                </motion.div>

                {/* Wave 2: Slower Blue Flow - Ultra Slowed */}
                <motion.div
                    className="absolute top-0 left-0 h-full w-[200%] flex"
                    animate={{ x: ["-50%", "0%"] }}
                    transition={{ duration: 90, repeat: Infinity, ease: "linear" }}
                    style={{ opacity: 0.7 }}
                >
                    <svg className="w-1/2 h-full" viewBox="0 0 1000 100" preserveAspectRatio="none">
                        <path d="M0,50 C150,20 350,80 500,50 C650,20 850,80 1000,50" stroke="url(#flowGradient2)" strokeWidth="4" fill="none" filter="url(#neonGlow)" />
                    </svg>
                    <svg className="w-1/2 h-full" viewBox="0 0 1000 100" preserveAspectRatio="none">
                        <path d="M0,50 C150,20 350,80 500,50 C650,20 850,80 1000,50" stroke="url(#flowGradient2)" strokeWidth="4" fill="none" filter="url(#neonGlow)" />
                    </svg>
                </motion.div>

                {/* Wave 3: Subtle Accent - Ultra Slowed */}
                <motion.div
                    className="absolute top-0 left-0 h-full w-[200%] flex"
                    animate={{ x: ["0%", "-50%"] }}
                    transition={{ duration: 120, repeat: Infinity, ease: "linear" }}
                    style={{ opacity: 0.5 }}
                >
                    <svg className="w-1/2 h-full" viewBox="0 0 1000 100" preserveAspectRatio="none">
                        <path d="M0,50 C250,30 350,70 500,50 C650,30 750,70 1000,50" stroke="#06b6d4" strokeWidth="2" fill="none" />
                    </svg>
                    <svg className="w-1/2 h-full" viewBox="0 0 1000 100" preserveAspectRatio="none">
                        <path d="M0,50 C250,30 350,70 500,50 C650,30 750,70 1000,50" stroke="#06b6d4" strokeWidth="2" fill="none" />
                    </svg>
                </motion.div>
            </div>

            {/* Main Text Content */}
            <motion.div
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 1.2, ease: "easeOut" }}
                className="text-center z-10 flex flex-col items-center relative"
            >
                <p className="text-xl md:text-3xl text-gray-500 font-bold mb-8 tracking-widest break-keep">
                    누구나 쉽고 편하게
                </p>

                <div className="flex flex-col items-center space-y-4 relative">
                    <span className="text-6xl md:text-8xl lg:text-9xl font-black text-gray-900 leading-tight tracking-tighter break-keep drop-shadow-sm">
                        들리는 쇼핑,
                    </span>
                    <span className="text-6xl md:text-8xl lg:text-9xl font-black text-gray-900 leading-tight tracking-tighter break-keep drop-shadow-sm">
                        마음을 잇다.
                    </span>
                    <span className="text-[5rem] md:text-[9rem] font-black leading-none tracking-tighter mt-8 pb-4 bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-indigo-500 drop-shadow-sm" style={{ fontFamily: 'sans-serif' }}>
                        HearBe
                    </span>
                </div>
            </motion.div>

            {/* Scroll Indicator */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1, y: [0, 10, 0] }}
                transition={{ delay: 2, duration: 2, repeat: Infinity }}
                className="absolute bottom-12 cursor-pointer flex flex-col items-center gap-3 text-gray-400 hover:text-purple-600 transition-colors z-20"
                onClick={onScrollDown}
            >
                <div className="w-[1px] h-12 bg-gradient-to-b from-transparent via-gray-400 to-transparent mb-2" />
                <span className="text-sm font-bold tracking-[0.2em] uppercase">Scroll Down</span>
                <ChevronDown size={24} strokeWidth={2} />
            </motion.div>
        </section>
    );
};

export default IntroHero;
