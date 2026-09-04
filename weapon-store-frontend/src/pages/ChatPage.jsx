import { useEffect, useRef, useState } from "react";
import { getChatHistory, sendMessageToAI } from "../api/chatApi";

const SUGGESTED_QUESTIONS = [
  "Как выбрать оптический прицел?",
  "Сравни модели для спортивной стрельбы",
  "Что учесть при выборе карабина?",
];

const messageTimeFormatter = new Intl.DateTimeFormat("ru-RU", {
  hour: "2-digit",
  minute: "2-digit",
});

const getMessageText = (message) =>
  message.message || message.content || message.answer || "";

const getMessageRole = (message) => {
  if (message.role) return message.role;
  if (message.is_user === true) return "user";
  if (message.is_user === false) return "assistant";
  return "assistant";
};

export default function ChatPage() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    let isMounted = true;

    getChatHistory()
      .then((data) => {
        if (!isMounted) return;

        if (Array.isArray(data)) {
          setMessages(data);
        } else if (Array.isArray(data?.messages)) {
          setMessages(data.messages);
        } else {
          setMessages([]);
        }
      })
      .catch(() => {
        if (isMounted) setMessages([]);
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, sending]);

  const handleSend = async (suggestedMessage) => {
    const currentMessage =
      typeof suggestedMessage === "string" ? suggestedMessage.trim() : message.trim();

    if (!currentMessage || sending) return;

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        message: currentMessage,
        created_at: new Date().toISOString(),
      },
    ]);
    setMessage("");
    setSending(true);

    try {
      const data = await sendMessageToAI(currentMessage);
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          message: data.answer,
          blocked: data.blocked,
          created_at: new Date().toISOString(),
        },
      ]);
    } catch {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          message: "Не удалось получить ответ. Проверьте подключение и попробуйте ещё раз.",
          blocked: false,
          created_at: new Date().toISOString(),
          failed: true,
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <main className="workspace-page chat-page">
      <div className="container workspace-layout workspace-layout--chat">
        <header className="workspace-heading workspace-heading--chat">
          <p className="workspace-heading__eyebrow">Интеллектуальный помощник</p>
          <h1>AI-консультант</h1>
          <p>Поможет сравнить характеристики и сориентироваться в каталоге.</p>
        </header>

        {loading ? (
          <div className="workspace-status">Загружаем историю диалога…</div>
        ) : (
          <section className="glass-panel chat-window" aria-label="Диалог с AI-консультантом">
            <header className="chat-window__header">
              <div className="chat-agent">
                <span className="chat-agent__avatar" aria-hidden="true">AI</span>
                <div>
                  <strong>Muller AI</strong>
                  <span className="chat-agent__status">
                    <span aria-hidden="true" />
                    Готов к диалогу
                  </span>
                </div>
              </div>
              <span className="chat-window__caption">Справочная консультация</span>
            </header>

            <div className="chat-messages" aria-live="polite">
              {messages.length === 0 ? (
                <div className="chat-welcome">
                  <span className="chat-welcome__mark" aria-hidden="true">AI</span>
                  <p className="workspace-heading__eyebrow">Начните диалог</p>
                  <h2>Чем могу помочь?</h2>
                  <p>Задайте свой вопрос или выберите один из готовых вариантов.</p>
                  <div className="chat-suggestions">
                    {SUGGESTED_QUESTIONS.map((question) => (
                      <button type="button" key={question} onClick={() => handleSend(question)}>
                        {question} <span aria-hidden="true">↗</span>
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                messages.map((chatMessage, index) => {
                  const role = getMessageRole(chatMessage);
                  const text = getMessageText(chatMessage);
                  const date = chatMessage.created_at
                    ? new Date(chatMessage.created_at)
                    : null;

                  return (
                    <article
                      className={`chat-message chat-message--${role}${
                        chatMessage.failed ? " chat-message--failed" : ""
                      }`}
                      key={chatMessage.id ?? `${role}-${index}`}
                    >
                      <span className="chat-message__avatar" aria-hidden="true">
                        {role === "user" ? "Вы" : "AI"}
                      </span>
                      <div className="chat-message__column">
                        <div className="chat-message__meta">
                          <strong>{role === "user" ? "Вы" : "Muller AI"}</strong>
                          {date && !Number.isNaN(date.getTime()) && (
                            <time dateTime={chatMessage.created_at}>
                              {messageTimeFormatter.format(date)}
                            </time>
                          )}
                        </div>
                        <div className="chat-message__bubble">
                          <p>{text}</p>
                          {chatMessage.blocked && (
                            <span className="chat-message__restriction">
                              Ответ ограничен правилами безопасности
                            </span>
                          )}
                        </div>
                      </div>
                    </article>
                  );
                })
              )}

              {sending && (
                <article className="chat-message chat-message--assistant">
                  <span className="chat-message__avatar" aria-hidden="true">AI</span>
                  <div className="chat-message__column">
                    <div className="chat-message__meta"><strong>Muller AI</strong></div>
                    <div className="chat-message__bubble chat-message__bubble--typing">
                      <span />
                      <span />
                      <span />
                    </div>
                  </div>
                </article>
              )}
              <div ref={messagesEndRef} />
            </div>

            <footer className="chat-composer">
              <div className="chat-composer__field">
                <textarea
                  rows="2"
                  value={message}
                  onChange={(event) => setMessage(event.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Напишите вопрос о товарах или характеристиках…"
                  maxLength={1500}
                  aria-label="Сообщение AI-консультанту"
                />
                <span>{message.length}/1500</span>
              </div>
              <button
                type="button"
                className="chat-composer__send"
                onClick={() => handleSend()}
                disabled={sending || !message.trim()}
                aria-label="Отправить сообщение"
              >
                <span aria-hidden="true">↑</span>
              </button>
              <p>
                Enter — отправить, Shift + Enter — новая строка. Ответы носят справочный характер.
              </p>
            </footer>
          </section>
        )}
      </div>
    </main>
  );
}
