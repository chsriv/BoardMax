"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion"; 
import { Send, Sparkles, Loader2, GraduationCap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface Message {
  id: string;
  role: "user" | "ai";
  content: string;
}

export default function ChatInterface() {
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSearch = async () => {
    const cleanQuery = query.trim();
    if (!cleanQuery) return;

    // SECURITY GUARDRAIL 1: Input Length Validation (Max 500 chars)
    if (cleanQuery.length > 500) {
      const errorMsg: Message = { 
        id: Date.now().toString(), 
        role: "ai", 
        content: "⛔ **Security Block**: Query too long (max 500 characters). Please shorten your question." 
      };
      setMessages((prev) => [...prev, errorMsg]);
      return;
    }

    // SECURITY GUARDRAIL 2: Prompt Injection Detection
    const dangerousPatterns = [
      /ignore\s+(previous|above|all)\s+instructions?/i,
      /system\s*:\s*/i,
      /you\s+are\s+now/i,
      /new\s+role/i,
      /forget\s+(everything|all|previous)/i,
      /<script>/i,
      /javascript:/i,
      /\bexec\b|\beval\b/i
    ];

    const hasDangerousPattern = dangerousPatterns.some(pattern => pattern.test(cleanQuery));
    if (hasDangerousPattern) {
      const errorMsg: Message = { 
        id: Date.now().toString(), 
        role: "ai", 
        content: "⛔ **Security Block**: Your query contains potentially unsafe content. Please rephrase your question." 
      };
      setMessages((prev) => [...prev, errorMsg]);
      return;
    }

    // 1. Add User Message
    const userMsg: Message = { id: Date.now().toString(), role: "user", content: cleanQuery };
    setMessages((prev) => [...prev, userMsg]);
    setQuery("");
    setIsLoading(true);

    try {
      // 2. Call Backend
      const res = await fetch("http://localhost:8000/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: cleanQuery, subject: "social-science" }),
      });

      const data = await res.json();

      if (!res.ok) {
        // Handle HTTP errors (400, 403, 500, etc.)
        throw new Error(data.detail || "Server error occurred");
      }
      
      // 3. Add AI Response
      const aiMsg: Message = { 
        id: (Date.now() + 1).toString(), 
        role: "ai", 
        content: data.answer || "❌ Error: No response received." 
      };
      setMessages((prev) => [...prev, aiMsg]);

    } catch (err: any) {
      // Show specific error message
      const errorMsg: Message = { 
        id: Date.now().toString(), 
        role: "ai", 
        content: err.message.includes("Failed to fetch") 
          ? "⚠️ **Connection Error**: Backend server is not running on port 8000!"
          : `⛔ **Error**: ${err.message}` 
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4 h-screen flex flex-col font-sans">
      {/* HEADER */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }} 
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between mb-6 pt-4"
      >
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-600 rounded-xl shadow-lg shadow-blue-200">
            <GraduationCap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-800">BoardMax</h1>
            <p className="text-xs text-slate-500 font-medium">AI MARKING SCHEME COACH</p>
          </div>
        </div>
        <Badge variant="secondary" className="bg-blue-100 text-blue-700 px-3 py-1 hover:bg-blue-200">Social Science</Badge>
      </motion.div>

      {/* CHAT AREA */}
      <Card className="flex-1 overflow-hidden bg-white/80 backdrop-blur-md border-slate-200 shadow-xl flex flex-col rounded-3xl">
        <div className="flex-1 overflow-y-auto p-6 space-y-6" ref={scrollRef}>
          <AnimatePresence>
            {messages.length === 0 && (
              <motion.div 
                initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                className="h-full flex flex-col items-center justify-center text-slate-400"
              >
                <Sparkles className="w-16 h-16 mb-4 opacity-10 text-blue-600" />
                <p className="text-lg font-medium text-slate-500">Ask a question to start coaching...</p>
                <p className="text-sm opacity-50">Try: "Explain the Non-Cooperation Movement"</p>
              </motion.div>
            )}

            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 20, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] p-5 rounded-2xl shadow-sm text-[15px] leading-relaxed ${
                    msg.role === "user"
                      ? "bg-blue-600 text-white rounded-br-none"
                      : "bg-white border border-slate-100 text-slate-800 rounded-bl-none"
                  }`}
                >
                  {/* BOLD TEXT RENDERING */}
                  <div className="whitespace-pre-line">
                    {msg.content.split("**").map((part, i) => 
                      i % 2 === 1 ? <strong key={i} className={msg.role === 'ai' ? "text-blue-700 font-bold" : "font-bold underline decoration-blue-300 decoration-2 underline-offset-2"}>{part}</strong> : part
                    )}
                  </div>
                </div>
              </motion.div>
            ))}

            {isLoading && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex justify-start">
                <div className="bg-white border p-4 rounded-2xl rounded-bl-none flex items-center gap-3 shadow-sm">
                  <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
                  <span className="text-sm text-slate-500 font-medium">Analyzing Marking Scheme...</span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* INPUT AREA */}
        <div className="p-4 bg-white/50 border-t border-slate-100 flex gap-3 backdrop-blur-sm">
          <Input 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder="Type your question..." 
            className="h-12 border-slate-200 focus-visible:ring-blue-500 rounded-xl bg-white shadow-sm text-base"
          />
          <Button 
            onClick={handleSearch} 
            disabled={isLoading} 
            className="h-12 w-12 rounded-xl bg-blue-600 hover:bg-blue-700 transition-all shadow-md hover:shadow-lg hover:shadow-blue-200"
          >
            <Send className="w-5 h-5" />
          </Button>
        </div>
      </Card>
    </div>
  );
}