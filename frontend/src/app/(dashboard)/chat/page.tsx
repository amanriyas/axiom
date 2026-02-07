"use client";

import { useEffect, useState, useRef } from "react";
import {
  Send,
  Plus,
  MessageSquare,
  Bot,
  User,
  Loader2,
  Trash2,
} from "lucide-react";
import { TopNav } from "@/components/layout/top-nav";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { toast } from "sonner";
import { chatApi } from "@/lib/api";
import { ChatConversation, ChatMessage } from "@/types";

export default function ChatPage() {
  const [conversations, setConversations] = useState<ChatConversation[]>([]);
  const [activeConversation, setActiveConversation] = useState<ChatConversation | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchConversations = async () => {
    setIsLoading(true);
    try {
      const data = await chatApi.listConversations();
      setConversations(data);
    } catch (error) {
      console.error("Failed to fetch conversations:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const selectConversation = async (conversation: ChatConversation) => {
    setActiveConversation(conversation);
    try {
      const msgs = await chatApi.getMessages(conversation.id);
      setMessages(msgs);
    } catch {
      toast.error("Failed to load messages");
    }
  };

  const createNewConversation = async () => {
    try {
      const conv = await chatApi.createConversation();
      setConversations((prev) => [conv, ...prev]);
      setActiveConversation(conv);
      setMessages([]);
    } catch {
      toast.error("Failed to create conversation");
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isSending) return;

    let conversation = activeConversation;

    // Auto-create conversation if none selected
    if (!conversation) {
      try {
        conversation = await chatApi.createConversation(input.slice(0, 50));
        setConversations((prev) => [conversation!, ...prev]);
        setActiveConversation(conversation);
      } catch {
        toast.error("Failed to create conversation");
        return;
      }
    }

    const userMessage: ChatMessage = {
      id: Date.now(),
      conversation_id: conversation.id,
      role: "user",
      content: input,
      sources: null,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    setInput("");
    setIsSending(true);

    try {
      const response = await chatApi.sendMessage(conversation.id, currentInput);
      setMessages((prev) => [...prev, response]);
    } catch {
      toast.error("Failed to get response");
      // Remove the optimistic user message
      setMessages((prev) => prev.filter((m) => m.id !== userMessage.id));
      setInput(currentInput);
    } finally {
      setIsSending(false);
    }
  };

  const deleteConversation = async (convId: number, e?: React.MouseEvent) => {
    e?.stopPropagation();
    try {
      await chatApi.deleteConversation(convId);
      setConversations((prev) => prev.filter((c) => c.id !== convId));
      if (activeConversation?.id === convId) {
        setActiveConversation(null);
        setMessages([]);
      }
      toast.success("Conversation deleted");
    } catch {
      toast.error("Failed to delete conversation");
    }
  };

  const clearAllHistory = async () => {
    try {
      await chatApi.clearAll();
      setConversations([]);
      setActiveConversation(null);
      setMessages([]);
      toast.success("All chat history cleared");
    } catch {
      toast.error("Failed to clear history");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Disable parent main overflow-auto so our internal scroll areas work
  useEffect(() => {
    const main = document.querySelector("main");
    if (main) {
      main.style.overflow = "hidden";
      return () => {
        main.style.overflow = "";
      };
    }
  }, []);

  return (
    <div className="flex flex-col h-full">
      <TopNav title="Policy Chat" />

      <div className="flex flex-1 min-h-0 overflow-hidden">
        {/* Sidebar - Conversations */}
        <div className="w-72 border-r border-border flex flex-col min-h-0">
          <div className="p-3 border-b border-border shrink-0 space-y-2">
            <Button className="w-full" size="sm" onClick={createNewConversation}>
              <Plus className="mr-2 h-4 w-4" />
              New Chat
            </Button>
            {conversations.length > 0 && (
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button variant="outline" size="sm" className="w-full text-muted-foreground">
                    <Trash2 className="mr-2 h-3.5 w-3.5" />
                    Clear All History
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Clear all chat history?</AlertDialogTitle>
                    <AlertDialogDescription>
                      This will permanently delete all {conversations.length} conversation{conversations.length !== 1 ? "s" : ""} and their messages. This action cannot be undone.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction onClick={clearAllHistory} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                      Delete All
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            )}
          </div>

          <ScrollArea className="flex-1 min-h-0">
            <div className="p-2 space-y-1">
              {conversations.length === 0 && !isLoading ? (
                <div className="py-8 text-center text-sm text-muted-foreground">
                  <MessageSquare className="mx-auto mb-2 h-8 w-8 opacity-50" />
                  <p>No conversations yet</p>
                  <p className="text-xs mt-1">Start a new chat to ask about policies</p>
                </div>
              ) : (
                conversations.map((conv) => (
                  <div
                    key={conv.id}
                    onClick={() => selectConversation(conv)}
                    className={`group relative w-full text-left rounded-lg px-3 py-2 text-sm transition-colors cursor-pointer ${
                      activeConversation?.id === conv.id
                        ? "bg-sidebar-accent text-sidebar-accent-foreground"
                        : "text-muted-foreground hover:bg-sidebar-accent/50"
                    }`}
                  >
                    <p className="font-medium truncate pr-6">{conv.title || "New conversation"}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {new Date(conv.last_message_at).toLocaleDateString()}
                    </p>
                    <button
                      onClick={(e) => deleteConversation(conv.id, e)}
                      className="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded-md opacity-0 group-hover:opacity-100 hover:bg-destructive/20 hover:text-destructive transition-all"
                      title="Delete conversation"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col min-h-0 min-w-0">
          {!activeConversation && messages.length === 0 ? (
            /* Empty State */
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center max-w-md">
                <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                  <Bot className="h-8 w-8 text-primary" />
                </div>
                <h2 className="text-xl font-semibold mb-2">Policy Chatbot</h2>
                <p className="text-muted-foreground mb-6">
                  Ask questions about company policies, onboarding procedures, benefits, and more. 
                  Answers are powered by your uploaded policy documents.
                </p>
                <div className="grid gap-2 text-left">
                  {[
                    "What is our remote work policy?",
                    "How many vacation days do employees get?",
                    "What does the onboarding process look like?",
                  ].map((suggestion) => (
                    <button
                      key={suggestion}
                      onClick={() => {
                        setInput(suggestion);
                      }}
                      className="rounded-lg border px-4 py-2 text-sm text-muted-foreground hover:bg-accent hover:text-foreground transition-colors text-left"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            /* Messages */
            <ScrollArea className="flex-1 min-h-0">
              <div className="max-w-3xl mx-auto space-y-4 p-4 pb-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${message.role === "user" ? "justify-end" : ""}`}
                  >
                    {message.role === "assistant" && (
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
                        <Bot className="h-4 w-4 text-primary" />
                      </div>
                    )}
                    <div
                      className={`rounded-lg px-4 py-3 max-w-[80%] ${
                        message.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted"
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      {message.sources && (() => {
                        try {
                          const parsed = JSON.parse(message.sources);
                          if (Array.isArray(parsed) && parsed.length > 0) {
                            return (
                              <div className="mt-2 flex flex-wrap gap-1">
                                {parsed.map((source: { text?: string; source?: string }, i: number) => (
                                  <Badge key={i} variant="outline" className="text-[10px]">
                                    {source.source || source.text || String(source)}
                                  </Badge>
                                ))}
                              </div>
                            );
                          }
                          return null;
                        } catch {
                          return null;
                        }
                      })()}
                    </div>
                    {message.role === "user" && (
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary">
                        <User className="h-4 w-4 text-primary-foreground" />
                      </div>
                    )}
                  </div>
                ))}
                {isSending && (
                  <div className="flex gap-3">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
                      <Bot className="h-4 w-4 text-primary" />
                    </div>
                    <div className="rounded-lg bg-muted px-4 py-3">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Thinking...
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>
          )}

          {/* Input */}
          <div className="border-t border-border p-4 shrink-0">
            <div className="max-w-3xl mx-auto flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about company policies..."
                disabled={isSending}
                className="flex-1"
              />
              <Button onClick={sendMessage} disabled={!input.trim() || isSending} size="icon">
                {isSending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
