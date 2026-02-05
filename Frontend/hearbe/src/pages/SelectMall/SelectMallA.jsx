import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShoppingCart, User, LogOut } from 'lucide-react';
import iconCoupang from '../../assets/coupang_logo.png';
import iconNaver from '../../assets/C/naver_plus_logo.png';
import icon11st from '../../assets/C/11st_logo.png';
import iconSsg from '../../assets/C/ssg_logo.png';
import logoA from '../../assets/logoA.png';
import { authAPI } from '../../services/authAPI';
import Swal from 'sweetalert2';
import './SelectMallA.css';

const SelectMall = () => {
    const navigate = useNavigate();

    const malls = [
        { id: '1', name: '쿠팡', logo: iconCoupang, url: 'https://www.coupang.com', color: '#E2211C' },
        { id: '2', name: '네이버 쇼핑', logo: iconNaver, url: 'https://shopping.naver.com/ns/home', color: '#03C75A' },
        { id: '3', name: '11번가', logo: icon11st, url: 'https://m.11st.co.kr/', color: '#FF4B4B' },
        { id: '4', name: 'SSG.COM', logo: iconSsg, url: 'https://m.ssg.com/', color: '#ffb100' },
    ];

    const handleSelectMall = (url) => {
        window.open(url, '_blank', 'noopener,noreferrer');
    };

    const handleLogout = () => {
        Swal.fire({
            title: '로그아웃 하시겠습니까?',
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: '로그아웃',
            cancelButtonText: '취소'
        }).then(async (result) => {
            if (result.isConfirmed) {
                try {
                    await authAPI.logout();
                } catch (err) {
                    console.warn('Logout failed:', err);
                } finally {
                    localStorage.clear();
                    navigate('/main');
                }
            }
        });
    };

    return (
        <div className="select-mall-a-container">
            {/* Logo */}
            <img
                src={logoA}
                alt="Logo"
                className="select-mall-a-logo cursor-pointer"
                onClick={() => navigate('/main')}
            />

            {/* Top Navigation */}
            <header className="select-mall-a-header">
                <div className="header-actions-a">
                    <button className="header-btn-a cursor-pointer" onClick={() => navigate('/A/cart')}>
                        <ShoppingCart size={56} />
                        <span>카트</span>
                    </button>
                    <button className="header-btn-a cursor-pointer" onClick={() => navigate('/A/member-info')}>
                        <User size={56} />
                        <span>마이</span>
                    </button>
                    <button className="header-btn-a cursor-pointer" onClick={handleLogout}>
                        <LogOut size={56} />
                        <span>로그아웃</span>
                    </button>
                </div>
            </header>

            {/* Main Content */}
            <main className="select-mall-a-main">
                <div className="mall-list-a">
                    {malls.map((mall, index) => (
                        <button
                            key={mall.id}
                            className="mall-item-a cursor-pointer"
                            onClick={() => handleSelectMall(mall.url)}
                        >
                            <div className="mall-num-a" style={{ backgroundColor: mall.color }}>{index + 1}</div>
                            <div className="mall-info-a">
                                <span className="mall-name-a">{mall.name}</span>
                                <img src={mall.logo} alt={mall.name} className="mall-logo-img-a" />
                            </div>
                            <div className="mall-arrow-a">→</div>
                        </button>
                    ))}
                </div>
            </main>

            <footer className="select-mall-a-footer">
                <p>© 2026 HearBe. All rights reserved.</p>
            </footer>
        </div>
    );
};

export default SelectMall;
