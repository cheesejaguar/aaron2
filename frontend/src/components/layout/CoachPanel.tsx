import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { X, Send, Bot } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useUIStore } from "@/stores/ui-store";
import { coachApi } from "@/api/coach";
import type { ChatMessage } from "@/types";

export function CoachPanel() {
  const close = useUIStore((s) => s.toggleCoachPanel);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<string>();

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

  const handleSend = () => {
    if (!input.trim()) return;
    const msg = input.trim();
    setMessages((prev) => [...prev, { role: "user", content: msg }]);
    setInput("");
    chatMutation.mutate({ message: msg, conversation_id: conversationId });
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between p-4 border-b border-border/40">
        <div className="flex items-center gap-2">
          <Bot className="h-4 w-4" style={{ color: "rgb(167 139 250 / 0.6)" }} />
          <h3
            className="text-lg font-bold"
            style={{ fontFamily: "'DM Serif Display', serif" }}
          >
            AI Health Coach
          </h3>
        </div>
        <Button variant="ghost" size="icon" className="h-8 w-8 rounded-lg" onClick={close}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {messages.length === 0 && (
            <div className="text-center mt-12">
              <Bot className="h-10 w-10 text-muted-foreground/20 mx-auto mb-3" />
              <p className="text-sm text-muted-foreground/40 font-light">
                Ask me about your diet, health goals, or meal planning!
              </p>
            </div>
          )}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-xl px-4 py-2.5 text-sm ${
                  msg.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted/30 border border-border/30"
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
          {chatMutation.isPending && (
            <div className="flex justify-start">
              <div className="bg-muted/30 border border-border/30 rounded-xl px-4 py-2.5 text-sm generating-pulse">
                Thinking...
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      <div className="p-4 border-t border-border/40">
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
            placeholder="Ask your health coach..."
            disabled={chatMutation.isPending}
            className="rounded-xl border-border/40 bg-muted/20 focus:bg-background transition-colors"
          />
          <Button
            type="submit"
            size="icon"
            className="rounded-xl h-10 w-10 shrink-0"
            disabled={chatMutation.isPending || !input.trim()}
          >
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  );
}
