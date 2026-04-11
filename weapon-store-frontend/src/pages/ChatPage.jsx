import { useEffect, useState } from "react";
import { getChatHistory, sendMessageToAI } from "../api/chatApi";

export default function ChatPage() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    getChatHistory()
      .then((data) => {
        console.log("CHAT HISTORY:", data);

        if (Array.isArray(data)) {
          setMessages(data);
        } else if (Array.isArray(data?.messages)) {
          setMessages(data.messages);
        } else {
          setMessages([]);
        }
      })
      .catch((error) => {
        console.error("CHAT HISTORY ERROR:", error);
        setMessages([]);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const handleSend = async () => {
    if (!message.trim()) return;

    const userMessage = {
      role: "user",
      message: message,
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentMessage = message;
    setMessage("");
    setSending(true);

    try {
      const data = await sendMessageToAI(currentMessage);
      console.log("AI RESPONSE:", data);

      const aiMessage = {
        role: "assistant",
        message: data.answer,
        blocked: data.blocked,
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error("AI CHAT ERROR:", error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          message: "Ошибка при обращении к AI-консультанту.",
          blocked: false,
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const getMessageText = (msg) => {
    return (
      msg.message ||
      msg.content ||
      msg.answer ||
      ""
    );
  };

  const getMessageRole = (msg) => {
    if (msg.role) return msg.role;
    if (msg.is_user === true) return "user";
    if (msg.is_user === false) return "assistant";
    return "assistant";
  };

  if (loading) {
    return (
      <div className="container page">
        <h2>AI-консультант</h2>
        <p>Загрузка истории чата...</p>
      </div>
    );
  }

  return (
    <div className="container page">
      <h2>AI-консультант</h2>

      <div
        style={{
          border: "1px solid #334155",
          borderRadius: "12px",
          padding: "16px",
          background: "#111827",
          minHeight: "350px",
          marginBottom: "16px",
          display: "flex",
          flexDirection: "column",
          gap: "12px",
        }}
      >
        {messages.length === 0 ? (
          <p style={{ color: "#94a3b8" }}>
            История пуста. Задай первый вопрос.
          </p>
        ) : (
          messages.map((msg, index) => {
            const role = getMessageRole(msg);
            const text = getMessageText(msg);

            return (
              <div
                key={index}
                style={{
                  alignSelf: role === "user" ? "flex-end" : "flex-start",
                  maxWidth: "75%",
                  padding: "12px 14px",
                  borderRadius: "12px",
                  background: role === "user" ? "#2563eb" : "#1e293b",
                  color: "#fff",
                  whiteSpace: "pre-wrap",
                }}
              >
                <div
                  style={{
                    fontSize: "12px",
                    opacity: 0.8,
                    marginBottom: "6px",
                  }}
                >
                  {role === "user" ? "Вы" : "AI-консультант"}
                </div>

                <div>{text}</div>

                {msg.blocked && (
                  <div style={{ marginTop: "8px", color: "#fca5a5", fontSize: "12px" }}>
                    Ответ помечен как ограниченный
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      <div style={{ display: "flex", gap: "12px", alignItems: "flex-start" }}>
        <textarea
          rows="4"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Например: Посоветуй полуавтоматическое ружьё для охоты"
          style={{
            flex: 1,
            padding: "12px",
            borderRadius: "10px",
            border: "1px solid #334155",
            background: "#0f172a",
            color: "#fff",
            resize: "vertical",
          }}
        />

        <button
          onClick={handleSend}
          disabled={sending || !message.trim()}
          style={{
            border: "none",
            background: sending ? "#475569" : "#2563eb",
            color: "#fff",
            padding: "12px 18px",
            borderRadius: "10px",
            minWidth: "120px",
          }}
        >
          {sending ? "Отправка..." : "Отправить"}
        </button>
      </div>
    </div>
  );
}