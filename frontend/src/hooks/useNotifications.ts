import { useCallback, useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api";

export interface NotificationItem {
  id: number;
  title: string;
  body: string;
  category: string;
  action_url: string | null;
  is_read: boolean;
  read_at: string | null;
  created_at: string;
}

export function useNotifications(unreadOnly = false) {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | Error | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const query = unreadOnly ? "?unread_only=true" : "";
      const data = await api.get<NotificationItem[]>(`/notifications/${query}`);
      setNotifications(data);
      setError(null);
    } catch (requestError) {
      setError(requestError as ApiError | Error);
    } finally {
      setLoading(false);
    }
  }, [unreadOnly]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function markRead(id: number) {
    await api.patch<NotificationItem>(`/notifications/${id}/mark-read/`);
    setNotifications((current) => current.map((item) => item.id === id ? { ...item, is_read: true } : item));
  }

  async function markAllRead() {
    await api.post("/notifications/mark-all-read/");
    setNotifications((current) => current.map((item) => ({ ...item, is_read: true })));
  }

  return { notifications, loading, error, refresh, markRead, markAllRead };
}
