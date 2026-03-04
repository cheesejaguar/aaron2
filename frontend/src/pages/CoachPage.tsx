import { useState, useRef, useEffect } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Bot, Send, Sparkles, MessageCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { coachApi } from "@/api/coach";
import type { ChatMessage } from "@/types";

const INSIGHT_PRIORITY_BORDER: Record<string, string> = {
  high: "rgb(239 68 68 / 0.5)",
  medium: "rgb(245 158 11 / 0.4)",
  low: "rgb(16 185 129 / 0.3)",
};

const QUICK_QUESTIONS = [
  "What should I eat to lower my blood pressure?",
  "How much sodium should I have daily?",
  "Suggest a heart-healthy snack",
  "Review my nutrition today",
];

export function CoachPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<string>();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { data: insights } = useQuery({
    queryKey: ["coach", "insights"],
    queryFn: coachApi.insights,
  });

  const chatMutation = useMutation({
    mutationFn: coachApi.chat,
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.reply },
      ]);
      setConversationId(data.conversation_id);
    },
  });

  const handleSend = (text?: string) => {
    const msg = (text || input).trim();
    if (!msg) return;
    setMessages((prev) => [...prev, { role: "user", content: msg }]);
    setInput("");
    chatMutation.mutate({ message: msg, conversation_id: conversationId });
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, chatMutation.isPending]);

  const hasMessages = messages.length > 0;

  return (
    <div className="flex flex-col h-[calc(100vh-2rem)] max-w-[1400px]">
      {/* Header — compact */}
      <div className="shrink-0 flex items-center justify-between gap-4 mb-4">
        <div className="flex items-center gap-3">
          <div
            className="h-9 w-9 rounded-xl flex items-center justify-center"
            style={{ background: "rgb(167 139 250 / 0.1)" }}
          >
            <Bot className="h-4.5 w-4.5" style={{ color: "rgb(167 139 250)" }} />
          </div>
          <div>
            <h1
              className="text-2xl font-bold tracking-tight leading-none"
              style={{ fontFamily: "'DM Serif Display', serif" }}
            >
              AI Health Coach
            </h1>
          </div>
        </div>
      </div>

      {/* Main content — fills remaining space */}
      <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-5 gap-4">
        {/* Insights panel — 2 cols on desktop, horizontal scroll on mobile */}
        <div className="lg:col-span-2 flex flex-col min-h-0">
          {/* Insights */}
          <div
            className="meal-card-enter rounded-2xl border border-border/40 p-5 flex flex-col min-h-0 lg:flex-1"
            style={{
              background:
                "linear-gradient(165deg, rgb(167 139 250 / 0.04) 0%, transparent 40%)",
            }}
          >
            <div className="flex items-center gap-2 mb-4 shrink-0">
              <Sparkles className="h-3.5 w-3.5" style={{ color: "rgb(167 139 250 / 0.6)" }} />
              <h2
                className="text-[11px] font-semibold uppercase tracking-widest"
                style={{ color: "rgb(167 139 250 / 0.6)" }}
              >
                Insights
              </h2>
            </div>

            <div className="flex-1 overflow-y-auto min-h-0 space-y-2.5 pr-1 scrollbar-thin">
              {insights?.insights && insights.insights.length > 0 ? (
                insights.insights.map((insight, i) => (
                  <div
                    key={i}
                    className="meal-card-enter rounded-xl p-3.5 bg-muted/20 border-l-2"
                    style={{
                      animationDelay: `${0.1 + i * 0.06}s`,
                      borderLeftColor:
                        INSIGHT_PRIORITY_BORDER[insight.priority] || "rgb(16 185 129 / 0.3)",
                    }}
                  >
                    <div className="flex items-center gap-2 mb-1.5">
                      <span
                        className="text-[9px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded-full"
                        style={{
                          color: "rgb(167 139 250 / 0.7)",
                          background: "rgb(167 139 250 / 0.08)",
                        }}
                      >
                        {insight.category}
                      </span>
                    </div>
                    <p className="text-sm font-medium leading-snug mb-1">
                      {insight.title}
                    </p>
                    <p className="text-xs text-muted-foreground/50 font-light leading-relaxed">
                      {insight.description}
                    </p>
                  </div>
                ))
              ) : (
                <div className="py-8 text-center">
                  <Sparkles className="h-6 w-6 text-muted-foreground/20 mx-auto mb-2" />
                  <p className="text-xs text-muted-foreground/40 font-light">
                    Log more data to get personalized insights
                  </p>
                </div>
              )}
            </div>

            {/* Quick questions */}
            <div className="shrink-0 mt-4 pt-4 border-t border-border/30">
              <div className="flex items-center gap-2 mb-3">
                <MessageCircle
                  className="h-3 w-3"
                  style={{ color: "rgb(167 139 250 / 0.4)" }}
                />
                <span className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/40">
                  Quick questions
                </span>
              </div>
              <div className="space-y-1.5">
                {QUICK_QUESTIONS.map((q) => (
                  <button
                    key={q}
                    onClick={() => handleSend(q)}
                    className="w-full text-left text-xs text-muted-foreground/60 font-light px-3 py-2 rounded-lg border border-border/30 hover:border-border/60 hover:text-foreground/80 hover:bg-muted/20 transition-all duration-150 leading-snug"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Chat — 3 cols on desktop */}
        <div className="lg:col-span-3 flex flex-col min-h-0">
          <div
            className="meal-card-enter flex-1 flex flex-col min-h-0 rounded-2xl border border-border/40 overflow-hidden"
            style={{ animationDelay: "0.06s" }}
          >
            {/* Chat messages */}
            <div className="flex-1 overflow-y-auto p-5 min-h-0">
              {!hasMessages ? (
                <div className="h-full flex flex-col items-center justify-center text-center px-6">
                  <div className="relative mb-5">
                    <div
                      className="absolute inset-0 rounded-full blur-2xl opacity-20"
                      style={{
                        background:
                          "radial-gradient(circle, rgb(167 139 250 / 0.6), transparent)",
                      }}
                    />
                    <Bot className="h-14 w-14 text-muted-foreground/30 relative" />
                  </div>
                  <h2
                    className="text-xl font-bold text-foreground/70 mb-2"
                    style={{ fontFamily: "'DM Serif Display', serif" }}
                  >
                    How can I help?
                  </h2>
                  <p className="text-sm text-muted-foreground/40 font-light max-w-xs leading-relaxed">
                    Ask me about nutrition, the DASH diet, meal planning, or
                    your health goals.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((msg, i) => (
                    <div
                      key={i}
                      className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                    >
                      {msg.role === "assistant" && (
                        <div
                          className="h-6 w-6 rounded-lg flex items-center justify-center shrink-0 mt-1 mr-2.5"
                          style={{ background: "rgb(167 139 250 / 0.1)" }}
                        >
                          <Bot
                            className="h-3.5 w-3.5"
                            style={{ color: "rgb(167 139 250 / 0.6)" }}
                          />
                        </div>
                      )}
                      <div
                        className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                          msg.role === "user"
                            ? "bg-primary text-primary-foreground rounded-br-md"
                            : "bg-muted/30 border border-border/30 rounded-bl-md"
                        }`}
                      >
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                      </div>
                    </div>
                  ))}
                  {chatMutation.isPending && (
                    <div className="flex justify-start">
                      <div
                        className="h-6 w-6 rounded-lg flex items-center justify-center shrink-0 mt-1 mr-2.5"
                        style={{ background: "rgb(167 139 250 / 0.1)" }}
                      >
                        <Bot
                          className="h-3.5 w-3.5"
                          style={{ color: "rgb(167 139 250 / 0.6)" }}
                        />
                      </div>
                      <div className="bg-muted/30 border border-border/30 rounded-2xl rounded-bl-md px-4 py-3 text-sm generating-pulse">
                        Thinking...
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>

            {/* Input bar */}
            <div className="shrink-0 p-4 border-t border-border/30">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSend();
                }}
                className="flex gap-2"
              >
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask about your health, diet, or goals..."
                  disabled={chatMutation.isPending}
                  className="flex-1 rounded-xl border-border/40 bg-muted/20 focus:bg-background transition-colors h-10"
                />
                <Button
                  type="submit"
                  className="rounded-xl h-10 w-10 shrink-0"
                  size="icon"
                  disabled={chatMutation.isPending || !input.trim()}
                >
                  <Send className="h-4 w-4" />
                </Button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
