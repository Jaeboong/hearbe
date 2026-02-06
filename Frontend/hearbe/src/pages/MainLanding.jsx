import { useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Volume2, Download, ArrowRight, Share2, Layout, Zap } from 'lucide-react';
import '../App.css';
import '../index.css'
import logoC from '../assets/logoC.png';

// 모드 선택 카드 컴포넌트
const ModeCard = ({ mode, onSelect }) => (
  <motion.button
    whileHover={{ y: -10 }}
    whileTap={{ scale: 0.98 }}
    onClick={() => onSelect(mode.id, mode.title)}
    className="relative overflow-hidden group rounded-[2rem] shadow-lg hover:shadow-2xl transition-all duration-300 w-full min-w-[300px] h-[550px] flex flex-col items-start justify-between p-10 text-left bg-white border border-gray-100"
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
      <div className="inline-block px-4 py-1.5 bg-white/90 rounded-full mb-8 shadow-sm">
        <span className="text-xs font-black text-gray-900 tracking-wider uppercase">{mode.label}</span>
      </div>
      <h3 className="text-4xl font-black text-white mb-6 leading-tight drop-shadow-sm">
        {mode.title}
      </h3>
      <p className="text-xl font-medium text-white/90 leading-relaxed max-w-[90%]">
        {mode.desc}
      </p>
    </div>

    {/* Bottom Content */}
    <div className="relative z-10 w-full mt-auto">
      <div className="flex flex-wrap gap-2 mb-8 opacity-80">
        {mode.tags.map(tag => (
          <span key={tag} className="px-3 py-1 rounded-full text-xs font-bold border border-white/30 text-white bg-white/10 backdrop-blur-sm">
            {tag}
          </span>
        ))}
      </div>
      <div className="flex items-center gap-4 group-hover:gap-6 transition-all">
        <span className="text-sm font-bold text-white uppercase tracking-widest">Start Shopping</span>
        <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center text-purple-600 shadow-lg group-hover:scale-110 transition-transform">
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
    <div className="w-full h-screen overflow-hidden bg-white flex flex-col items-center justify-center relative">
      <div className="absolute inset-0 bg-gradient-to-br from-purple-50 via-white to-blue-50 opacity-50 z-0" />

      {/* Header - Fixed & Transparent for unity */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-transparent h-32 flex items-center transition-all duration-300">
        <div className="max-w-7xl w-full mx-auto px-8 flex items-center justify-between">
          <img src={logoC} alt="HearBe" className="h-24 object-contain cursor-pointer drop-shadow-sm" onClick={() => navigate('/welcome')} />
          <div className="flex items-center gap-4">
            <a
              href="/downloads/MCPDesktop.zip"
              download
              className="px-10 py-5 rounded-full font-extrabold text-2xl text-white flex items-center gap-3 shadow-lg hover:shadow-purple-500/30 transition-all hover:-translate-y-1 no-underline"
              style={{ background: 'linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%)' }}
            >
              <Download size={24} /> 설정 도우미
            </a>
          </div>
        </div>
      </header>

      {/* Shopping Mode Selection Only */}
      <div className="relative z-10 w-full max-w-[1600px] px-8 py-12">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl md:text-7xl font-black text-gray-900 mb-6 tracking-tight">쇼핑 모드 선택</h2>
          <p className="text-2xl text-gray-500 font-medium">당신에게 가장 편안한 방식을 선택하세요</p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
          <ModeCard
            onSelect={handleModeSelect}
            mode={{
              id: 'audio',
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
    </div>
  );
};

export default MainLanding;
