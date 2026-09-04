import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getCurrentUser } from "../api/authApi";

const accountDateFormatter = new Intl.DateTimeFormat("ru-RU", {
  day: "numeric",
  month: "long",
  year: "numeric",
});

const getInitials = (user) => {
  const source = user?.full_name?.trim() || user?.email || "MF";
  const parts = source.split(/[\s@._-]+/).filter(Boolean);

  return parts
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");
};

export default function ProfilePage() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    getCurrentUser()
      .then((data) => {
        if (isMounted) setUser(data);
      })
      .catch(() => {
        if (isMounted) {
          setError("Не удалось загрузить данные профиля.");
        }
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const memberSince = user?.created_at
    ? accountDateFormatter.format(new Date(user.created_at))
    : "Дата не указана";

  return (
    <main className="workspace-page profile-page">
      <div className="container workspace-layout">
        <header className="workspace-heading">
          <p className="workspace-heading__eyebrow">Личный кабинет</p>
          <h1>Профиль</h1>
          <p>Данные учётной записи и быстрый доступ к основным разделам.</p>
        </header>

        {loading && <div className="workspace-status">Загружаем профиль…</div>}
        {!loading && error && (
          <div className="workspace-status workspace-status--error">{error}</div>
        )}

        {!loading && user && (
          <div className="profile-grid">
            <section className="glass-panel profile-card">
              <div className="profile-card__identity">
                <div className="profile-avatar" aria-hidden="true">
                  {getInitials(user)}
                </div>
                <div>
                  <p className="profile-card__label">Владелец аккаунта</p>
                  <h2>{user.full_name || "Пользователь Muller's Firearms"}</h2>
                  <span className="profile-status">
                    <span aria-hidden="true" />
                    Аккаунт активен
                  </span>
                </div>
              </div>

              <dl className="profile-details">
                <div>
                  <dt>Электронная почта</dt>
                  <dd>{user.email}</dd>
                </div>
                <div>
                  <dt>Телефон</dt>
                  <dd>{user.phone || "Не указан"}</dd>
                </div>
                <div>
                  <dt>Дата регистрации</dt>
                  <dd>{memberSince}</dd>
                </div>
                <div>
                  <dt>Уровень доступа</dt>
                  <dd>{user.is_admin ? "Администратор" : "Клиент"}</dd>
                </div>
              </dl>
            </section>

            <aside className="profile-shortcuts" aria-label="Быстрые действия">
              <Link to="/orders" className="glass-panel profile-shortcut">
                <span className="profile-shortcut__index">01</span>
                <div>
                  <strong>Мои заказы</strong>
                  <span>История и статусы заказов</span>
                </div>
                <span className="profile-shortcut__arrow" aria-hidden="true">↗</span>
              </Link>

              <Link to="/cart" className="glass-panel profile-shortcut">
                <span className="profile-shortcut__index">02</span>
                <div>
                  <strong>Корзина</strong>
                  <span>Выбранные позиции</span>
                </div>
                <span className="profile-shortcut__arrow" aria-hidden="true">↗</span>
              </Link>

              <Link to="/chat" className="glass-panel profile-shortcut">
                <span className="profile-shortcut__index">03</span>
                <div>
                  <strong>AI-консультант</strong>
                  <span>Помощь с выбором товаров</span>
                </div>
                <span className="profile-shortcut__arrow" aria-hidden="true">↗</span>
              </Link>
            </aside>
          </div>
        )}
      </div>
    </main>
  );
}
