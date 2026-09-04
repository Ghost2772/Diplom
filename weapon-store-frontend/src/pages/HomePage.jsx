import { Link } from "react-router-dom";

export default function HomePage() {
  return (
    <div className="container page">
      <h1>Muller’s Firearms</h1>
      <p>Демонстрационный интернет-магазин с ИИ-консультантом.</p>
      <div className="home-actions">
        <Link to="/catalog" className="btn">
          Перейти в каталог
        </Link>
        <Link to="/chat" className="btn btn-secondary">
          Открыть AI-чат
        </Link>
      </div>
    </div>
  );
}
