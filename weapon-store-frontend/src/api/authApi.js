import api from "./axios";

export const getDemoConfig = async () => {
  const response = await api.get("/auth/demo");
  return response.data;
};

export const loginDemo = async () => {
  const response = await api.post("/auth/demo");
  return response.data;
};

export const registerUser = async (data) => {
  const response = await api.post("/auth/register", data);
  return response.data;
};

export const loginUser = async (formData) => {
  const response = await api.post("/auth/login", formData, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get("/users/me");
  return response.data;
};
