import api from "./axios";

export const sendMessageToAI = async (message) => {
  const response = await api.post("/ai/chat", { message });
  return response.data;
};

export const getChatHistory = async () => {
  const response = await api.get("/ai/history");
  return response.data;
};