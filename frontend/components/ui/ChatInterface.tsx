"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

type Mode = "optimizer" | "evaluator";

interface Message {
  role: "user" | "assistant";
  content: string;
  mode?: Mode;
  subject?: string;
}

const subjects = ["Physics", "Chemistry", "Biology", "Math", "Computer Science", "English"];

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [subject, setSubject] = useState("Physics");
  const [mode, setMode] = useState<Mode>("optimizer");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim()) return;
    if (input.length < 10) {
      setError("Please write at least 10 characters");
      return;
    }

    setError(null);
    const userMessage: Message = {
      role: "user",
      content: input,
      mode,
      subject,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: input,
          subject: subject,
          mode: mode,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Request failed");
      }

      const data = await response.json();

      const aiMessage: Message = {
        role: "assistant",
        content: data.answer,
        mode: data.mode,
        subject: data.subject,
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      console.error("Error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const formatMarkdown = (text: string) => {
    // Simple markdown parser for bold text
    return text.split("\n").map((line, idx) => {
      const parts = line.split(/(\*\*.*?\*\*)/g);
      return (
        <div key={idx} className="mb-2">
          {parts.map((part, i) => {
            if (part.startsWith("**") && part.endsWith("**")) {
              return (
                <strong key={i} className="font-semibold text-blue-700">
                  {part.slice(2, -2)}
                </strong>
              );
            }
            return <span key={i}>{part}</span>;
          })}
        </div>
      );
    });
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-md p-4 border-b-4 border-blue-600">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-blue-900">BoardMax</h1>
            <p className="text-sm text-gray-600">CBSE Answer Intelligence</p>
          </div>
          <div className="flex gap-4 items-center">
            {/* Subject Selector */}
            <div className="flex flex-col">
              <label className="text-xs text-gray-600 mb-1">Subject</label>
              <select
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isLoading}
              >
                {subjects.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>

            {/* Mode Selector */}
            <div className="flex flex-col">
              <label className="text-xs text-gray-600 mb-1">Mode</label>
              <div className="flex gap-2">
                <Button
                  variant={mode === "optimizer" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setMode("optimizer")}
                  disabled={isLoading}
                  className={mode === "optimizer" ? "bg-blue-600 hover:bg-blue-700" : ""}
                >
                  📝 Optimizer
                </Button>
                <Button
                  variant={mode === "evaluator" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setMode("evaluator")}
                  disabled={isLoading}
                  className={mode === "evaluator" ? "bg-green-600 hover:bg-green-700" : ""}
                >
                  ✓ Evaluator
                </Button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Chat Messages */}
      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full">
          <div className="max-w-6xl mx-auto p-6 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">🎓</div>
                <h2 className="text-2xl font-semibold text-gray-700 mb-2">
                  Welcome to BoardMax!
                </h2>
                <p className="text-gray-600 mb-4">
                  Choose your mode and start optimizing your answers.
                </p>
                <div className="grid grid-cols-2 gap-4 max-w-2xl mx-auto mt-8">
                  <Card className="p-4 border-2 border-blue-200 bg-blue-50">
                    <div className="text-3xl mb-2">📝</div>
                    <h3 className="font-semibold text-blue-900 mb-1">Optimizer Mode</h3>
                    <p className="text-sm text-gray-700">
                      Rewrites your answer in official CBSE marking scheme format to maximize marks.
                    </p>
                  </Card>
                  <Card className="p-4 border-2 border-green-200 bg-green-50">
                    <div className="text-3xl mb-2">✓</div>
                    <h3 className="font-semibold text-green-900 mb-1">Evaluator Mode</h3>
                    <p className="text-sm text-gray-700">
                      Evaluates your answer against the marking scheme and provides detailed feedback.
                    </p>
                  </Card>
                </div>
              </div>
            ) : (
              messages.map((message, idx) => (
                <div
                  key={idx}
                  className={`flex ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <Card
                    className={`max-w-3xl p-4 ${
                      message.role === "user"
                        ? "bg-blue-600 text-white"
                        : "bg-white border-2 border-gray-200"
                    }`}
                  >
                    {message.role === "user" ? (
                      <>
                        <div className="flex items-center gap-2 mb-2">
                          <Badge variant="secondary" className="bg-white/20 text-white">
                            {message.subject}
                          </Badge>
                          <Badge variant="secondary" className="bg-white/20 text-white">
                            {message.mode === "optimizer" ? "📝 Optimizer" : "✓ Evaluator"}
                          </Badge>
                        </div>
                        <div className="whitespace-pre-wrap">{message.content}</div>
                      </>
                    ) : (
                      <>
                        <div className="flex items-center gap-2 mb-3">
                          <span className="text-2xl">🤖</span>
                          <span className="font-semibold text-gray-800">
                            BoardMax AI
                          </span>
                          <Badge variant="outline">
                            {message.mode === "optimizer" ? "Optimized Answer" : "Evaluation"}
                          </Badge>
                        </div>
                        <Separator className="mb-3" />
                        <div className="text-gray-800 leading-relaxed">
                          {formatMarkdown(message.content)}
                        </div>
                      </>
                    )}
                  </Card>
                </div>
              ))
            )}

            {isLoading && (
              <div className="flex justify-start">
                <Card className="max-w-3xl p-4 bg-white border-2 border-gray-200">
                  <div className="flex items-center gap-3">
                    <div className="animate-pulse flex space-x-2">
                      <div className="w-3 h-3 bg-blue-600 rounded-full animate-bounce"></div>
                      <div className="w-3 h-3 bg-blue-600 rounded-full animate-bounce delay-100"></div>
                      <div className="w-3 h-3 bg-blue-600 rounded-full animate-bounce delay-200"></div>
                    </div>
                    <span className="text-gray-600">AI is thinking...</span>
                  </div>
                </Card>
              </div>
            )}
          </div>
        </ScrollArea>
      </div>

      {/* Input Area */}
      <div className="bg-white border-t-4 border-blue-600 p-4 shadow-lg">
        <div className="max-w-6xl mx-auto">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg mb-3 text-sm">
              ⚠️ {error}
            </div>
          )}
          <form onSubmit={handleSubmit} className="flex gap-3">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={
                mode === "optimizer"
                  ? "Paste your answer here to optimize it..."
                  : "Paste your answer here for evaluation..."
              }
              disabled={isLoading}
              className="flex-1 text-base"
              maxLength={2000}
            />
            <Button
              type="submit"
              disabled={isLoading || !input.trim()}
              className={`px-8 ${
                mode === "optimizer"
                  ? "bg-blue-600 hover:bg-blue-700"
                  : "bg-green-600 hover:bg-green-700"
              }`}
            >
              {isLoading ? "Processing..." : mode === "optimizer" ? "Optimize" : "Evaluate"}
            </Button>
          </form>
          <p className="text-xs text-gray-500 mt-2">
            {input.length}/2000 characters • Minimum 10 characters required
          </p>
        </div>
      </div>
    </div>
  );
}
