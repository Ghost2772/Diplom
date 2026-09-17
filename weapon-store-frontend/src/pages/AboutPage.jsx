import { useEffect } from "react";
import { Link } from "react-router-dom";
import DemoLogin from "../components/DemoLogin";
import { useAuth } from "../context/authContext";

const REPOSITORY = "https://github.com/Ghost2772/Diplom";
const SOURCE = `${REPOSITORY}/blob/portfolio-rework`;

const features = [
  {
    number: "01",
    title: "Каталог и товары",
    description: "Категории, отдельные страницы товаров, фотографии и характеристики из API",
    tags: ["React Router", "REST API"],
    to: "/catalog",
    action: "Посмотреть каталог",
  },
  {
    number: "02",
    title: "Личный кабинет",
    description: "Профиль, корзина и история учебных заказов с составом, стоимостью и статусами",
    tags: ["JWT", "SQLAlchemy"],
    to: "/orders",
    action: "Открыть заказы",
  },
  {
    number: "03",
    title: "Администрирование",
    description: "Пользователи, управление заказами и редактор товаров с загрузкой фотографий",
    tags: ["Роли доступа", "Валидация"],
    source: "weapon-store-frontend/src/components/AdminProductsPanel.jsx",
    action: "Код редактора товаров",
  },
  {
    number: "04",
    title: "AI-консультант",
    description: "Каталог и история переписки передаются в GigaChat, личный диалог можно очистить",
    tags: ["GigaChat API", "Async HTTP"],
    to: "/chat",
    action: "Открыть чат",
  },
];

const decisions = [
  {
    title: "Отдельная демо-сессия для каждого посетителя",
    text: "Сервер создаёт временный аккаунт с собственной корзиной и примерами заказов. Срок действия проверяется вместе с токеном, а истёкшие демо-данные очищаются при следующем демо-входе с небольшим запасом времени для текущих запросов",
    source: "weapon-store-backend/app/services/demo.py",
    test: "weapon-store-backend/tests/test_demo_login.py",
  },
  {
    title: "Заказ сохраняет данные на момент оформления",
    text: "Название, артикул и цена записываются в позиции заказа отдельно от карточки товара. Последующее редактирование каталога не меняет состав и стоимость уже оформленного заказа",
    source: "weapon-store-backend/app/models/order_item.py",
    test: "weapon-store-backend/tests/test_admin_products_and_chat.py",
  },
  {
    title: "Очистка чата учитывает ответ, который ещё готовится",
    text: "Перед сохранением ответа сервер проверяет, осталось ли исходное сообщение. Если пользователь очистил диалог в другой вкладке, запоздавший ответ не появляется в истории заново",
    source: "weapon-store-backend/app/ai/ai_service.py",
    test: "weapon-store-backend/tests/test_admin_products_and_chat.py",
  },
];

function SourceLink({ path, children, className = "about-text-link" }) {
  return (
    <a href={`${SOURCE}/${path}`} target="_blank" rel="noopener noreferrer" className={className}>
      {children} <span aria-hidden="true">↗</span>
    </a>
  );
}

