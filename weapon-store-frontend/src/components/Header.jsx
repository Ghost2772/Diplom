import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/authContext";

export default function Header() {
  const { isAuthenticated, logout } = useAuth();
  const { pathname } = useLocation();
  const isHomePage = pathname === "/";

  return (
    <header className={`header${isHomePage ? " header--home" : ""}`}>
      <div className="container nav">
        <Link to="/" className="logo">
          Muller's Firearms
        </Link>

        <nav className="nav-links">
          <Link to="/catalog">Каталог</Link>
          {isAuthenticated && <Link to="/cart">Корзина</Link>}
          {isAuthenticated && <Link to="/orders">Заказы</Link>}
          {isAuthenticated && <Link to="/chat">AI-чат</Link>}
          {!isAuthenticated && <Link to="/login">Вход</Link>}
          {!isAuthenticated && <Link to="/register">Регистрация</Link>}
          {isAuthenticated && (
            <button onClick={logout} className="logout-btn">
              Выйти
            </button>
          )}
        </nav>
      </div>
    </header>
  );
}
