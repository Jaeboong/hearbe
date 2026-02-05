import { useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Volume2, Download, ArrowRight, Share2, Layout, Zap, Settings, Info, BookOpen, Eye } from 'lucide-react';
import '../App.css';
import '../index.css'
import logoC from '../assets/logoC.png';

// 모드 선택 카드 컴포넌트
const ModeCard = ({ mode, onSelect }) => (
  <motion.button
    whileHover={{ y: -10 }}
    whileTap={{ scale: 0.98 }}
    onClick={() => onSelect(mode.id, mode.title)}
    className="cursor-pointer relative overflow-hidden group rounded-[2rem] shadow-lg hover:shadow-2xl transition-all duration-300 w-full min-w-[280px] h-[480px] flex flex-col items-start justify-between p-8 text-left bg-white border border-gray-100"
    style={{ background: mode.bgColor }}
  >
    {/* Background Icon */}
    <div className="absolute -right-12 -bottom-12 opacity-10 transition-transform duration-500 group-hover:scale-110 group-hover:rotate-12">
      {mode.iconLarge}
    </div>

    {/* Top Content */}
    <div className="relative z-10 w-full">
      <div className="w-16 h-16 rounded-2xl bg-white/20 backdrop-blur-md flex items-center justify-center mb-8 text-white shadow-inner border border-white/20">
        {mode.icon}
      </div>
      <div className="inline-block px-4 py-1.5 rounded-full mb-8 shadow-sm" style={{ backgroundColor: mode.badgeBg || 'rgba(255,255,255,0.9)' }}>
        <span className="text-xs font-black tracking-wider uppercase" style={{ color: mode.labelColor || '#111827' }}>
          {mode.label}
        </span>
      </div>
      <h3 className="text-4xl font-black mb-6 leading-tight drop-shadow-sm" style={{ color: mode.textColor || '#FFFFFF' }}>
        {mode.title}
      </h3>
      <p className="text-xl font-medium leading-relaxed max-w-[90%]" style={{ color: mode.textColor ? mode.textColor + 'E6' : 'rgba(255,255,255,0.9)' }}>
        {mode.desc}
      </p>
    </div>

    {/* Bottom Content */}
    <div className="relative z-10 w-full mt-auto">
      <div className="flex flex-wrap gap-2 mb-8 opacity-80">
        {mode.tags.map(tag => (
          <span
            key={tag}
            className="px-3 py-1 rounded-full text-xs font-bold border border-white/30 backdrop-blur-sm"
            style={{
              color: mode.textColor || '#FFFFFF',
              borderColor: mode.textColor ? mode.textColor + '4D' : 'rgba(255,255,255,0.3)',
              backgroundColor: 'rgba(255,255,255,0.1)'
            }}
          >
            {tag}
          </span>
        ))}
      </div>
      <div className="flex items-center gap-4 group-hover:gap-6 transition-all">
        <span className="text-sm font-bold uppercase tracking-widest" style={{ color: mode.textColor || '#FFFFFF' }}>
          Start Shopping
        </span>
        <div
          className="w-12 h-12 rounded-full flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform"
          style={{ backgroundColor: mode.btnBg || 'white', color: mode.arrowColor || '#7C3AED' }}
        >
          <ArrowRight size={24} />
        </div>
      </div>
    </div>
  </motion.button>
);


