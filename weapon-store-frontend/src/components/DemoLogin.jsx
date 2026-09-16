import { useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { loginDemo } from "../api/authApi";
import { useAuth } from "../context/authContext";
import { getApiErrorMessage } from "../utils/apiErrors";

export default function DemoLogin({ disabled = false, onPendingChange }) {
  const { demoConfig, isAuthenticated, login } = useAuth();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const requestInFlight = useRef(false);
  const location = useLocation();
  const navigate = useNavigate();

  if (!demoConfig?.enabled || isAuthenticated) return null;

  const handleDemoLogin = async () => {
    if (requestInFlight.current || disabled) return;
    requestInFlight.current = true;
    setPending(true);
    setError("");
    onPendingChange?.(true);
    try {
      const data = await loginDemo();
      login(data.access_token);
      const from = location.state?.from;
      const destination = from?.pathname && !from.pathname.startsWith("/admin")
        ? `${from.pathname}${from.search || ""}${from.hash || ""}`
        : "/profile";
      navigate(destination, { replace: true });
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "Не удалось открыть демо-аккаунт. Попробуйте ещё раз"));
    } finally {
      requestInFlight.current = false;
      setPending(false);
      onPendingChange?.(false);
    }
  };

  return (
    <section className="demo-entry" aria-label="Знакомство с проектом">
      <div>
        <p className="demo-entry__eyebrow">Проект для портфолио</p>
        <p className="demo-entry__description">
          Готовый профиль, корзина и примеры заказов
        </p>
      </div>
      <button
        type="button"
        className="demo-entry__button"
        disabled={pending || disabled}
        onClick={handleDemoLogin}
        aria-busy={pending}
      >
        {pending ? "Подготавливаем демо…" : "Войти в демо-аккаунт"}
        {!pending && <span aria-hidden="true">↗</span>}
      </button>
      <p className="demo-entry__hint">
        Без регистрации · Отдельная сессия на {demoConfig.session_minutes} мин
      </p>
      {error && <p className="demo-entry__error" role="alert">{error}</p>}
    </section>
  );
}
