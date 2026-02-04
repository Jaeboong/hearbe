import { useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Volume2, Download, ArrowRight, Share2, Layout, Zap, Mic, Eye, ShoppingBag, Command, ChevronDown } from 'lucide-react';
import '../App.css';
import '../index.css'
import logoC from '../assets/logoC.png';

// 모드 선택 카드 컴포넌트
const ModeCard = ({ mode, onSelect }) => (
  <motion.button
    whileHover={{ y: -10 }}
    whileTap={{ scale: 0.98 }}
    onClick={() => onSelect(mode.id, mode.title)}
    className="relative overflow-hidden group rounded-[2rem] shadow-lg hover:shadow-2xl transition-all duration-300 w-full h-[500px] flex flex-col items-start justify-between p-8 text-left"
    style={{ background: mode.bgColor }}
  >
    {/* Background Icon */}
    <div className="absolute -right-12 -bottom-12 opacity-10 transition-transform duration-500 group-hover:scale-110 group-hover:rotate-12">
      {mode.iconLarge}
    </div>

    {/* Top Content */}
    <div className="relative z-10 w-full">
      <div className="w-16 h-16 rounded-2xl bg-white/20 backdrop-blur-md flex items-center justify-center mb-6 text-white shadow-inner border border-white/20">
        {mode.icon}
      </div>
      <div className="inline-block px-3 py-1 bg-white/90 rounded-full mb-6 shadow-sm">
        <span className="text-xs font-black text-gray-900 tracking-wider uppercase">{mode.label}</span>
      </div>
      <h3 className="text-4xl font-black text-white mb-4 leading-tight drop-shadow-sm">
        {mode.title}
      </h3>
      <p className="text-lg font-medium text-white/90 leading-relaxed max-w-[80%]">
        {mode.desc}
      </p>
    </div>

    {/* Bottom Content */}
    <div className="relative z-10 w-full mt-auto">
      <div className="flex flex-wrap gap-2 mb-8">
        {mode.tags.map(tag => (
          <span key={tag} className="px-3 py-1 rounded-full text-xs font-bold border border-white/30 text-white bg-white/10 backdrop-blur-sm">
            {tag}
          </span>
        ))}
      </div>
      <div className="flex items-center gap-3 group-hover:gap-5 transition-all">
        <span className="text-sm font-bold text-white uppercase tracking-widest">Start Now</span>
        <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center text-purple-600 shadow-lg">
          <ArrowRight size={20} />
        </div>
      </div>
    </div>
  </motion.button>
);

