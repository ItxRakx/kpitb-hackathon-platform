import { useCallback, useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api";

export interface Inquiry {
  id: number;
  created_by_name: string;
  created_by_email: string;
  hackathon: number | null;
  hackathon_title: string | null;
  project: number | null;
  project_title: string | null;
  subject: string;
  message: string;
  status: "open" | "answered" | "closed";
  admin_response: string;
  created_at: string;
  updated_at: string;
}

interface PaginatedResponse<T> { results: T[]; }

export function useInquiries() {
  const [inquiries, setInquiries] = useState<Inquiry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | Error | null>(null);

  const refetch = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.get<PaginatedResponse<Inquiry> | Inquiry[]>("/projects/inquiries/");
      setInquiries(Array.isArray(data) ? data : data.results);
      setError(null);
    } catch (requestError) {
      setError(requestError as ApiError | Error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void refetch(); }, [refetch]);
  return { inquiries, loading, error, refetch };
}
