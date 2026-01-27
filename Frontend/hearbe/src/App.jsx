import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login/LoginA';
import SignUp from './pages/SignUp/SignUpA';
import SelectMall from './pages/SelectMall/SelectMallA';
import StoreBrowser from './pages/StoreBrowser/StoreBrowserA';
import Cart from './pages/Cart/CartA';
import Mypage from './pages/Mypage/MypageA';
import MemberInfo from './pages/Mypage/MemberInfoA';
import CardManagement from './pages/Mypage/CardManagementA';
import Wishlist from './pages/Mypage/WishlistA';
import OrderHistory from './pages/Mypage/OrderHistoryA';

import './App.css';

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/mall" element={<SelectMall />} />
        <Route path="/store" element={<StoreBrowser />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/mypage" element={<Mypage />} />
        <Route path="/mypage/profile" element={<MemberInfo />} />
        <Route path="/mypage/orders" element={<OrderHistory />} />
        <Route path="/mypage/wishlist" element={<Wishlist />} />
        <Route path="/mypage/card" element={<CardManagement />} />
      </Routes>
    </>
  )
}

export default App
