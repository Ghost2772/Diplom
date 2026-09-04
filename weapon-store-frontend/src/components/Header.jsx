import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/authContext";

export default function Header() {
  const { isAuthenticated, user, logout } = useAuth();
  const { pathname } = useLocation();
  const usesOverlayHeader = ["/", "/login", "/register"].includes(pathname);

  return (
    <header className={`header${usesOverlayHeader ? " header--home" : ""}`}>
      <div className="container nav">
        <Link to="/" className="logo">
          Muller's Firearms
        </Link>

        <nav className="nav-links">
          <Link to="/catalog">Каталог</Link>
          {isAuthenticated && <Link to="/profile">Профиль</Link>}
          {isAuthenticated && <Link to="/cart">Корзина</Link>}
          {isAuthenticated && <Link to="/orders">Заказы</Link>}
          {isAuthenticated && <Link to="/chat">AI-чат</Link>}
          {user?.is_admin && <Link to="/admin">Админ</Link>}
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
