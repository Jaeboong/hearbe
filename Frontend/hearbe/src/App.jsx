import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login/LoginA';
import SignUp from './components/SignUp/SignUpA';
import SelectMall from './components/SelectMall/SelectMallA';
import StoreBrowser from './components/StoreBrowser/StoreBrowserA';
import Cart from './components/Cart/CartA';
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
