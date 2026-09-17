import { useEffect, useState, useCallback } from "react";
import { User, isAuthenticated } from "@/lib/auth";
import { api, ApiError } from "@/lib/api";

export interface UseUserResult {
  loading: boolean;
  user: User | null;
  error: ApiError | Error | null;
  refetch: () => Promise<void>;
}

let cachedUser: User | null = null;
let cachedPromise: Promise<User | null> | null = null;

export function useUser(): UseUserResult {
  const [loading, setLoading] = useState<boolean>(() => isAuthenticated() && cachedUser === null);
  const [user, setUser] = useState<User | null>(cachedUser);
  const [error, setError] = useState<ApiError | Error | null>(null);

  const fetchUser = useCallback(async () => {
    if (!isAuthenticated()) {
      cachedUser = null;
      setUser(null);
      setLoading(false);
      setError(null);
      return;
    }

    if (cachedPromise) {
      try {
        const result = await cachedPromise;
        setUser(result);
      } catch (err) {
        setError(err as ApiError | Error);
      } finally {
        setLoading(false);
      }
      return;
    }

    setLoading(true);
    setError(null);

    cachedPromise = (async () => {
      try {
        const data = await api.get<User>("/accounts/me/");
        cachedUser = data;
        return data;
      } catch (err) {
        cachedUser = null;
        throw err;
      } finally {
        cachedPromise = null;
      }
    })();

    try {
      const result = await cachedPromise;
      setUser(result);
    } catch (err) {
      setError(err as ApiError | Error);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const refetch = useCallback(async () => {
    cachedUser = null;
    cachedPromise = null;
    await fetchUser();
  }, [fetchUser]);

  return { loading, user, error, refetch };
}
