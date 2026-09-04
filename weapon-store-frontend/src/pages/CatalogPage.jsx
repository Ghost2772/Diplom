import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getCategories } from "../api/productsApi";

const CATEGORY_CARDS = [
  {
    slug: "smoothbore-shotguns",
    number: "01",
    title: "Гладкоствольное оружие",
    description:
      "Помповые, самозарядные и классические модели для охоты и спортивной стрельбы.",
    image: "/images/categories/smoothbore.webp",
    imageWidth: 1461,
    imageHeight: 980,
    variant: "smoothbore",
  },
  {
    slug: "rifled-firearms",
    number: "02",
    title: "Нарезное оружие",
    description:
      "Карабины и винтовки с высокой точностью для охотничьих и спортивных задач.",
    image: "/images/categories/rifled.webp",
    imageWidth: 852,
    imageHeight: 657,
    variant: "rifled",
  },
  {
    slug: "ammunition-and-gear",
    number: "03",
    title: "Амуниция",
    description:
      "Боеприпасы, экипировка и снаряжение, подобранные под разные сценарии использования.",
    image: "/images/categories/ammunition.webp",
    imageWidth: 1320,
    imageHeight: 813,
    variant: "ammunition",
  },
  {
    slug: "optics",
    number: "04",
    title: "Оптические прицелы",
    description:
      "Оптика для точного наведения и уверенного наблюдения на разных дистанциях.",
    image: "/images/categories/optics.webp",
    imageWidth: 379,
    imageHeight: 362,
    variant: "optics",
  },
];

export default function CatalogPage() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    getCategories()
      .then((categories) => {
        if (!isMounted) return;

        const loadedCategories = Array.isArray(categories) ? categories : [];
        setCategories(loadedCategories);

        if (loadedCategories.length === 0) {
          setError("Категории пока недоступны.");
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

  const availableSlugs = new Set(categories.map((category) => category.slug));
  const availableCards = CATEGORY_CARDS.filter((card) => availableSlugs.has(card.slug));

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

        {!loading && availableCards.length > 0 && (
          <section className="category-grid" aria-label="Категории товаров">
            {availableCards.map((card, index) => (
              <Link
                to={`/catalog/${card.slug}`}
                className={`category-card category-card--${card.variant}`}
                aria-label={`Открыть категорию ${card.title}`}
                key={card.slug}
                style={{ "--card-delay": `${170 + index * 110}ms` }}
              >
                <div className="category-card__content">
                  <span className="category-card__number">Категория {card.number}</span>
                  <h2>{card.title}</h2>
                  <p>{card.description}</p>
                  <span className="category-card__link">
                    Смотреть модели <span aria-hidden="true">↗</span>
                  </span>
                </div>

                <div className="category-card__media" aria-hidden="true">
                  <img
                    src={card.image}
                    alt=""
                    width={card.imageWidth}
                    height={card.imageHeight}
                  />
                </div>
              </Link>
            ))}
          </section>
        )}
      </div>
    </main>
  );
}
