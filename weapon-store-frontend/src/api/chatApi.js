import api from "./axios";

export const sendMessageToAI = async (message) => {
  const response = await api.post("/ai/chat", { message }, { timeout: 105000 });
  return response.data;
};

export const getChatHistory = async () => {
  const response = await api.get("/ai/history");
  return response.data;
};

export const clearChatHistory = async () => {
  await api.delete("/ai/history");
};