export default function AboutPage() {
  const { isAuthenticated, demoConfig, user } = useAuth();

  useEffect(() => {
    const previousTitle = document.title;
    document.title = "О проекте — Muller's Firearms";
    const target = document.getElementById(window.location.hash.slice(1));
    if (target) target.scrollIntoView();
    else window.scrollTo(0, 0);
    return () => { document.title = previousTitle; };
  }, []);

  return (
    <main className="workspace-page about-page">
      <div className="container workspace-layout about-layout">
        <header className="about-intro">
          <div className="workspace-heading about-intro__heading">
            <p className="workspace-heading__eyebrow">Full-stack · Проект для портфолио</p>
            <h1>О проекте</h1>
            <p className="about-intro__name">Muller's Firearms</p>
            <p>
              Учебное веб-приложение, которое объединяет каталог, личный кабинет,
              административную панель и AI-консультанта
            </p>
            <div className="about-actions">
              <a className="workspace-primary-button" href={`${REPOSITORY}/tree/portfolio-rework`}
                target="_blank" rel="noopener noreferrer">
                Исходный код на GitHub <span aria-hidden="true">↗</span>
              </a>
              <a className="about-text-link" href="#tour">Как посмотреть демо <span aria-hidden="true">↓</span></a>
            </div>
          </div>

          <aside className="glass-panel about-passport" aria-label="Кратко о проекте">
            <p className="about-kicker">От задачи до приложения</p>
            <h2>Полный цикл разработки</h2>
            <p>Проект вырос из дипломной работы по направлению 09.03.02</p>
            <dl>
              <div><dt>Интерфейс</dt><dd>React · Vite</dd></div>
              <div><dt>Сервер</dt><dd>Python · FastAPI</dd></div>
              <div><dt>Данные</dt><dd>PostgreSQL · Alembic</dd></div>
              <div><dt>Запуск и проверки</dt><dd>Docker · GitHub Actions</dd></div>
            </dl>
            <p className="about-passport__note">Каталог, цены и заказы используются для демонстрации навыков</p>
          </aside>
        </header>

        <nav className="about-navigation" aria-label="Разделы о проекте">
          <a href="#features">Возможности</a>
          <a href="#architecture">Архитектура</a>
          <a href="#decisions">Технические решения</a>
          <a href="#quality">Проверки</a>
        </nav>

        <section className="about-section" id="features" aria-labelledby="features-title">
          <div className="about-section__heading">
            <h2 className="about-kicker" id="features-title">01 / Возможности</h2>
          </div>
          <div className="about-features">
            {features.map((feature) => (
              <article key={feature.number} className="glass-panel about-feature">
                <span className="about-feature__number" aria-hidden="true">{feature.number}</span>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
                <ul className="about-tags" aria-label="Технологии и подходы">
                  {feature.tags.map((tag) => <li key={tag}>{tag}</li>)}
                </ul>
                {feature.to ? (
                  <Link className="about-text-link" to={feature.to}>
                    {feature.action} <span aria-hidden="true">↗</span>
                  </Link>
                ) : (
                  <SourceLink path={feature.source}>{feature.action}</SourceLink>
                )}
              </article>
            ))}
          </div>
          <p className="about-section__note">
            Административные действия доступны владельцу проекта, ответы AI зависят от настройки GigaChat
          </p>
        </section>

        <section className="about-section" id="architecture" aria-labelledby="architecture-title">
          <div className="about-section__heading">
            <h2 className="about-kicker" id="architecture-title">02 / Архитектура</h2>
          </div>
          <div className="glass-panel about-system">
            <figure className="about-diagram" aria-labelledby="architecture-caption">
              <div className="about-diagram__node about-diagram__node--client">
                <span>Интерфейс</span><strong>React</strong><small>Страницы, формы и навигация</small>
              </div>
              <div className="about-diagram__connector"><span>/api · Nginx</span><b aria-hidden="true">↓</b></div>
              <div className="about-diagram__node about-diagram__node--api">
                <span>Сервер приложения</span><strong>FastAPI</strong><small>Авторизация, данные и бизнес-логика</small>
              </div>
              <svg className="about-diagram__branches" viewBox="0 0 400 40" preserveAspectRatio="none" aria-hidden="true">
                <path d="M200 0V20M100 40V20H300V40" />
              </svg>
              <div className="about-diagram__outputs">
                <div className="about-diagram__node">
                  <span>База данных</span><strong>PostgreSQL</strong><small>SQLAlchemy · Alembic</small>
                </div>
                <div className="about-diagram__node">
                  <span>Внешний API</span><strong>GigaChat</strong><small>Контекст каталога и диалога</small>
                </div>
              </div>
              <figcaption id="architecture-caption">
                Браузер обращается к серверу, сервер работает с базой данных и API модели
              </figcaption>
            </figure>
            <div className="about-system__details">
              <h3>Отдельная ответственность каждого слоя</h3>
              <dl>
                <div>
                  <dt>React + React Router + Axios</dt>
                  <dd>Интерфейс, переходы между страницами, загрузка данных и обратная связь в формах</dd>
                </div>
                <div>
                  <dt>FastAPI + Pydantic</dt>
                  <dd>REST API, проверка входных данных, JWT-аутентификация и серверная проверка роли</dd>
                </div>
                <div>
                  <dt>SQLAlchemy Async + PostgreSQL</dt>
                  <dd>Связи пользователей, корзин, заказов и сообщений, ограничения целостности данных</dd>
                </div>
                <div>
                  <dt>Docker Compose + Nginx</dt>
                  <dd>Совместный запуск сервисов, проксирование API и хранение файлов в отдельном томе</dd>
                </div>
              </dl>
              <SourceLink path="README.md">Устройство и запуск проекта</SourceLink>
            </div>
          </div>
        </section>

        <section className="about-section" id="decisions" aria-labelledby="decisions-title">
          <div className="about-section__heading">
            <h2 className="about-kicker" id="decisions-title">03 / Технические решения</h2>
          </div>
          <div className="about-decisions">
            {decisions.map((decision, index) => (
              <details key={decision.title} className="glass-panel about-decision" open={index === 0}>
                <summary>{decision.title}<span aria-hidden="true">+</span></summary>
                <div className="about-decision__body">
                  <p>{decision.text}</p>
                  <div className="about-actions">
                    <SourceLink path={decision.source}>Реализация</SourceLink>
                    <SourceLink path={decision.test}>Тесты сценария</SourceLink>
                  </div>
                </div>
              </details>
            ))}
          </div>
        </section>

        <section className="about-section" id="quality" aria-labelledby="quality-title">
          <div className="about-section__heading">
            <h2 className="about-kicker" id="quality-title">04 / Проверки</h2>
          </div>
          <div className="about-quality">
            <article>
              <h3>Сценарии API</h3>
              <p>Авторизация, права доступа, заказы, редактор товаров, загрузка изображений и изоляция демо</p>
              <SourceLink path="weapon-store-backend/tests/test_user_flow.py">Примеры pytest</SourceLink>
            </article>
            <article>
              <h3>Автоматические проверки</h3>
              <p>Ruff, ESLint, тесты backend, сборка frontend и применение миграций в GitHub Actions</p>
              <SourceLink path=".github/workflows/ci.yml">Конфигурация CI</SourceLink>
            </article>
            <article>
              <h3>Запуск из репозитория</h3>
              <p>Docker Compose запускает базу, API и frontend, применяет миграции и подготавливает учебный каталог</p>
              <SourceLink path="docker-compose.yml">Конфигурация запуска</SourceLink>
            </article>
          </div>
        </section>

        <section className="glass-panel about-tour" id="tour" aria-labelledby="tour-title">
          <div>
            <p className="about-kicker">Попробуйте сами</p>
            <h2 id="tour-title">Короткий маршрут знакомства</h2>
            <ol className="about-tour__steps">
              <li><Link to="/catalog">Каталог</Link><span>Откройте категорию и страницу товара</span></li>
              <li><Link to="/cart">Корзина</Link><span>Добавьте позицию и оформите учебный заказ</span></li>
              <li><Link to="/orders">Мои заказы</Link><span>Посмотрите состав, стоимость и статусы</span></li>
              <li><Link to="/chat">AI-чат</Link><span>Задайте вопрос о каталоге и попробуйте очистку истории</span></li>
            </ol>
          </div>
          <div className="about-tour__entry">
            {isAuthenticated ? (
              <>
                <p className="about-kicker">{user?.is_demo ? "Демо-сессия открыта" : "Вы уже вошли"}</p>
                <h3>Продолжите знакомство</h3>
                <p>Профиль и основные разделы доступны через меню</p>
                <Link className="workspace-primary-button" to="/profile">Перейти в профиль <span aria-hidden="true">↗</span></Link>
              </>
            ) : demoConfig?.enabled ? (
              <DemoLogin />
            ) : (
              <>
                <h3>Откройте личный кабинет</h3>
                <p>Вход доступен на отдельной странице, каталог можно посмотреть сразу</p>
                <Link className="workspace-primary-button" to="/login">Перейти ко входу <span aria-hidden="true">↗</span></Link>
              </>
            )}
            <p className="about-tour__note">Это учебная демонстрация без реальной оплаты и доставки</p>
          </div>
        </section>

        <footer className="about-footer">
          <span>Muller's Firearms · Портфолио full-stack разработки</span>
          <SourceLink path="README.md">Документация проекта</SourceLink>
        </footer>
      </div>
    </main>
  );
}