const MainLanding = ({ handleModeSelect, modeSelectionRef, onOpenSetup }) => {
  const navigate = useNavigate();

  return (
    // Main Container
    <div className="w-full min-h-screen overflow-y-auto overflow-x-hidden bg-white flex flex-col items-center justify-start relative">
      <div className="fixed inset-0 bg-gradient-to-br from-purple-50 via-white to-blue-50 opacity-50 z-0 pointer-events-none" />

      {/* Header - Fixed & Transparent for unity */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-sm md:bg-transparent md:backdrop-blur-none h-20 md:h-32 flex items-center transition-all duration-300">
        <div className="max-w-7xl w-full mx-auto px-4 md:px-8 flex items-center justify-between">
          <img src={logoC} alt="HearBe" className="h-10 md:h-24 object-contain cursor-pointer drop-shadow-sm" onClick={() => window.location.href = '/main'} />
          <div className="flex items-center gap-2 md:gap-6">
            {/* 서비스 소개 버튼 */}
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/intro')}
              className="p-2 md:p-3 rounded-full hover:bg-gray-100 transition-colors flex items-center justify-center relative group"
              title="서비스 소개"
            >
              <Info className="w-5 h-5 md:w-6 md:h-6 text-gray-700" />
              {/* 말풍선 */}
              <div className="absolute top-full mt-2 px-3 py-1.5 bg-gray-800 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50">
                서비스 소개
              </div>
            </motion.button>

            {/* 가이드 버튼 */}
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/guide')}
              className="p-2 md:p-3 rounded-full hover:bg-gray-100 transition-colors flex items-center justify-center relative group"
              title="가이드"
            >
              <BookOpen className="w-5 h-5 md:w-6 md:h-6 text-gray-700" />
              {/* 말풍선 */}
              <div className="absolute top-full mt-2 px-3 py-1.5 bg-gray-800 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50">
                가이드
              </div>
            </motion.button>

            {/* 음성 프로그램 다운로드 */}
            <motion.a
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              href="/downloads/MCPDesktop.zip"
              download
              className="p-2 md:p-3 rounded-full hover:bg-gray-100 transition-colors flex items-center justify-center relative group"
              title="음성 프로그램 다운로드"
            >
              <Download className="w-5 h-5 md:w-6 md:h-6 text-gray-700" />
              {/* 말풍선 */}
              <div className="absolute top-full mt-2 px-3 py-1.5 bg-gray-800 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50">
                음성 프로그램 다운로드
              </div>
            </motion.a>
          </div>
        </div>
      </header>

      {/* Shopping Mode Selection */}
      <div className="relative z-10 w-full max-w-6xl px-4 md:px-8 py-8 md:py-12 mt-20 md:mt-32 mb-10">
        <div className="relative flex flex-col md:flex-row items-center justify-center mb-8 md:mb-16">
          <div className="text-center md:absolute md:left-1/2 md:-translate-x-1/2 z-0">
            <h2 className="text-3xl md:text-5xl lg:text-7xl font-black text-gray-900 mb-4 md:mb-6 tracking-tight">쇼핑 모드 선택</h2>
            <p className="text-lg md:text-2xl text-gray-500 font-medium">당신에게 가장 편안한 방식을 선택하세요</p>
          </div>

          {/* Spacer for mobile layout harmony if needed, or just rely on flex-col */}
          <div className="hidden md:block w-full h-24 pointer-events-none"></div>

          {/* Type S Button (Moved from Card) */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => handleModeSelect('sharing', '함께 쇼핑')}
            className="md:absolute md:right-0 z-10 flex items-center gap-3 px-6 py-4 bg-white border-2 border-pink-100 rounded-[2rem] shadow-lg hover:shadow-xl hover:border-pink-300 transition-all group mt-6 md:mt-0"
          >
            <div className="w-10 h-10 rounded-full bg-pink-100 flex items-center justify-center text-pink-600 group-hover:bg-pink-200 transition-colors">
              <Share2 size={20} />
            </div>
            <div className="text-left">
              <span className="block text-xs font-bold text-pink-500 uppercase tracking-wider">TYPE S</span>
              <span className="block text-lg font-bold text-gray-900">공유 쇼핑</span>
            </div>
            <ArrowRight size={20} className="text-gray-300 group-hover:text-pink-500 transition-colors ml-2" />
          </motion.button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-10">
          {/* Type A */}
          <ModeCard
            onSelect={handleModeSelect}
            mode={{
              id: 'audio',
              label: 'TYPE A',
              title: '음성·큰글씨 쇼핑',
              desc: '듣고 말하는 가장 쉬운 쇼핑',
              tags: ['#음성안내', '#큰글자'],
              bgColor: 'linear-gradient(135deg, #6D28D9 0%, #4C1D95 100%)', // Deep Violet
              textColor: '#FFFFFF',
              icon: <Volume2 size={32} />,
              iconLarge: <Zap size={240} />
            }}
          />

          {/* Type B (New) */}
          <ModeCard
            onSelect={handleModeSelect}
            mode={{
              id: 'big',
              label: 'TYPE B',
              title: '고대비 쇼핑',
              desc: '고대비 모드로 쇼핑',
              tags: ['#고대비', '#저시력'],
              bgColor: '#171C28',
              textColor: '#FFF064',
              labelColor: '#171C28',
              badgeBg: '#FFF064',
              btnBg: '#FFF064',
              arrowColor: '#171C28',
              icon: <Eye size={32} color="#FFF064" />,
              iconLarge: <Eye size={240} color="#FFF064" opacity={0.1} />

            }}
          />

          {/* Type C (Moved to 3rd position) */}
          <ModeCard
            onSelect={handleModeSelect}
            mode={{
              id: 'common',
              label: 'TYPE C',
              title: '일반 쇼핑',
              desc: '우리에게 익숙한 표준 화면',
              tags: ['#표준화면', '#빠른탐색'],
              bgColor: 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)', // Royal Blue
              textColor: '#FFFFFF',
              icon: <Layout size={32} />,
              iconLarge: <Layout size={240} />
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default MainLanding;
