import { useCallback, useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";

export interface ParticipantEnrollment {
  id: number;
  hackathon: number;
  hackathon_title: string;
  hackathon_slug: string;
  selected_problem: number | null;
  selected_problem_title: string | null;
  participation_preference: "create_team" | "join_team" | "need_team" | "solo";
  primary_role: "developer" | "data_ai" | "designer" | "product" | "domain_expert" | "student" | "other";
  experience_level: "beginner" | "intermediate" | "advanced";
  attendance_mode: "onsite" | "online" | "flexible";
  motivation: string;
  agreed_to_rules: boolean;
  status: "registered" | "approved" | "waitlist" | "cancelled";
  created_at: string;
}

export function useEnrollment(hackathonSlug: string) {
  const [enrollment, setEnrollment] = useState<ParticipantEnrollment | null>(null);
  const [loading, setLoading] = useState(isAuthenticated());
  const [error, setError] = useState<ApiError | Error | null>(null);

  const refetch = useCallback(async () => {
    if (!isAuthenticated()) {
      setEnrollment(null); setLoading(false); return;
    }
    setLoading(true);
    try {
      const data = await api.get<ParticipantEnrollment>(`/hackathons/${hackathonSlug}/enrollment/`);
      setEnrollment(data);
      setError(null);
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 404) {
        setEnrollment(null);
        setError(null);
      } else {
        setError(requestError as ApiError | Error);
      }
    } finally {
      setLoading(false);
    }
  }, [hackathonSlug]);

  useEffect(() => { void refetch(); }, [refetch]);
  return { enrollment, loading, error, refetch };
}

export function useMyEnrollments() {
  const [enrollments, setEnrollments] = useState<ParticipantEnrollment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    api.get<ParticipantEnrollment[]>("/hackathons/enrollments/me/")
      .then((data) => { if (active) setEnrollments(data); })
      .catch(() => { if (active) setEnrollments([]); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  return { enrollments, loading };
}