const MainLanding = ({ handleModeSelect, modeSelectionRef, onOpenSetup }) => {
  const navigate = useNavigate();

  // Auto-scroll effect after a delay
  useEffect(() => {
    const timer = setTimeout(() => {
      modeSelectionRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 5000); // 5 seconds delay
    return () => clearTimeout(timer);
  }, [modeSelectionRef]);

  return (
    // Main Container
    <div className="w-full h-screen overflow-y-scroll snap-y snap-mandatory scroll-smooth bg-white">

      {/* Header - Fixed & Transparent for unity */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-transparent h-24 flex items-center transition-all duration-300">
        <div className="max-w-7xl w-full mx-auto px-8 flex items-center justify-between">
          <img src={logoC} alt="HearBe" className="h-12 object-contain cursor-pointer drop-shadow-sm" onClick={() => window.scrollTo(0, 0)} />
          <div className="flex items-center gap-4">
            <button
              onClick={onOpenSetup}
              className="px-6 py-3 rounded-2xl font-bold text-sm text-white flex items-center gap-2 shadow-lg hover:shadow-purple-500/30 transition-all hover:-translate-y-0.5"
              style={{ background: 'linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%)' }}
            >
              <Download size={18} /> 설정 도우미
            </button>
          </div>
        </div>
      </header>

      {/* Section 1: Hero - Minimal Typography (Toss Style) with Ultra Slow 3D Glowing Flowing Wave */}
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
          onClick={() => modeSelectionRef.current?.scrollIntoView({ behavior: 'smooth' })}
        >
          <div className="w-[1px] h-12 bg-gradient-to-b from-transparent via-gray-400 to-transparent mb-2" />
          <span className="text-sm font-bold tracking-[0.2em] uppercase">Scroll Down</span>
          <ChevronDown size={24} strokeWidth={2} />
        </motion.div>
      </section>

      {/* Section 2: Mode Selection */}
      <section ref={modeSelectionRef} className="snap-start w-full min-h-screen flex flex-col justify-center items-center px-8 py-24 bg-white relative">
        <div className="max-w-[1400px] w-full mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-20"
          >
            <h2 className="text-4xl md:text-6xl font-black text-gray-900 mb-6 tracking-tight">쇼핑 모드 선택</h2>
            <p className="text-xl md:text-2xl text-gray-500 font-medium">당신에게 가장 편안한 방식을 선택하세요</p>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <ModeCard
              onSelect={handleModeSelect}
              mode={{
                id: 'audio', // 'big' maps to 'audio' logic in router anyway, or we can use 'audio' as the unified key
                label: 'TYPE A',
                title: <>보이스 & 큰글씨<br />통합 쇼핑</>,
                desc: <>저시력자와 시각장애인을 위한<br />음성 안내 및 큰 글씨 모드</>,
                tags: ['음성 안내', '큰 글씨', '통합 지원'],
                bgColor: 'linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%)',
                textColor: '#FFFFFF',
                icon: <Volume2 size={32} />,
                iconLarge: <Zap size={300} />
              }}
            />
            <ModeCard
              onSelect={handleModeSelect}
              mode={{
                id: 'common',
                label: 'TYPE C',
                title: <>표준<br />일반 쇼핑</>,
                desc: <>시각 정보를 활용한<br />우리에게 익숙한 표준 모드</>,
                tags: ['표준 UI', '시각·음성 병행'],
                bgColor: 'linear-gradient(135deg, #818CF8 0%, #6366F1 100%)',
                textColor: '#FFFFFF',
                icon: <Layout size={32} />,
                iconLarge: <Layout size={300} />
              }}
            />
            <ModeCard
              onSelect={handleModeSelect}
              mode={{
                id: 'sharing',
                label: 'TYPE S',
                title: <>원격 지원<br />공유 쇼핑</>,
                desc: <>함께 실시간 화면을<br />보며 즐기는 소통 쇼핑</>,
                tags: ['화면 공유', '라이브'],
                bgColor: 'linear-gradient(135deg, #F472B6 0%, #EC4899 100%)',
                textColor: '#FFFFFF',
                icon: <Share2 size={32} />,
                iconLarge: <Share2 size={300} />
              }}
            />
          </div>
        </div>
      </section>

      {/* Section 3: How to Use */}
      <section className="snap-start w-full min-h-screen flex flex-col justify-center items-center px-8 py-24 bg-[#F8F9FF]">
        <div className="max-w-7xl w-full mx-auto flex flex-col lg:flex-row items-center gap-20">
          <div className="flex-1 text-left">
            <h2 className="text-5xl md:text-7xl font-black text-gray-900 mb-10 leading-[1.1] tracking-tight">
              간단하지만,<br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-indigo-600">강력합니다.</span>
            </h2>
            <p className="text-2xl text-gray-500 font-medium leading-relaxed max-w-xl">
              복잡한 절차 없이 세 단계만으로.<br />
              누구나 쉽게 시작할 수 있는 쇼핑의 새로운 표준입니다.
            </p>
          </div>

          <div className="flex-1 w-full bg-white rounded-[40px] p-16 shadow-2xl shadow-purple-200/50 border border-purple-50">
            <div className="space-y-10">
              {[
                { num: 1, text: "쇼핑 모드 선택", sub: "" },
                { num: 2, text: "상품 음성 검색 및 선택", sub: "" },
                { num: 3, text: "간편하게 구매", sub: "" }
              ].map((step, i) => (
                <div key={i} className="flex items-center gap-8 group">
                  <div className="flex-shrink-0 w-20 h-20 rounded-3xl bg-purple-50 group-hover:bg-purple-600 transition-colors duration-300 flex items-center justify-center text-3xl font-black text-purple-600 group-hover:text-white">
                    {step.num}
                  </div>
                  <div>
                    <h3 className="text-3xl font-bold text-gray-900">{step.text}</h3>
                    {step.sub && <p className="text-gray-500 mt-2 text-lg">{step.sub}</p>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Section 4: Speciality */}
      <section className="snap-start w-full min-h-screen flex flex-col justify-center items-center px-8 py-24 bg-[#111] overflow-hidden relative">
        <div className="relative z-10 max-w-7xl w-full mx-auto text-white">
          <div className="text-center mb-24">
            <h2 className="text-5xl md:text-7xl font-black mb-8 tracking-tight">HearBe의 특별함</h2>
            <p className="text-2xl text-gray-400 max-w-3xl mx-auto leading-relaxed">누구에게나 평등한 쇼핑의 가치를 가장 선명하게 전달합니다.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
            <div className="bg-white/5 backdrop-blur-xl rounded-[40px] p-12 border border-white/10 hover:bg-white/10 transition-all duration-500 hover:-translate-y-2 group">
              <div className="w-20 h-20 rounded-3xl bg-purple-600 flex items-center justify-center mb-10 group-hover:scale-110 transition-transform">
                <Mic size={40} className="text-white" />
              </div>
              <h3 className="text-3xl font-bold mb-6">보이스 컨트롤</h3>
              <p className="text-gray-400 text-lg leading-relaxed mb-8">목소리 하나로 상품 검색부터 주문까지 모든 쇼핑 과정을 한 번에 완료하세요.</p>
            </div>

            <div className="bg-white/5 backdrop-blur-xl rounded-[40px] p-12 border border-white/10 hover:bg-white/10 transition-all duration-500 hover:-translate-y-2 group">
              <div className="w-20 h-20 rounded-3xl bg-white flex items-center justify-center mb-10 group-hover:scale-110 transition-transform">
                <Eye size={40} className="text-purple-600" />
              </div>
              <h3 className="text-3xl font-bold mb-6">초고대비 모드</h3>
              <p className="text-gray-400 text-lg leading-relaxed mb-8">저시력 사용자를 위해 모든 화면 요소를 크고 선명하게 최적화하여 보여줍니다.</p>
            </div>

            <div className="bg-white/5 backdrop-blur-xl rounded-[40px] p-12 border border-white/10 hover:bg-white/10 transition-all duration-500 hover:-translate-y-2 group">
              <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-purple-500 to-indigo-500 flex items-center justify-center mb-10 group-hover:scale-110 transition-transform">
                <Command size={40} className="text-white" />
              </div>
              <h3 className="text-3xl font-bold mb-6">음성 명령 브릿지</h3>
              <p className="text-gray-400 text-lg leading-relaxed mb-8">사용자의 음성 메시지를 쇼핑몰의 동작으로 즉시 변환하여 실행합니다.</p>
            </div>
          </div>

          <footer className="mt-32 pt-10 border-t border-white/10 text-center text-gray-500 font-medium">
            © 2026 HearBe. All rights reserved.
          </footer>
        </div>
      </section>
    </div>
  );
};

export default MainLanding;
