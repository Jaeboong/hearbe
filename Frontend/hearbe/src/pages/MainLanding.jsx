import { motion } from 'framer-motion';
import { Volume2, Download, ArrowRight, Share2, Layout, Zap, Mic, Eye, ShoppingBag, Command } from 'lucide-react';
import '../App.css';
import '../index.css'
import logoC from '../assets/logoC.png'; // C형 로고로 변경

// 모드 선택 카드 컴포넌트
const ModeCard = ({ mode, onSelect }) => (
  <motion.button
    whileHover={{ y: -15, scale: 1.02 }}
    whileTap={{ scale: 0.98 }}
    onClick={() => onSelect(mode.id, mode.title)}
    className="mode-card"
    style={{ background: mode.bgColor }}
  >
    <div className="mode-card-watermark">{mode.iconLarge}</div>
    <div className="mode-card-content" style={{ color: mode.textColor }}>
      <div className="mode-card-top">
        <div className="mode-icon-box">{mode.icon}</div>
        <div className="mode-label-tag">
          <span>{mode.label}</span>
        </div>
        <h3 className="mode-title">{mode.title}</h3>
        <p className="mode-desc">{mode.desc}</p>
      </div>
      <div className="mode-card-bottom">
        <div className="mode-tags">
          {mode.tags.map(tag => (
            <span key={tag} className="mode-tag" style={{ backgroundColor: mode.tagBg }}>{tag}</span>
          ))}
        </div>
        <div className="mode-start-action">
          <span className="start-now-text">Start Now</span>
          <div className="arrow-circle" style={{ color: mode.textColor }}>
            <ArrowRight size={24} />
          </div>
        </div>
      </div>
    </div>
  </motion.button>
);

/**
 * MainLanding - 메인 랜딩 페이지 컴포넌트
 *
 * @param {Object} props
 * @param {Function} props.handleModeSelect - 모드 선택 핸들러
 * @param {React.RefObject} props.modeSelectionRef - 모드 선택 영역 ref
 */
