import { Link } from "react-router-dom";

export default function HomePage() {
  return (
    <main className="home-hero">
      <div className="home-hero__content">
        <h1 className="home-hero__title">
          Вооружение — залог безопасности
        </h1>

        <div className="home-hero__actions">
          <Link to="/catalog" className="home-hero__button home-hero__button--primary">
            Перейти в каталог
          </Link>
          <Link to="/chat" className="home-hero__button home-hero__button--secondary">
            Открыть AI-чат
          </Link>
        </div>
      </div>
    </main>
  );
}
