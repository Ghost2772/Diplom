import { useEffect, useMemo, useState } from "react";
import { getCart, clearCart, removeCartItem } from "../api/cartApi";
import { createOrderFromCart } from "../api/ordersApi";

export default function CartPage() {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadCart = async () => {
    try {
      const data = await getCart();
      console.log("CART DATA:", data);
      setCart(data);
    } catch (error) {
      console.error("CART ERROR:", error);
      alert("Ошибка загрузки корзины");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCart();
  }, []);

  const items = useMemo(() => {
    if (!cart) return [];
    return cart.items || cart.cart_items || [];
  }, [cart]);

  const total = useMemo(() => {
    return items.reduce((sum, item) => {
      const price = item.product?.price ?? item.price ?? 0;
      const quantity = item.quantity ?? 1;
      return sum + price * quantity;
    }, 0);
  }, [items]);

  const handleCreateOrder = async () => {
    try {
      await createOrderFromCart();
      alert("Заказ оформлен");
      await loadCart();
    } catch (error) {
      console.error("CREATE ORDER ERROR:", error);
      alert("Ошибка оформления заказа");
    }
  };

  const handleClearCart = async () => {
    try {
      await clearCart();
      alert("Корзина очищена");
      await loadCart();
    } catch (error) {
      console.error("CLEAR CART ERROR:", error);
      alert("Ошибка очистки корзины");
    }
  };

  const handleRemoveItem = async (itemId) => {
    try {
      await removeCartItem(itemId);
      await loadCart();
    } catch (error) {
      console.error("REMOVE ITEM ERROR:", error);
      alert("Ошибка удаления товара");
    }
  };

  if (loading) {
    return (
      <div className="container page">
        <h2>Корзина</h2>
        <p>Загрузка корзины...</p>
      </div>
    );
  }

  return (
    <div className="container page">
      <h2>Корзина</h2>

      {items.length === 0 ? (
        <p>Корзина пуста.</p>
      ) : (
        <>
          {items.map((item, index) => {
            const product = item.product || {};
            const name = product.name || item.name || `Товар #${index + 1}`;
            const description = product.description || item.description || "";
            const price = product.price ?? item.price ?? 0;
            const quantity = item.quantity ?? 1;

            return (
              <div
                key={item.id ?? index}
                style={{
                  border: "1px solid #334155",
                  padding: "16px",
                  marginBottom: "16px",
                  borderRadius: "10px",
                  background: "#111827",
                }}
              >
                <h3>{name}</h3>
                {description && <p>{description}</p>}
                <p>Цена: {price}</p>
                <p>Количество: {quantity}</p>
                <p>Сумма: {price * quantity}</p>

                {item.id && (
                  <button onClick={() => handleRemoveItem(item.id)}>
                    Удалить
                  </button>
                )}
              </div>
            );
          })}

          <h3>Итого: {total}</h3>

          <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
            <button onClick={handleCreateOrder}>Оформить заказ</button>
            <button onClick={handleClearCart}>Очистить корзину</button>
          </div>
        </>
      )}
    </div>
  );
}