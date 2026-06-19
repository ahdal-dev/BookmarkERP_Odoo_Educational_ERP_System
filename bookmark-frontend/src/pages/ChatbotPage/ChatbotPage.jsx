import { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import AppShell from '../../components/AppShell/AppShell';
import { chatbotStudentNav } from '../../config/navConfigs';
import { chatbotAPI } from '../../api/apiGateway';
import styles from './ChatbotPage.module.css';

/* ============================================================
   CHATBOT PAGE — Academic Assistant
   Streams-free structured chat with the FastAPI gateway, which
   proxies to the Academic Agent microservice. Renders Markdown
   (incl. GFM tables) for schedules and record summaries.
   ============================================================ */

const SUGGESTIONS = [
  'What is the schedule and instructor for course CS101?',
  'Do I have any holds on my account?',
  'Show me my weekly schedule.',
  'What courses am I currently registered for?',
];

const WELCOME = {
  role: 'assistant',
  content:
    "Hi! I'm your Academic Assistant. I can look up courses, check your holds, "
    + 'show your schedule and records, help you register or drop courses, file '
    + 'petitions, and estimate a GPA. What would you like to do?',
};

export default function ChatbotPage() {
  const [messages, setMessages] = useState([WELCOME]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const scrollRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, loading]);

  const send = async (text) => {
    const question = (text ?? input).trim();
    if (!question || loading) return;

    setError(null);
    setInput('');

    // History = the conversation so far (exclude the synthetic welcome message).
    const history = messages
      .filter((m) => m !== WELCOME)
      .map((m) => ({ role: m.role, content: m.content }));

    setMessages((prev) => [...prev, { role: 'user', content: question }]);
    setLoading(true);

    try {
      const data = await chatbotAPI.query(question, history);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.answer || 'Sorry, I had trouble answering that.',
          toolUsed: data.tool_used,
        },
      ]);
    } catch (err) {
      const detail = err?.response?.data?.detail || 'The assistant is unavailable right now. Please try again shortly.';
      setError(detail);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: detail, isError: true },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const onKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <AppShell navItems={chatbotStudentNav} logoVariant="stacked">
      <div className={styles.layout}>
        <div className={styles.breadcrumb}>STUDENT · AI ASSISTANT</div>

        <div className={styles.chatCard}>
          <header className={styles.header}>
            <div>
              <h2 className={styles.title}>Academic Assistant</h2>
              <p className={styles.subtitle}>Ask about courses, registration, petitions, holds, schedule, records, and GPA.</p>
            </div>
            <span className={styles.statusDot} aria-label="online" />
          </header>

          <div className={styles.messages} ref={scrollRef}>
            {messages.map((m, i) => (
              <div
                key={i}
                className={`${styles.row} ${m.role === 'user' ? styles.rowUser : styles.rowAssistant}`}
              >
                <div
                  className={[
                    styles.bubble,
                    m.role === 'user' ? styles.bubbleUser : styles.bubbleAssistant,
                    m.isError ? styles.bubbleError : '',
                  ].join(' ')}
                >
                  {m.role === 'user' ? (
                    <span>{m.content}</span>
                  ) : (
                    <div className={styles.md}>
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
                    </div>
                  )}
                  {m.toolUsed && (
                    <span className={styles.toolTag}>via {m.toolUsed}</span>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className={`${styles.row} ${styles.rowAssistant}`}>
                <div className={`${styles.bubble} ${styles.bubbleAssistant}`}>
                  <span className={styles.typing}>
                    <span /><span /><span />
                  </span>
                </div>
              </div>
            )}
          </div>

          {messages.length <= 1 && !loading && (
            <div className={styles.suggestions}>
              {SUGGESTIONS.map((s) => (
                <button key={s} className={styles.suggestion} onClick={() => send(s)}>
                  {s}
                </button>
              ))}
            </div>
          )}

          <div className={styles.composer}>
            <textarea
              ref={inputRef}
              className={styles.input}
              placeholder="Type your message…  (Enter to send, Shift+Enter for a new line)"
              value={input}
              rows={1}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              disabled={loading}
            />
            <button
              className={styles.sendBtn}
              onClick={() => send()}
              disabled={loading || !input.trim()}
              aria-label="Send"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4 20-7z"/></svg>
            </button>
          </div>
          {error && <div className={styles.errorBar}>{error}</div>}
        </div>
      </div>
    </AppShell>
  );
}
