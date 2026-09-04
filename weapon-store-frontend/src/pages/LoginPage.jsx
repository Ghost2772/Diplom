import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { loginUser } from "../api/authApi";
import { useAuth } from "../context/authContext";
import { getApiErrorMessage } from "../utils/apiErrors";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const { login } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const registrationCompleted = location.state?.registered === true;
  const destination = location.state?.from?.pathname || "/catalog";

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    const formData = new URLSearchParams();
    formData.append("username", email.trim());
    formData.append("password", password);

    try {
      const data = await loginUser(formData);
      login(data.access_token);
      navigate(destination, { replace: true });
    } catch (requestError) {
      setError(
        getApiErrorMessage(
          requestError,
          "Не удалось войти. Проверьте email и пароль.",
        ),
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="auth-page auth-page--login">
      <div className="container auth-layout">
        <section className="glass-panel auth-card" aria-labelledby="login-title">
          <div className="auth-card__intro">
            <p className="auth-eyebrow">Личный кабинет</p>
            <h1 id="login-title">С возвращением</h1>
            <p>Войдите, чтобы продолжить работу с каталогом, заказами и AI-консультантом.</p>
          </div>

          {registrationCompleted && (
            <div className="auth-notice auth-notice--success" role="status">
              <span aria-hidden="true">✓</span>
              Регистрация завершена. Теперь можно войти.
            </div>
          )}

          {error && (
            <div className="auth-notice auth-notice--error" role="alert">
              <span aria-hidden="true">!</span>
              {error}
            </div>
          )}

          <form className="auth-form" onSubmit={handleSubmit}>
            <label className="auth-field">
              <span>Email</span>
              <input
                type="email"
                name="email"
                value={email}
                onChange={(event) => {
                  setEmail(event.target.value);
                  setError("");
                }}
                placeholder="you@example.com"
                autoComplete="email"
                required
              />
            </label>

            <div className="auth-field">
              <label htmlFor="login-password">Пароль</label>
              <span className="auth-field__control">
                <input
                  id="login-password"
                  type={showPassword ? "text" : "password"}
                  name="password"
                  value={password}
                  onChange={(event) => {
                    setPassword(event.target.value);
                    setError("");
                  }}
                  placeholder="Введите пароль"
                  autoComplete="current-password"
                  required
                />
                <button
                  type="button"
                  className="auth-field__toggle"
                  onClick={() => setShowPassword((visible) => !visible)}
                  aria-label={showPassword ? "Скрыть пароль" : "Показать пароль"}
                >
                  {showPassword ? "Скрыть" : "Показать"}
                </button>
              </span>
            </div>

            <button className="auth-submit" type="submit" disabled={submitting}>
              <span>{submitting ? "Выполняется вход..." : "Войти"}</span>
              {!submitting && <span className="auth-submit__arrow" aria-hidden="true">↗</span>}
            </button>
          </form>

          <p className="auth-card__footer">
            Впервые здесь? <Link to="/register">Создать аккаунт</Link>
          </p>
        </section>

        <aside className="auth-showcase" aria-label="Возможности личного кабинета">
          <p className="auth-showcase__brand">Muller's Firearms</p>
          <h2>Всё необходимое для точного выбора.</h2>
          <p>
            Сохраняйте товары, отслеживайте заказы и получайте персональные рекомендации
            в одном пространстве.
          </p>
          <div className="auth-showcase__features">
            <span>01</span><strong>Единый профиль</strong>
            <span>02</span><strong>История заказов</strong>
            <span>03</span><strong>AI-консультант</strong>
          </div>
        </aside>
      </div>
    </main>
  );
}
