const fieldLabels = {
  email: "Email",
  password: "Пароль",
  full_name: "Имя",
  phone: "Телефон",
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
