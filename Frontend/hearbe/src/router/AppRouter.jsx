import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { useState, useRef } from 'react';

// [페이지 컴포넌트]
import MainLanding from '../pages/MainLanding';
import InitialSetup from '../pages/InitialSetup/InitialSetup';

// [A형 페이지 임포트]
import LoginA from '../pages/Login/LoginA';
import SignUpA from '../pages/SignUp/SignUpA';
import SelectMallA from '../pages/SelectMall/SelectMallA';
import StoreBrowserA from '../pages/StoreBrowser/StoreBrowserA';
import CartA from '../pages/Cart/CartA';
import MemberInfoA from '../pages/MemberInfo/MemberInfoA';
import OrderHistoryA from '../pages/OrderHistory/OrderHistoryA';
import WishlistA from '../pages/Wishlist_A/WishlistA';
import CardManagementA from '../pages/CardManagement_A/CardManagementA';
import FindIdA from '../pages/FindId/FindIdA';
import FindPasswordA from '../pages/FindPassword/FindPasswordA';
import ChangePasswordA from '../pages/FindPassword/ChangePasswordA';

// [C형 페이지 임포트]
import LoginC from '../pages/Login/LoginC';
import SignUpC from '../pages/SignUp/SignUpC';
import SelectMallC from '../pages/SelectMall/SelectMallC';
import StoreBrowserC from '../pages/StoreBrowser/StoreBrowserC';
import CartC from '../pages/Cart/CartC';
import MemberInfoC from '../pages/MemberInfo/MemberInfoC';
import OrderHistoryC from '../pages/OrderHistory/OrderHistoryC';
import WishlistC from '../pages/Wishlist_C/WishlistC';
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
  const [showInitialSetup, setShowInitialSetup] = useState(() => {
    return localStorage.getItem('hearbe_mcp_setup_completed') !== 'true';
  });
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

  // 초기 설정이 완료되지 않았으면 InitialSetup을 먼저 보여줌
  if (showInitialSetup) {
    return <InitialSetup onComplete={handleSetupComplete} />;
  }

  return (
    <Routes>
      {/* 메인 랜딩 페이지 */}
      <Route
        path="/"
        element={
          <MainLanding
            handleModeSelect={handleModeSelect}
            modeSelectionRef={modeSelectionRef}
          />
        }
      />

      {/* Type A Routes */}
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
        path="/A/signup"
        element={
          <SignUpA
            mode={selectedMode}
            micPermissionGranted={micPermissionGranted}
            onBack={() => navigate('/A/login')}
          />
        }
      />
      <Route
        path="/A/mall"
        element={
          <SelectMallA
            mode={selectedMode}
            micPermissionGranted={micPermissionGranted}
          />
        }
      />
      <Route
        path="/A/store"
        element={
          <StoreBrowserA
            mode={selectedMode}
            micPermissionGranted={micPermissionGranted}
            onBack={() => navigate('/A/mall')}
            onHome={() => navigate('/')}
            onCart={() => navigate('/A/cart')}
            onMyPage={() => navigate('/A/member-info')}
          />
        }
      />
      <Route
        path="/A/cart"
        element={
          <CartA
            mode={selectedMode}
            micPermissionGranted={micPermissionGranted}
            onBack={() => navigate(-1)}
            onHome={() => navigate('/')}
          />
        }
      />
      <Route
        path="/A/member-info"
        element={
          <MemberInfoA
            mode={selectedMode}
            micPermissionGranted={micPermissionGranted}
            onBack={() => navigate(-1)}
            onHome={() => navigate('/')}
          />
        }
      />
      <Route
        path="/A/order-history"
        element={
          <OrderHistoryA
            mode={selectedMode}
            micPermissionGranted={micPermissionGranted}
            onBack={() => navigate(-1)}
            onHome={() => navigate('/')}
          />
        }
      />
      <Route
        path="/A/wishlist"
        element={
          <WishlistA
            mode={selectedMode}
            micPermissionGranted={micPermissionGranted}
            onBack={() => navigate(-1)}
            onHome={() => navigate('/')}
          />
        }
      />
      <Route
        path="/A/card-management"
        element={
          <CardManagementA
            mode={selectedMode}
            micPermissionGranted={micPermissionGranted}
            onBack={() => navigate(-1)}
            onHome={() => navigate('/')}
          />
        }
      />
      <Route
        path="/A/findId"
        element={<FindIdA />}
      />
      <Route
        path="/A/findPassword"
        element={<FindPasswordA />}
      />
      <Route
        path="/A/changePassword"
        element={<ChangePasswordA />}
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
            onCart={() => navigate('/C/cart')}
            onMyPage={() => navigate('/C/member-info')}
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
            onCart={() => navigate('/C/cart')}
            onMyPage={() => navigate('/C/member-info')}
          />
        }
      />
      <Route
        path="/C/order-history"
        element={
          <OrderHistoryC
            onHome={() => navigate('/')}
          />
        }
      />
      <Route
        path="/C/wishlist"
        element={
          <WishlistC
            onHome={() => navigate('/')}
          />
        }
      />
      <Route
        path="/C/member-info"
        element={
          <MemberInfoC // MemberInfoC는 이제 /C/member-info 경로에서 직접 렌더링
            onBack={() => navigate('/C/mypage')} // 뒤로가기 시 /C/mypage (리다이렉트될 경로)로 이동
            onHome={() => navigate('/')}
            onCart={() => navigate('/C/cart')}
            onMyPage={() => navigate('/C/member-info')} // 마이페이지 링크를 /C/member-info로 변경
          />
        }
      />

      {/* /C/mypage는 이제 /C/member-info로 리다이렉트 */}
      <Route path="/C/mypage" element={<Navigate to="/C/member-info" replace />} />
      <Route
        path="/C/cart"
        element={
          <CartC
            onHome={() => navigate('/')}
          />
        }
      />

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
