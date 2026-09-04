import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerUser } from "../api/authApi";
import { getApiErrorMessage } from "../utils/apiErrors";

const initialForm = {
  full_name: "",
  email: "",
  phone: "",
  password: "",
  confirmPassword: "",
};

export default function RegisterPage() {
  const [form, setForm] = useState(initialForm);
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const updateField = (field) => (event) => {
    setForm((current) => ({ ...current, [field]: event.target.value }));
    setError("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (form.password !== form.confirmPassword) {
      setError("Пароли не совпадают.");
      return;
    }

    if (form.password.length < 8) {
      setError("Пароль должен содержать не менее 8 символов.");
      return;
    }

    setSubmitting(true);

    try {
      await registerUser({
        full_name: form.full_name.trim(),
        email: form.email.trim(),
        phone: form.phone.trim() || null,
        password: form.password,
      });
      navigate("/login", { replace: true, state: { registered: true } });
    } catch (requestError) {
      setError(
        getApiErrorMessage(
          requestError,
          "Не удалось создать аккаунт. Проверьте введённые данные.",
        ),
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="auth-page auth-page--register">
      <div className="container auth-layout">
        <section
          className="glass-panel auth-card auth-card--register"
          aria-labelledby="register-title"
        >
          <div className="auth-card__intro">
            <p className="auth-eyebrow">Новый аккаунт</p>
            <h1 id="register-title">Регистрация</h1>
            <p>Создайте профиль для доступа к корзине, заказам и AI-консультанту.</p>
          </div>

          {error && (
            <div className="auth-notice auth-notice--error" role="alert">
              <span aria-hidden="true">!</span>
              {error}
            </div>
          )}

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="auth-form__grid">
              <label className="auth-field">
                <span>Имя</span>
                <input
                  type="text"
                  name="full_name"
                  value={form.full_name}
                  onChange={updateField("full_name")}
                  placeholder="Александр Абрамов"
                  autoComplete="name"
                  minLength="2"
                  maxLength="120"
                  required
                />
              </label>

              <label className="auth-field">
                <span>Email</span>
                <input
                  type="email"
                  name="email"
                  value={form.email}
                  onChange={updateField("email")}
                  placeholder="you@example.com"
                  autoComplete="email"
                  required
                />
              </label>

              <label className="auth-field auth-field--wide">
                <span>Телефон <small>необязательно</small></span>
                <input
                  type="tel"
                  name="phone"
                  value={form.phone}
                  onChange={updateField("phone")}
                  placeholder="+7 999 000-00-00"
                  autoComplete="tel"
                  minLength="7"
                  maxLength="32"
                />
              </label>

              <div className="auth-field">
                <label htmlFor="register-password">Пароль</label>
                <span className="auth-field__control">
                  <input
                    id="register-password"
                    type={showPassword ? "text" : "password"}
                    name="password"
                    value={form.password}
                    onChange={updateField("password")}
                    placeholder="Минимум 8 символов"
                    autoComplete="new-password"
                    minLength="8"
                    maxLength="64"
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

              <label className="auth-field">
                <span>Повторите пароль</span>
                <input
                  type={showPassword ? "text" : "password"}
                  name="confirmPassword"
                  value={form.confirmPassword}
                  onChange={updateField("confirmPassword")}
                  placeholder="Повторите пароль"
                  autoComplete="new-password"
                  minLength="8"
                  maxLength="64"
                  required
                />
              </label>
            </div>

            <p className="auth-form__hint">
              Нажимая кнопку, вы подтверждаете согласие на обработку данных в рамках
              демонстрационного проекта.
            </p>

            <button className="auth-submit" type="submit" disabled={submitting}>
              <span>{submitting ? "Создаём аккаунт..." : "Создать аккаунт"}</span>
              {!submitting && <span className="auth-submit__arrow" aria-hidden="true">↗</span>}
            </button>
          </form>

          <p className="auth-card__footer">
            Уже зарегистрированы? <Link to="/login">Войти</Link>
          </p>
        </section>

        <aside className="auth-showcase" aria-label="Преимущества регистрации">
          <p className="auth-showcase__brand">Muller's Firearms</p>
          <h2>Персональный сервис с первого визита.</h2>
          <p>
            Соберите подборку, оформите демонстрационный заказ и продолжите диалог с
            консультантом в любое время.
          </p>
          <div className="auth-showcase__features">
            <span>01</span><strong>Быстрый доступ</strong>
            <span>02</span><strong>Сохранённая корзина</strong>
            <span>03</span><strong>Помощь в выборе</strong>
          </div>
        </aside>
      </div>
    </main>
  );
}
