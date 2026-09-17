import { useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api";
import type { Project } from "@/hooks/useProjects";

export interface ProjectDetail extends Project {
  description: string;
  is_public: boolean;
  is_leader: boolean;
  demo_video_url: string | null;
  attachments: Array<{
    id: number;
    display_name: string;
    attachment_type: string;
    file_url: string;
    file_size: number | null;
  }>;
}

export function useProject(slug: string) {
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | Error | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    api.get<ProjectDetail>(`/projects/${slug}/`)
      .then((data) => {
        if (active) {
          setProject(data);
          setError(null);
        }
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
  }, [slug]);

  return { project, loading, error };
}
