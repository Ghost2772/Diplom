import { useEffect, useState } from "react";
import { getProducts } from "../api/productsApi";
import { addToCart } from "../api/cartApi";

export default function CatalogPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getProducts()
      .then((data) => {
        console.log("PRODUCTS:", data);
        setProducts(Array.isArray(data) ? data : []);
      })
      .catch((error) => {
        console.error("PRODUCTS ERROR:", error);
        alert("Ошибка загрузки товаров");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const handleAddToCart = async (productId) => {
    try {
      await addToCart(productId, 1);
      alert("Товар добавлен в корзину");
    } catch (error) {
      console.error("ADD TO CART ERROR:", error);
      alert("Не удалось добавить товар в корзину");
    }
  };

  if (loading) {
    return (
      <div className="container page">
        <h2>Каталог</h2>
        <p>Загрузка товаров...</p>
      </div>
    );
  }

  return (
    <div className="container page">
      <h2>Каталог</h2>

      {products.length === 0 ? (
        <p>Товары не найдены.</p>
      ) : (
        products.map((p) => (
          <div
            key={p.id}
            style={{
              border: "1px solid #334155",
              padding: "16px",
              marginBottom: "16px",
              borderRadius: "10px",
              background: "#111827",
            }}
          >
            <h3>{p.name}</h3>
            <p>{p.description}</p>
            <p>Цена: {p.price}</p>
            <p>Остаток: {p.stock}</p>

            <button onClick={() => handleAddToCart(p.id)}>
              В корзину
            </button>
          </div>
        ))
      )}
    </div>
  );
}