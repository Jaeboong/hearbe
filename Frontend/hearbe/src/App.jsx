import AppRouter from './router/AppRouter';
import './App.css';

/**
 * App - 애플리케이션 루트 컴포넌트
 * 모든 라우팅 로직은 AppRouter로 위임
 */
export default function App() {
  return <AppRouter />;
}