const MainLanding = ({ handleModeSelect, modeSelectionRef }) => (
  <div className="landing-container">
    <header className="landing-header">
      <div className="header-inner">
        <img
          src={logoC}
          alt="HearBe"
          className="main-logo"
          onClick={() => window.location.assign('/')}
          style={{ cursor: 'pointer' }}
        />
        <div className="header-actions">
          <button className="btn-download" style={{ background: 'linear-gradient(135deg, #A78BFA 0%, #7C3AED 100%)', color: '#fff', border: 'none' }}>
            <Download size={16} /> 보조 프로그램 다운로드
          </button>
        </div>
      </div>
    </header>

    <main className="landing-main">
      <section className="hero-section">
        <div className="hero-bg-gradients" />
        <div className="hero-content">
          <div className="badge-ai">
            <span className="ping-dot"><span className="ping" /><span className="dot" /></span>
            AI-Powered Voice Commerce
          </div>
          <h1 className="hero-title">
            당신의 감각을 깨우는<br />
            <span className="gradient-text">새로운 쇼핑의 시작</span>
          </h1>
          <p className="hero-subtitle">
            시각장애인을 위한 혁신적인 음성 가이드부터 대화면 쇼핑까지,<br />
            HearBe는 모두에게 평등하고 즐거운 쇼핑 경험을 선사합니다.
          </p>
          <button
            onClick={() => modeSelectionRef.current?.scrollIntoView({ behavior: 'smooth' })}
            className="btn-primary-large"
          >
            지금 시작하기
          </button>
        </div>

        {/* Floating Sound Wave Animation */}
        <div className="absolute right-20 bottom-0 top-0 flex items-center justify-center pointer-events-none pr-12">
          <div className="flex items-center gap-2 h-48 group-hover:gap-3 transition-all duration-500">
            {[...Array(16)].map((_, i) => (
              <motion.div
                key={i}
                className="w-2.5 rounded-full bg-gradient-to-t from-[#7C3AED] via-[#A78BFA] to-white/40"
                animate={{
                  height: [
                    20 + Math.random() * 40,
                    100 + Math.random() * 120,
                    20 + Math.random() * 40
                  ]
                }}
                transition={{
                  duration: 0.6 + Math.random() * 0.8,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: i * 0.08
                }}
                style={{
                  opacity: 0.1 + (1 - Math.abs(8 - i) / 8) * 0.8
                }}
              />
            ))}
          </div>
        </div>
      </section>

      <div ref={modeSelectionRef} className="mode-selection-area">
        <div className="section-header">
          <h2 className="section-title">쇼핑 모드 선택</h2>
          <p className="section-subtitle">당신에게 가장 편안한 방식을 선택하세요</p>
        </div>

        <div className="mode-grid">
          <ModeCard onSelect={handleModeSelect} mode={{ id: 'audio', label: 'TYPE A', title: <>보이스<br />쇼핑</>, desc: <>화면을 보지 않고<br />음성만으로 완성하는 쇼핑</>, tags: ['전과정 음성', 'AI 가이드'], bgColor: 'linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%)', textColor: '#FFFFFF', tagBg: 'rgba(255,255,255,0.15)', icon: <Volume2 size={32} />, iconLarge: <Volume2 size={300} /> }} />
          <ModeCard onSelect={handleModeSelect} mode={{ id: 'big', label: 'TYPE B', title: <>큰 글씨<br />쇼핑</>, desc: <>돋보기 없이도<br />선명하고 시원한 화면</>, tags: ['큰 글씨', '간편 UI'], bgColor: 'linear-gradient(135deg, #A78BFA 0%, #8B5CF6 100%)', textColor: '#FFFFFF', tagBg: 'rgba(255,255,255,0.15)', icon: <Zap size={32} />, iconLarge: <Zap size={300} /> }} />
          <ModeCard onSelect={handleModeSelect} mode={{ id: 'common', label: 'TYPE C', title: <>표준<br />쇼핑</>, desc: <>시각 정보를 활용한<br />우리에게 익숙한 표준 모드</>, tags: ['표준 UI', '시각·음성 병행'], bgColor: 'linear-gradient(135deg, #818CF8 0%, #6366F1 100%)', textColor: '#FFFFFF', tagBg: 'rgba(255,255,255,0.15)', icon: <Layout size={32} />, iconLarge: <Layout size={300} /> }} />
          <ModeCard onSelect={handleModeSelect} mode={{ id: 'sharing', label: 'TYPE S', title: <>공유<br />쇼핑</>, desc: <>함께 실시간 화면을<br />보며 즐기는 소통 쇼핑</>, tags: ['화면 공유', '라이브'], bgColor: 'linear-gradient(135deg, #F472B6 0%, #EC4899 100%)', textColor: '#FFFFFF', tagBg: 'rgba(255,255,255,0.15)', icon: <Share2 size={32} />, iconLarge: <Share2 size={300} /> }} />
        </div>
      </div>

      <div className="how-to-use-section">
        <div className="how-to-use-container">
          <div className="how-to-label"> 
            <h3 style={{ fontSize: '3rem' }}>이용방법</h3> 
            <p>간단한 3단계 프로세스</p>
          </div>
          <div className="steps-wrapper">
            <div className="step-item">
              <span className="step-num">1</span>
              <span className="step-text">쇼핑 모드 선택</span>
            </div>
            <div className="step-item">
              <span className="step-num">2</span>
              <span className="step-text">상품 음성 검색 및 선택</span>
            </div>
            <div className="step-item">
              <span className="step-num">3</span>
              <span className="step-text">간편하게 구매</span>
            </div>
          </div>
        </div>
      </div>

      <section className="speciality-section">
        <div className="section-header center">
          <h2 className="section-title">HearBe의 특별함</h2>
          <p className="section-subtitle primary-color">누구에게나 평등한 쇼핑의 가치를 가장 선명하게 전달합니다.</p>
        </div>

        <div className="speciality-grid">
          <div className="spec-card purple large-h">
            <div className="spec-icon-box white-icon">
              <Mic size={32} />
            </div>
            <h3>보이스 컨트롤</h3>
            <p>목소리 하나로 상품 검색부터 주문까지<br />모든 쇼핑 과정을 한 번에 완료하세요.</p>
            <div className="spec-tags">
              <span>음성 인식</span>
              <span>AI 가이드</span>
              <span>핸즈프리</span>
            </div>
          </div>

          <div className="spec-card white">
            <div className="spec-icon-box text-purple">
              <Eye size={32} />
            </div>
            <h3>초고대비 모드</h3>
            <p>저시력 사용자를 위해 모든 화면 요소를<br />크고 선명하게 최적화하여 보여줍니다.</p>
            <div className="spec-tag-badge">WCAG AAA 준수</div>
          </div>

          <div className="spec-card white">
            <div className="spec-icon-box text-purple">
              <ShoppingBag size={32} />
            </div>
            <h3>통합 장바구니</h3>
            <p>여러 쇼핑몰의 상품들을 HearBe 안에서<br />하나의 리스트로 편리하게 관리하세요.</p>
          </div>

          <div className="spec-card dark wide">
            <div className="spec-content">
              <div className="spec-icon-box text-purple-light">
                <Command size={32} />
              </div>
              <h3>음성 명령 브릿지</h3>
              <p>사용자의 음성 메시지를 외부 쇼핑몰의<br />동작으로 실시간 변환하여 실행합니다.</p>
            </div>
            <div className="spec-visual">
              <div className="bridge-visual">
                <div className="mic-listening" />
                <div className="lines" />
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <footer className="landing-footer">
      <p>© 2026 HearBe. All rights reserved.</p>
    </footer>
  </div>
);

export default MainLanding;
