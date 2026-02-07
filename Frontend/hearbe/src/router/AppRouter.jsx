import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { useState, useRef } from 'react';

import MainLanding from '../pages/MainLanding';
import BrandLanding from '../pages/BrandLanding';
import InitialSetup from '../pages/InitialSetup/InitialSetup';
import Intro from '../pages/Intro/Intro';
import AudioPage from '../pages/Audio/AudioPage';

import LoginB from '../pages/Login/LoginB';
import SignUpB from '../pages/SignUp/SignUpB';
import SelectMallB from '../pages/SelectMall/SelectMallB';
import StoreBrowserB from '../pages/StoreBrowser/StoreBrowserB';
import CartB from '../pages/Cart/CartB';
import MemberInfoB from '../pages/MemberInfo/MemberInfoB';
import OrderHistoryB from '../pages/OrderHistory/OrderHistoryB';
import WishlistB from '../pages/Wishlist/WishlistB';
import CardManagementB from '../pages/CardManagement_B/CardManagementB';
import FindIdB from '../pages/FindId/FindIdB';
import FindPasswordB from '../pages/FindPassword/FindPasswordB';
import ChangePasswordB from '../pages/FindPassword/ChangePasswordB';

import LoginC from '../pages/Login/LoginC';
import SignUpC from '../pages/SignUp/SignUpC';
import SelectMallC from '../pages/SelectMall/SelectMallC';
import CartC from '../pages/Cart/CartC';
import MemberInfoC from '../pages/MemberInfo/MemberInfoC';
import OrderHistoryC from '../pages/OrderHistory/OrderHistoryC';
import WishlistC from '../pages/Wishlist/WishlistC';
import FindIdC from '../pages/FindId/FindIdC';
import FindPasswordC from '../pages/FindPassword/FindPasswordC';

import GuardianViewS from '../pages/GuardianView/GuardianViewS';


