import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import logoA from '../../assets/logoA.png';
import iconCamera from '../../assets/icon-camera.png';
import './FindPasswordA.css';

const FindPasswordA = () => {
    const navigate = useNavigate();
    const [showModal, setShowModal] = useState(false);
    const [cardForm, setCardForm] = useState({
        card_company: '',
        card_number: '',
        expiration_date: '',
        cvc: ''
    });

    const handleOpen = () => {
        setCardForm({
            card_company: '신한카드',
            card_number: '1234-5678-9012-3456',
            expiration_date: '01/28',
            cvc: '123'
        });
        setShowModal(true);
    };

    const handleClose = () => {
        setShowModal(false);
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        if (name === 'card_number') {
            const digits = value.replace(/[^0-9]/g, '').slice(0, 16);
            setCardForm((prev) => ({ ...prev, [name]: digits }));
            return;
        }
        if (name === 'expiration_date') {
            const digits = value.replace(/[^0-9]/g, '').slice(0, 4);
            const formatted = digits.length <= 2 ? digits : `${digits.slice(0, 2)}/${digits.slice(2)}`;
            setCardForm((prev) => ({ ...prev, [name]: formatted }));
            return;
        }
        if (name === 'cvc') {
            const digits = value.replace(/[^0-9]/g, '').slice(0, 3);
            setCardForm((prev) => ({ ...prev, [name]: digits }));
            return;
        }
        setCardForm((prev) => ({ ...prev, [name]: value }));
    };

    const handleVerify = () => {
        const hardcoded = {
            card_company: '신한카드',
            card_number: '1234567890123456',
            expiration_date: '01/28',
            cvc: '123'
        };
        const input = {
            card_company: cardForm.card_company.trim(),
            card_number: cardForm.card_number.replace(/[^0-9]/g, ''),
            expiration_date: cardForm.expiration_date.trim(),
            cvc: cardForm.cvc.trim()
        };
        const isMatch =
            input.card_company === hardcoded.card_company &&
            input.card_number === hardcoded.card_number &&
            input.expiration_date === hardcoded.expiration_date &&
            input.cvc === hardcoded.cvc;

        if (!isMatch) {
            alert('카드 정보가 일치하지 않습니다.');
            return;
        }
        setShowModal(false);
        navigate('/A/changePassword');
    };

    return (
        <div className="findpw-container">
            <img
                src={logoA}
                alt="Logo"
                className="findpw-logo"
                onClick={() => navigate('/')}
            />

            <div className="findpw-box">
                <h1 className="findpw-title">비밀번호 변경</h1>
                <p className="findpw-desc">
                    장애인 복지 카드를 촬영하여
                    <br />
                    비밀번호를 변경할 수 있습니다.
                </p>

                <div className="findpw-card" onClick={handleOpen}>
                    <div className="findpw-card-title">장애인 복지카드 촬영하기</div>
                    <img src={iconCamera} alt="Camera" className="findpw-camera-icon" />
                </div>
            </div>

            {showModal && (
                <div className="findpw-modal-overlay" onClick={handleClose}>
                    <div className="findpw-modal-box" onClick={(e) => e.stopPropagation()}>
                        <div className="findpw-modal-close" onClick={handleClose}>X</div>
                        <div className="findpw-modal-title">카드 인증</div>
                        <div className="findpw-modal-desc">복지카드 정보를 입력해주세요.</div>

                        <div className="findpw-form-field">
                            <label>카드사</label>
                            <input
                                type="text"
                                name="card_company"
                                value={cardForm.card_company}
                                onChange={handleInputChange}
                                className="findpw-modal-input"
                            />
                        </div>
                        <div className="findpw-form-field">
                            <label>복지카드 번호</label>
                            <input
                                type="text"
                                name="card_number"
                                value={cardForm.card_number}
                                onChange={handleInputChange}
                                className="findpw-modal-input"
                                placeholder="숫자 16자리"
                            />
                        </div>
                        <div className="findpw-form-row">
                            <div className="findpw-form-field half">
                                <label>유효기간</label>
                                <input
                                    type="text"
                                    name="expiration_date"
                                    value={cardForm.expiration_date}
                                    onChange={handleInputChange}
                                    className="findpw-modal-input"
                                    placeholder="MM/YY"
                                />
                            </div>
                            <div className="findpw-form-field half">
                                <label>CVC</label>
                                <input
                                    type="text"
                                    name="cvc"
                                    value={cardForm.cvc}
                                    onChange={handleInputChange}
                                    className="findpw-modal-input"
                                    placeholder="000"
                                />
                            </div>
                        </div>
                        <button className="findpw-confirm-btn" onClick={handleVerify}>인증하기</button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default FindPasswordA;
