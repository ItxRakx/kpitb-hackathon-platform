import { useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api";

export interface Hackathon {
  id: number;
  title: string;
  slug: string;
  tagline: string;
  starts_at: string;
  ends_at: string;
  registration_opens_at: string;
  registration_closes_at: string;
  team_min_size: number;
  team_max_size: number;
  is_registration_open: boolean;
  is_ongoing: boolean;
  is_completed: boolean;
  tracks: string[];
  problem_count: number;
  participant_count: number;
  team_count: number;
}

export interface HackathonDetail extends Hackathon {
  description: string;
  cover_image_url: string | null;
  rules_url: string | null;
  prizes_text: string;
  rules: string;
  require_participant_enrollment: boolean;
}

interface PaginatedResponse<T> {
  results: T[];
}

export function useHackathons(scope?: "upcoming" | "current" | "past") {
  const [hackathons, setHackathons] = useState<Hackathon[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | Error | null>(null);

  useEffect(() => {
    let active = true;
    const query = scope ? `?scope=${scope}` : "";

    setLoading(true);
    api.get<PaginatedResponse<Hackathon> | Hackathon[]>(`/hackathons/${query}`)
      .then((data) => {
        if (!active) return;
        setHackathons(Array.isArray(data) ? data : data.results);
        setError(null);
      })
      .catch((requestError: ApiError | Error) => {
        if (!active) return;
        setError(requestError);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [scope]);

  return { hackathons, loading, error };
}

export function useHackathon(slug: string) {
  const [hackathon, setHackathon] = useState<HackathonDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | Error | null>(null);

  useEffect(() => {
    let active = true;
    api.get<HackathonDetail>(`/hackathons/${slug}/`)
      .then((data) => {
        if (!active) return;
        setHackathon(data);
        setError(null);
      })
      .catch((requestError: ApiError | Error) => {
        if (active) setError(requestError);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => { active = false; };
  }, [slug]);

  return { hackathon, loading, error };
}