function AppContent() {
  const navigate = useNavigate();
  const location = useLocation();
  const [selectedMode, setSelectedMode] = useState('audio');
  const [micPermissionGranted, setMicPermissionGranted] = useState(false);
  const [showInitialSetup, setShowInitialSetup] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('app') === 'mcp') {
      localStorage.setItem('hearbe_mcp_setup_completed', 'true');
      return false;
    }
    return localStorage.getItem('hearbe_mcp_setup_completed') !== 'true';
  });
  const modeSelectionRef = useRef(null);

  const handleModeSelect = (mode) => {
    setSelectedMode(mode);
    if (mode === 'common') {
      navigate('/C/login');
    } else if (mode === 'sharing') {
      navigate('/S/join');
    } else if (mode === 'big') {
      navigate('/B/login');
    } else {
      navigate('/A');
    }
  };

  const handleSetupComplete = (granted = false) => {
    setMicPermissionGranted(granted);
    setShowInitialSetup(false);
  };

  if (showInitialSetup && location.pathname === '/main') {
    return <InitialSetup onComplete={handleSetupComplete} />;
  }

  return (
    <Routes>
      <Route path="/" element={<Navigate to="/intro" replace />} />
      <Route path="/intro" element={<Intro />} />
      <Route path="/guide" element={<BrandLanding />} />
      <Route
        path="/main"
        element={
          <MainLanding
            handleModeSelect={handleModeSelect}
            modeSelectionRef={modeSelectionRef}
            onOpenSetup={() => setShowInitialSetup(true)}
          />
        }
      />
      <Route path="/A/*" element={<AudioPage />} />
      <Route
        path="/B/login"
        element={
          <LoginB
            mode={selectedMode}
            micPermissionGranted={micPermissionGranted}
            onLoginSuccess={() => navigate('/B/mall')}
            onSignup={() => navigate('/B/signup')}
          />
        }
      />

      <Route
        path="/B/signup"
        element={
          <SignUpB
            mode={selectedMode}
            micPermissionGranted={micPermissionGranted}
            onBack={() => navigate('/B/login')}
          />
        }
      />
      <Route
        path="/B/mall"
        element={
          <SelectMallB
            mode={selectedMode}
            micPermissionGranted={micPermissionGranted}
          />
        }
      />
      <Route
        path="/B/store"
        element={
          <StoreBrowserB
            mode={selectedMode}
            micPermissionGranted={micPermissionGranted}
            onBack={() => navigate('/B/mall')}
            onHome={() => navigate('/main')}
            onCart={() => navigate('/B/cart')}
            onMyPage={() => navigate('/B/member-info')}
          />
        }
      />
      <Route
        path="/B/cart"
        element={
          <CartB
            mode={selectedMode}
            micPermissionGranted={micPermissionGranted}
            onBack={() => navigate(-1)}
            onHome={() => navigate('/main')}
          />
        }
      />
      <Route
        path="/B/member-info"
        element={
          <MemberInfoB
            mode={selectedMode}
            micPermissionGranted={micPermissionGranted}
            onBack={() => navigate(-1)}
            onHome={() => navigate('/main')}
          />
        }
      />
      <Route
        path="/B/order-history"
        element={
          <OrderHistoryB
            mode={selectedMode}
            micPermissionGranted={micPermissionGranted}
            onBack={() => navigate(-1)}
            onHome={() => navigate('/main')}
          />
        }
      />
      <Route
        path="/B/wishlist"
        element={
          <WishlistB
            mode={selectedMode}
            micPermissionGranted={micPermissionGranted}
            onBack={() => navigate(-1)}
            onHome={() => navigate('/main')}
          />
        }
      />
      <Route
        path="/B/card-management"
        element={
          <CardManagementB
            mode={selectedMode}
            micPermissionGranted={micPermissionGranted}
            onBack={() => navigate(-1)}
            onHome={() => navigate('/main')}
          />
        }
      />
      <Route
        path="/B/findId"
        element={<FindIdB />}
      />
      <Route
        path="/B/findPassword"
        element={<FindPasswordB />}
      />
      <Route
        path="/B/changePassword"
        element={<ChangePasswordB />}
      />
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
        element={<FindPasswordC mode="common" onBack={() => navigate('/C/login')} />}
      />
      <Route
        path="/C/mall"
        element={
          <SelectMallC
            onBack={() => navigate('/C/login')}
            onCart={() => navigate('/C/cart')}
            onMyPage={() => navigate('/C/member-info')}
            onSelectMall={(mall) => window.open(mall.url, '_blank')}
          />
        }
      />
      <Route
        path="/C/order-history"
        element={
          <OrderHistoryC
            onHome={() => navigate('/C/mall')}
          />
        }
      />
      <Route
        path="/C/wishlist"
        element={
          <WishlistC
            onHome={() => navigate('/C/mall')}
          />
        }
      />
      <Route
        path="/C/member-info"
        element={
          <MemberInfoC
            onBack={() => navigate('/C/mypage')}
            onHome={() => navigate('/C/mall')}
            onCart={() => navigate('/C/cart')}
            onMyPage={() => navigate('/C/member-info')}
          />
        }
      />

      <Route path="/C/mypage" element={<Navigate to="/C/member-info" replace />} />
      <Route
        path="/C/cart"
        element={
          <CartC
            onHome={() => navigate('/C/mall')}
          />
        }
      />
      <Route path="/login" element={<Navigate to="/B/login" replace />} />
      <Route path="/signup" element={<Navigate to="/C/signup" replace />} />
      <Route path="/mall" element={<Navigate to="/C/mall" replace />} />
      <Route path="/cart" element={<Navigate to="/C/cart" replace />} />
      <Route path="/login-c" element={<Navigate to="/C/login" replace />} />
      <Route path="/signup-c" element={<Navigate to="/C/signup" replace />} />
      <Route path="/mall-c" element={<Navigate to="/C/mall" replace />} />
      <Route path="/mypage-c" element={<Navigate to="/C/mypage" replace />} />
      <Route path="/login-s" element={<Navigate to="/S/join" replace />} />
      <Route path="/S/guardian-view" element={<Navigate to="/S/join" replace />} />
      <Route path="/S/join" element={<GuardianViewS />} caseSensitive={false} />
      <Route path="*" element={<Navigate to="/intro" replace />} />
    </Routes>
  );
}

export default function AppRouter() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AppContent />
    </BrowserRouter>
  );
}
