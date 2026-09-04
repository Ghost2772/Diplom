import { Link } from "react-router-dom";

export default function HomePage() {
  return (
    <main className="home-hero">
      <div className="home-hero__content">
        <section className="home-hero__panel">
          <div className="home-hero__panel-glow" aria-hidden="true" />

          <div className="home-hero__copy">
            <p className="home-hero__eyebrow">Muller's Firearms / с 2026 года</p>
            <h1 className="home-hero__title">
              Вооружение — залог безопасности
            </h1>
            <p className="home-hero__description">
              Каталог охотничьего снаряжения с интеллектуальным помощником,
              который поможет сравнить характеристики и подобрать подходящую модель.
            </p>

            <div className="home-hero__actions">
              <Link
                to="/catalog"
                className="home-hero__button home-hero__button--primary"
              >
                Перейти в каталог <span aria-hidden="true">↗</span>
              </Link>
              <Link
                to="/chat"
                className="home-hero__button home-hero__button--secondary"
              >
                Открыть AI-чат
              </Link>
            </div>
          </div>

          <div className="home-hero__features" aria-label="Возможности магазина">
            <div>
              <span>01</span>
              <strong>Каталог</strong>
              <p>Категории и характеристики</p>
            </div>
            <div>
              <span>02</span>
              <strong>AI-подбор</strong>
              <p>Помощь в сравнении моделей</p>
            </div>
            <div>
              <span>03</span>
              <strong>Личный кабинет</strong>
              <p>Корзина и история заказов</p>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
