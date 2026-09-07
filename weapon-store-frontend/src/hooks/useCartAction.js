import { useEffect, useRef, useState } from "react";
import { addToCart } from "../api/cartApi";
import { getApiErrorMessage } from "../utils/apiErrors";

export function useCartAction() {
  const [notice, setNotice] = useState(null);
  const [addingProductId, setAddingProductId] = useState(null);
  const pending = useRef(false);

  useEffect(() => {
    if (!notice) return undefined;
    const timeoutId = window.setTimeout(() => setNotice(null), 4500);
    return () => window.clearTimeout(timeoutId);
  }, [notice]);

  const addProduct = async (product) => {
    if (pending.current || product.stock <= 0 || !product.is_active) return;
    pending.current = true;
    setAddingProductId(product.id);

    try {
      await addToCart(product.id, 1);
      setNotice({ type: "success", title: "Добавлено в корзину", text: product.name });
    } catch (error) {
      const requiresLogin = error.response?.status === 401;
      setNotice({
        type: "error",
        title: requiresLogin ? "Требуется авторизация" : "Не удалось добавить товар",
        text: requiresLogin
          ? "Войдите в аккаунт и повторите действие."
          : getApiErrorMessage(error, "Проверьте подключение и попробуйте ещё раз."),
        requiresLogin,
      });
    } finally {
      pending.current = false;
      setAddingProductId(null);
    }
  };

  return { notice, addingProductId, addProduct, dismissNotice: () => setNotice(null) };
}
