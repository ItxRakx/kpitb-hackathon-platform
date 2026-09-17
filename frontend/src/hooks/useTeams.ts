import { useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api";

export interface TeamMember {
  id: number;
  user: {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
  };
  is_leader: boolean;
  role: string;
  joined_at: string;
}

export interface Team {
  id: number;
  name: string;
  tagline: string;
  track: string | null;
  problem_statement: number | null;
  problem_statement_title: string | null;
  hackathon: number;
  hackathon_title: string;
  invite_code: string;
  is_roster_locked: boolean;
  member_count: number;
  max_members: number;
  is_registered: boolean;
  created_at: string;
  memberships?: TeamMember[];
  is_leader?: boolean;
}

interface PaginatedResponse<T> {
  results: T[];
}

export function useTeams(mine = false) {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | Error | null>(null);

  useEffect(() => {
    let active = true;
    const query = mine ? "?mine=true" : "";

    setLoading(true);
    api.get<PaginatedResponse<Team> | Team[]>(`/teams/${query}`)
      .then((data) => {
        if (!active) return;
        setTeams(Array.isArray(data) ? data : data.results);
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
  }, [mine]);

  return { teams, loading, error };
}
