import { useEffect, useState } from "react";
import { getMyOrders } from "../api/ordersApi";

const getStatusLabel = (status) => {
  switch (status) {
    case "created":
      return "Создан";
    case "processing":
      return "В обработке";
    case "completed":
      return "Завершён";
    case "cancelled":
      return "Отменён";
    default:
      return status;
  }
};

const getStatusColor = (status) => {
  switch (status) {
    case "created":
      return "#38bdf8";
    case "processing":
      return "#facc15";
    case "completed":
      return "#22c55e";
    case "cancelled":
      return "#ef4444";
    default:
      return "#94a3b8";
  }
};

export default function OrdersPage() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMyOrders()
      .then((data) => {
        console.log("MY ORDERS:", data);
        setOrders(Array.isArray(data) ? data : []);
      })
      .catch((error) => {
        console.error("ORDERS ERROR:", error);
        alert("Ошибка загрузки заказов");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="container page">
        <h2>Мои заказы</h2>
        <p>Загрузка заказов...</p>
      </div>
    );
  }

  return (
    <div className="container page">
      <h2>Мои заказы</h2>

      {orders.length === 0 ? (
        <p>У вас пока нет заказов.</p>
      ) : (
        orders.map((order) => (
          <div
            key={order.id}
            style={{
              border: "1px solid #334155",
              padding: "16px",
              marginBottom: "16px",
              borderRadius: "10px",
              background: "#111827",
            }}
          >
            <h3>Заказ #{order.id}</h3>

            {"status" in order && (
  <p style={{ color: getStatusColor(order.status) }}>
    Статус: {getStatusLabel(order.status)}
  </p>
)}
            {"total_price" in order && <p>Сумма: {order.total_price}</p>}
            {"created_at" in order && <p>Дата: {order.created_at}</p>}

            {order.items && Array.isArray(order.items) && order.items.length > 0 && (
              <div style={{ marginTop: "12px" }}>
                <h4>Товары:</h4>

                {order.items.map((item, index) => (
                  <div
                    key={item.id ?? index}
                    style={{
                      padding: "10px",
                      marginBottom: "10px",
                      border: "1px solid #1e293b",
                      borderRadius: "8px",
                    }}
                  >
                    <p>
                      <strong>
                        {item.product_name || item.product?.name || item.name || `Товар #${index + 1}`}
                      </strong>
                    </p>

                    {item.product?.description && (
                      <p>{item.product.description}</p>
                    )}

                    {"price" in item && <p>Цена: {item.price}</p>}
                    {"quantity" in item && <p>Количество: {item.quantity}</p>}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
}