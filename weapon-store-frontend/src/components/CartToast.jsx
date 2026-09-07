import { Link, useLocation } from "react-router-dom";

export default function CartToast({ notice, onClose }) {
  const location = useLocation();
  if (!notice) return null;

  return (
    <aside className={`cart-toast cart-toast--${notice.type}`} role="status" aria-live="polite">
      <span className="cart-toast__icon" aria-hidden="true">
        {notice.type === "success" ? "✓" : "!"}
      </span>
      <div className="cart-toast__content">
        <strong>{notice.title}</strong>
        <span>{notice.text}</span>
      </div>
      <div className="cart-toast__actions">
        {(notice.type === "success" || notice.requiresLogin) && (
          <Link
            to={notice.requiresLogin ? "/login" : "/cart"}
            state={notice.requiresLogin ? { from: location } : undefined}
          >
            {notice.requiresLogin ? "Войти" : "В корзину"}
          </Link>
        )}
        <button type="button" onClick={onClose} aria-label="Закрыть уведомление">×</button>
      </div>
    </aside>
  );
}
