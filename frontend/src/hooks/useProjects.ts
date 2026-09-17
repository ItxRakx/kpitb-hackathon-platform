import { useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api";

export interface Project {
  id: number;
  title: string;
  slug: string;
  tagline: string;
  short_description: string;
  track: string | null;
  build_mode: string;
  technologies: string[];
  hackathon_title: string;
  team: number;
  team_name: string;
  problem_statement: number | null;
  problem_statement_title: string | null;
  status: string;
  is_public: boolean;
  repo_url: string | null;
  demo_url: string | null;
  submitted_at: string | null;
}

interface PaginatedResponse<T> {
  results: T[];
}

export function useProjects(includePrivate = false) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | Error | null>(null);

  useEffect(() => {
    let active = true;
    const query = includePrivate ? "?is_public=false" : "";
    api.get<PaginatedResponse<Project> | Project[]>(`/projects/${query}`)
      .then((data) => {
        if (!active) return;
        setProjects(Array.isArray(data) ? data : data.results);
        setError(null);
      })
      .catch((requestError: ApiError | Error) => {
        if (active) setError(requestError);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [includePrivate]);

  return { projects, loading, error };
}
