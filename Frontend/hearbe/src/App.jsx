import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login/LoginA';
import SignUp from './pages/SignUp/SignUpA';
import SelectMall from './pages/SelectMall/SelectMallA';
import StoreBrowser from './pages/StoreBrowser/StoreBrowserA';
import Cart from './pages/Cart/CartA';

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
      </Routes>
    </>
  )
}

export default App
