import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { useState, useRef } from 'react';

// [페이지 컴포넌트]
import MainLanding from '../pages/MainLanding';

// [A형 페이지 임포트]
import LoginA from '../pages/Login/LoginA';
import SignUpA from '../pages/SignUp/SignUpA';
import SelectMallA from '../pages/SelectMall/SelectMallA';
import StoreBrowserA from '../pages/StoreBrowser/StoreBrowserA';
import CartA from '../pages/Cart/CartA';
import MemberInfoA from '../pages/MemberInfo_A/MemberInfoA';
import OrderHistoryA from '../pages/OrderHistory_A/OrderHistoryA';
import WishlistA from '../pages/Wishlist_A/WishlistA';
import CardManagementA from '../pages/CardManagement_A/CardManagementA';

// [C형 페이지 임포트]
import LoginC from '../pages/Login/LoginC';
import SignUpC from '../pages/SignUp/SignUpC';
import SelectMallC from '../pages/SelectMall/SelectMallC';
import StoreBrowserC from '../pages/StoreBrowser/StoreBrowserC';
import CartC from '../pages/Cart/CartC';
import MyPageC from '../pages/MyPage/MyPageC';
import FindIdC from '../pages/FindId/FindIdC';
import FindPasswordC from '../pages/FindPassword/FindPasswordC';

// [S형 페이지 임포트]
import LoginS from '../pages/Login/LoginS';

/**
 * AppContent - BrowserRouter 내부에서 실행되는 컴포넌트
 * useNavigate와 같은 라우터 훅을 사용할 수 있음
 */
function AppContent() {
  const navigate = useNavigate();
  const [selectedMode, setSelectedMode] = useState('audio');
  const [micPermissionGranted, setMicPermissionGranted] = useState(false);
  const [showInitialSetup, setShowInitialSetup] = useState(false);
  const modeSelectionRef = useRef(null);

  const handleSetupComplete = (micGranted) => {
    setMicPermissionGranted(micGranted);
    setShowInitialSetup(false);
  };

  const handleModeSelect = (mode, label) => {
    if (micPermissionGranted || mode === 'audio') {
      const utterance = new SpeechSynthesisUtterance(`${label} 모드를 선택하셨습니다.`);
      utterance.lang = 'ko-KR';
      window.speechSynthesis.speak(utterance);
    }
    setSelectedMode(mode);

    // 모드에 따라 분기 처리
    if (mode === 'common') {
      navigate('/C/login');
    } else {
      navigate('/A/login');
    }
  };

  const handleReset = () => {
    localStorage.clear();
    window.location.reload();
  };

  return (
    <Routes>
      {/* 메인 랜딩 페이지 */}
      <Route
        path="/"
        element={
          <MainLanding
            handleReset={handleReset}
            handleModeSelect={handleModeSelect}
            modeSelectionRef={modeSelectionRef}
          />
        }
      />

      {/* Type A Routes 수정 제안 */}
      <Route
        path="/A/login"
        element={
          <LoginA
            mode={selectedMode}
            micPermissionGranted={micPermissionGranted}
            onLoginSuccess={() => navigate('/A/mall')}
            onSignup={() => navigate('/A/signup')}
          />
        }
      />

      <Route
        path="/A/mall"
        element={
          <SelectMallA
            mode={selectedMode}
            micPermissionGranted={micPermissionGranted}
            onSelectMall={(mall) => navigate('/A/store', { state: { url: mall.url } })}
          />
        }
      />

      {/* Type C Routes */}
      <Route
        path="/C/login"
        element={
          <LoginC
            onLoginSuccess={() => navigate('/C/mall')}
            onSignup={() => navigate('/C/signup')}
            onFindId={() => navigate('/C/findId')}
            onFindPassword={() => navigate('/C/findPassword')}
          />
        }
      />
      <Route
        path="/C/signup"
        element={<SignUpC onBack={() => navigate(-1)} />}
      />
      <Route
        path="/C/findId"
        element={<FindIdC mode="common" onBack={() => navigate(-1)} />}
      />
      <Route
        path="/C/findPassword"
        element={<FindPasswordC mode="common" onBack={() => navigate(-1)} />}
      />
      <Route
        path="/C/mall"
        element={
          <SelectMallC
            onBack={() => navigate('/C/login')}
            onHome={() => navigate('/')}
            onCart={() => navigate('/C/mypage', { state: { activeTab: 'cart' } })}
            onMyPage={() => navigate('/C/mypage')}
            onSelectMall={(mall) => navigate('/C/store', { state: { url: mall.url, name: mall.name } })}
          />
        }
      />
      <Route
        path="/C/store"
        element={
          <StoreBrowserC
            onBack={() => navigate('/C/mall')}
            onHome={() => navigate('/')}
            onCart={() => navigate('/C/mypage', { state: { activeTab: 'cart' } })}
            onMyPage={() => navigate('/C/mypage')}
          />
        }
      />
      <Route
        path="/C/cart"
        element={
          <CartC
            onClose={() => navigate(-1)}
            onHome={() => navigate('/')}
            onCart={() => navigate('/C/mypage', { state: { activeTab: 'cart' } })}
            onMyPage={() => navigate('/C/mypage')}
          />
        }
      />
      <Route
        path="/C/mypage"
        element={
          <MyPageC
            mode="common"
            onBack={() => navigate(-1)}
            onHome={() => navigate('/')}
            onCart={() => navigate('/C/mypage', { state: { activeTab: 'cart' } })}
            onMyPage={() => navigate('/C/mypage')}
          />
        }
      />

      {/* Type A Routes */}
      <Route path="/A/login" element={<LoginA mode={selectedMode} micPermissionGranted={micPermissionGranted} />} />
      <Route path="/A/signup" element={<SignUpA mode={selectedMode} />} />
      <Route path="/A/mall" element={<SelectMallA mode={selectedMode} micPermissionGranted={micPermissionGranted} />} />
      <Route path="/A/store" element={<StoreBrowserA mode={selectedMode} micPermissionGranted={micPermissionGranted} />} />
      <Route path="/A/cart" element={<CartA mode={selectedMode} />} />
      <Route path="/A/mypage" element={<Navigate to="/A/member-info" replace />} />
      <Route path="/A/member-info" element={<MemberInfoA mode={selectedMode} />} />
      <Route path="/A/order-history" element={<OrderHistoryA mode={selectedMode} />} />
      <Route path="/A/wishlist" element={<WishlistA mode={selectedMode} />} />
      <Route path="/A/card-management" element={<CardManagementA mode={selectedMode} />} />

      {/* Flat Routes for compatibility */}
      <Route path="/login" element={<Navigate to="/A/login" replace />} />
      <Route path="/signup" element={<Navigate to="/C/signup" replace />} />
      <Route path="/mall" element={<Navigate to="/C/mall" replace />} />
      <Route path="/store" element={<Navigate to="/C/store" replace />} />
      <Route path="/cart" element={<Navigate to="/C/cart" replace />} />
      <Route path="/login-c" element={<Navigate to="/C/login" replace />} />
      <Route path="/signup-c" element={<Navigate to="/C/signup" replace />} />
      <Route path="/mall-c" element={<Navigate to="/C/mall" replace />} />
      <Route path="/store-c" element={<Navigate to="/C/store" replace />} />
      <Route path="/mypage-c" element={<Navigate to="/C/mypage" replace />} />
      <Route path="/login-s" element={<LoginS />} />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

/**
 * AppRouter - 애플리케이션의 최상위 라우터 컴포넌트
 * BrowserRouter를 포함하여 모든 라우팅 로직을 관리
 */
export default function AppRouter() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}
