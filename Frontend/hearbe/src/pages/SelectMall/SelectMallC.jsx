import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Home, ShoppingCart, User, ArrowUpRight, Layout } from 'lucide-react';
import './SelectMallC.css';
import coupangLogo from '../../assets/coupang_logo.png';
import naverPlusLogo from '../../assets/C/naver_plus_logo.png';
import gmarketLogo from '../../assets/C/Gmarket_logo.png';
import kurlyLogo from '../../assets/C/Kurly_logo.png';
import st11Logo from '../../assets/C/11st_logo.png';
import ssgLogo from '../../assets/C/ssg_logo.png';

const SelectMallC = ({ onBack, onHome, onCart, onMyPage, onSelectMall }) => {
    const navigate = useNavigate();

    const malls = [
        { id: 'coupang', name: '쿠팡', desc: '', color: '#E2211C', initial: 'C', logo: coupangLogo, logoSize: 300, url: 'https://www.coupang.com' },
        { id: 'naver', name: '네이버 쇼핑', desc: '', color: '#03C75A', initial: 'N', logo: naverPlusLogo, logoSize: 240, url: 'https://shopping.naver.com/ns/home' },
        { id: 'gmarket', name: 'G마켓', desc: '', color: '#0055ff', initial: 'G', logo: gmarketLogo, logoSize: 240, url: 'https://www.gmarket.co.kr' },
        { id: 'kurly', name: '마켓컬리', desc: '', color: '#5f0080', initial: 'K', logo: kurlyLogo, logoSize: 200, url: 'https://www.kurly.com' },
        { id: '11st', name: '11번가', desc: '', color: '#FF4B4B', initial: '1', logo: st11Logo, logoSize: 200, url: 'https://www.11st.co.kr' },
        { id: 'ssg', name: 'SSG.COM', desc: '', color: '#ffb100', initial: 'S', logo: ssgLogo, logoSize: 240, url: 'https://www.ssg.com' },
    ];

    const handleSelect = (mall) => {
        // Open shopping mall in new tab
        window.open(mall.url, '_blank');
    };

    return (
        <div className="select-mall-page-c">
            {/* Header 섹션 (디자인 통일) */}
            <header className="mall-header-c">
                <div className="header-left-c">
                    <div className="title-area-c" style={{ marginLeft: 0 }}>
                        <div className="title-icon-box-c">
                            <Layout size={24} />
                        </div>
                        <div className="title-text-c">
                            <h1>쇼핑몰 선택</h1>
                            <span className="subtitle-c">Select Shopping Mall</span>
                        </div>
                    </div>
                </div>

                <div className="header-right-c">
                    <button className="nav-item-c" onClick={onHome || (() => navigate('/'))}>
                        <div className="nav-icon-c"><Home size={24} /></div>
                        <span>홈</span>
                    </button>
                    <button className="nav-item-c" onClick={onCart || (() => navigate('/C/mypage/cart', { state: { activeTab: 'cart' } }))}>
                        <div className="nav-icon-c"><ShoppingCart size={24} /></div>
                        <span>장바구니</span>
                    </button>
                    <button className="nav-item-c" onClick={onMyPage || (() => navigate('/C/member-info'))}> {/* 마이페이지 링크를 /C/member-info로 변경 */}
                        <div className="nav-icon-c"><User size={24} /></div>
                        <span>마이페이지</span>
                    </button>
                </div>
            </header >

            {/* 메인 콘텐츠 */}
            < main className="mall-main-c" >
                <div className="mall-hero-c">
                    <h1 className="mall-main-title-c">어디서 쇼핑을 시작할까요?</h1>
                    <div className="voice-guide-badge-c">
                        <span className="badge-text-c">[SPACEBAR]</span>를 눌러 음성 명령이 가능합니다
                    </div>
                </div>

                <div className="mall-grid-container-c">
                    {malls.map((mall, index) => (
                        <div
                            key={mall.id}
                            className="mall-card-new-c"
                            onClick={() => handleSelect(mall)}
                        >
                            <div className="card-top-row-c">
                                <div className="card-title-row-c">
                                    <div className="card-num-badge-c" style={{ backgroundColor: mall.color }}>
                                        {index + 1}
                                    </div>
                                    <h3 className="mall-card-name-c">{mall.name}</h3>
                                </div>
                                <ArrowUpRight className="card-link-icon-c" size={20} />
                            </div>

                            <img src={mall.logo} alt={mall.name} className="card-watermark-logo-c" style={mall.logoSize ? { width: `${mall.logoSize}px` } : {}} />

                            <div className="card-content-c">
                                <p className="mall-card-desc-c">{mall.desc}</p>
                            </div>

                            <div className="card-footer-c">
                                <span className="open-store-text-c">OPEN STORE</span>
                                <span className="open-store-arrow-c">→</span>
                            </div>
                        </div>
                    ))}
                </div>
            </main >

            <footer className="landing-footer">
                <p>© 2026 HearBe. All rights reserved.</p>
            </footer>

            <div className="floating-question-c">?</div>
        </div >
    );
};

export default SelectMallC;
