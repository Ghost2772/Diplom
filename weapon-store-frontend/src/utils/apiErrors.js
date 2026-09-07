const fieldLabels = {
  email: "Email",
  password: "Пароль",
  full_name: "Имя",
  phone: "Телефон",
  name: "Название",
  sku: "Артикул",
  price: "Цена",
  old_price: "Старая цена",
  stock: "Остаток",
  category_id: "Категория",
  image_url: "Изображение",
  attributes: "Характеристики",
};

export function getApiErrorMessage(error, fallback) {
  const detail = error?.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail) && detail.length > 0) {
    const issue = detail[0];
    const field = issue?.loc?.at?.(-1);
    const label = fieldLabels[field];
    const message = issue?.msg;

    if (label && message) {
      return `${label}: ${message}`;
    }

    if (message) {
      return message;
    }
  }

  if (error?.code === "ECONNABORTED") {
    return "Сервер отвечает слишком долго. Попробуйте ещё раз.";
  }

  return fallback;
}
