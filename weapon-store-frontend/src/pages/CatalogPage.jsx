import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getCategories } from "../api/productsApi";

const SMOOTHBORE_SLUG = "smoothbore-shotguns";

export default function CatalogPage() {
  const [category, setCategory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    getCategories()
      .then((categories) => {
        if (!isMounted) return;

        const smoothboreCategory = Array.isArray(categories)
          ? categories.find((item) => item.slug === SMOOTHBORE_SLUG)
          : null;

        setCategory(smoothboreCategory || null);
        if (!smoothboreCategory) {
          setError("Категория пока недоступна.");
        }
      })
      .catch(() => {
        if (isMounted) {
          setError("Не удалось загрузить каталог. Попробуйте обновить страницу.");
        }
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <main className="catalog-page">
      <div className="container catalog-layout">
        <header className="catalog-heading">
          <p className="catalog-heading__eyebrow">Muller's Firearms</p>
          <h1>Каталог</h1>
          <p>Выберите категорию, чтобы перейти к доступным моделям.</p>
        </header>

        {loading && <div className="catalog-status">Загружаем категории…</div>}
        {!loading && error && <div className="catalog-status catalog-status--error">{error}</div>}

        {!loading && category && (
          <section className="category-grid" aria-label="Категории товаров">
            <Link
              to={`/catalog/${category.slug}`}
              className="category-card"
              aria-label="Открыть категорию Гладкоствольное оружие"
            >
              <div className="category-card__content">
                <span className="category-card__number">Категория 01</span>
                <h2>Гладкоствольное оружие</h2>
                <p>
                  Помповые, самозарядные и классические модели для охоты и
                  спортивной стрельбы.
                </p>
                <span className="category-card__link">
                  Смотреть модели <span aria-hidden="true">↗</span>
                </span>
              </div>

              <div className="category-card__media" aria-hidden="true">
                <img
                  src="/images/categories/smoothbore.webp"
                  alt=""
                  width="1461"
                  height="980"
                />
              </div>
            </Link>
          </section>
        )}
      </div>
    </main>
  );
}
