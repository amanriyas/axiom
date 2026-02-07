"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { AgentEvent } from "@/types";

interface UseSSEStreamOptions {
  onEvent?: (event: AgentEvent) => void;
  onError?: (error: Error) => void;
  onComplete?: () => void;
}

export function useSSEStream(url: string | null, options: UseSSEStreamOptions = {}) {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Stabilize callbacks in a ref so they never cause reconnection
  const callbacksRef = useRef(options);
  callbacksRef.current = options;

  const clearEvents = useCallback(() => {
    setEvents([]);
  }, []);

  const connect = useCallback(() => {
    if (!url || eventSourceRef.current) return;

    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as AgentEvent;
        setEvents((prev) => [...prev, data]);
        callbacksRef.current.onEvent?.(data);

        // Check for completion
        if (data.type === "done" && data.message.includes("complete")) {
          callbacksRef.current.onComplete?.();
        }
      } catch (e) {
        console.error("Failed to parse SSE event:", e);
      }
    };

    eventSource.onerror = () => {
      const err = new Error("SSE connection error");
      setError(err);
      setIsConnected(false);
      callbacksRef.current.onError?.(err);
      eventSource.close();
      eventSourceRef.current = null;
    };
  }, [url]); // Only depends on url — callbacks are read from ref

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
    }
  }, []);

  useEffect(() => {
    if (url) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [url, connect, disconnect]);

  return {
    events,
    isConnected,
    error,
    clearEvents,
    connect,
    disconnect,
  };
}
