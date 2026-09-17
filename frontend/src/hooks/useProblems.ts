import { useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api";

export interface ProblemStatement {
  id: number;
  hackathon: number;
  hackathon_title: string;
  hackathon_slug: string;
  title: string;
  slug: string;
  category: string;
  summary: string;
  description: string;
  deliverables: string;
  difficulty: "starter" | "intermediate" | "advanced";
  is_published: boolean;
}

interface PaginatedResponse<T> {
  results: T[];
}

export function useProblems(hackathon?: number | string) {
  const [problems, setProblems] = useState<ProblemStatement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | Error | null>(null);

  useEffect(() => {
    let active = true;
    const query = hackathon ? `?hackathon=${encodeURIComponent(hackathon)}` : "";
    setLoading(true);
    api.get<PaginatedResponse<ProblemStatement> | ProblemStatement[]>(`/hackathons/problems/${query}`)
      .then((data) => {
        if (!active) return;
        setProblems(Array.isArray(data) ? data : data.results);
        setError(null);
      })
      .catch((requestError: ApiError | Error) => {
        if (active) setError(requestError);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => { active = false; };
  }, [hackathon]);

  return { problems, loading, error };
}
