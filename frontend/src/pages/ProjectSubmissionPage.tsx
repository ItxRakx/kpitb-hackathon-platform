import { FormEvent, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import Container from "@/components/ui/Container";
import Button from "@/components/ui/Button";
import { useProjects, type Project } from "@/hooks/useProjects";
import { useTeams } from "@/hooks/useTeams";
import { ApiError, api } from "@/lib/api";

const buildModes = ["online", "physical", "hybrid"] as const;

function getErrorMessage(error: unknown) {
  if (error instanceof ApiError && typeof error.data === "object" && error.data !== null) {
    const data = error.data as Record<string, unknown>;
    if (typeof data.detail === "string") return data.detail;
    const first = Object.values(data).flat().find((value) => typeof value === "string");
    if (typeof first === "string") return first;
  }
  return "We could not save the project. Check the form and try again.";
}

function attachmentType(file: File) {
  if (file.type.startsWith("video/")) return "demo_video";
  if (file.type.startsWith("image/")) return "screenshot";
  if (/presentation|powerpoint|pdf/.test(file.type)) return "deck";
  if (/zip|compressed|tar/.test(file.type)) return "source_code";
  return "report";
}

export default function ProjectSubmissionPage() {
  const navigate = useNavigate();
  const { teams, loading: teamsLoading } = useTeams(true);
  const { projects, loading: projectsLoading } = useProjects(true);
  const [teamId, setTeamId] = useState("");
  const [title, setTitle] = useState("");
  const [tagline, setTagline] = useState("");
  const [shortDescription, setShortDescription] = useState("");
  const [description, setDescription] = useState("");
  const [buildMode, setBuildMode] = useState<(typeof buildModes)[number]>("online");
  const [technologies, setTechnologies] = useState("");
  const [repoUrl, setRepoUrl] = useState("");
  const [demoUrl, setDemoUrl] = useState("");
  const [demoVideoUrl, setDemoVideoUrl] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [recordedVideo, setRecordedVideo] = useState<File | null>(null);
  const [recording, setRecording] = useState(false);
  const [videoPreview, setVideoPreview] = useState("");
  const [working, setWorking] = useState(false);
  const [error, setError] = useState("");
  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const previewRef = useRef<HTMLVideoElement | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const eligibleTeams = teams.filter((team) => team.is_registered && team.is_leader && !projects.some((project) => project.team === team.id));
  const selectedTeam = teams.find((team) => String(team.id) === teamId);
  const existingProjects = projects.filter((project) => teams.some((team) => team.id === project.team));

  useEffect(() => () => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    if (videoPreview) URL.revokeObjectURL(videoPreview);
  }, [videoPreview]);

  async function startRecording() {
    setError("");
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
      setError("Video recording is not supported in this browser. Upload a video file instead.");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      streamRef.current = stream;
      if (previewRef.current) {
        previewRef.current.srcObject = stream;
        await previewRef.current.play();
      }
      const preferredType = MediaRecorder.isTypeSupported("video/webm;codecs=vp9,opus") ? "video/webm;codecs=vp9,opus" : "video/webm";
      const recorder = new MediaRecorder(stream, { mimeType: preferredType });
      chunksRef.current = [];
      recorder.ondataavailable = (event) => { if (event.data.size) chunksRef.current.push(event.data); };
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType || "video/webm" });
        const file = new File([blob], `team-intro-${Date.now()}.webm`, { type: blob.type });
        setRecordedVideo(file);
        setVideoPreview(URL.createObjectURL(blob));
        stream.getTracks().forEach((track) => track.stop());
        if (previewRef.current) previewRef.current.srcObject = null;
      };
      recorderRef.current = recorder;
      recorder.start(1000);
      setRecording(true);
    } catch {
      setError("Camera or microphone access was not available. You can upload an intro video instead.");
    }
  }

  function stopRecording() {
    recorderRef.current?.stop();
    setRecording(false);
  }

  async function uploadAttachment(projectId: number, file: File) {
    const body = new FormData();
    body.append("project", String(projectId));
    body.append("file", file);
    body.append("display_name", file.name);
    body.append("attachment_type", attachmentType(file));
    await api.post(`/projects/${projectId}/attachments/`, body);
  }

  async function saveProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setWorking(true); setError("");
    try {
      const project = await api.post<Project>("/projects/", {
        team_id: Number(teamId), title: title.trim(), tagline: tagline.trim(),
        short_description: shortDescription.trim(), description: description.trim(),
        build_mode: buildMode,
        technologies: technologies.split(",").map((item) => item.trim()).filter(Boolean),
        repo_url: repoUrl.trim() || null, demo_url: demoUrl.trim() || null,
        demo_video_url: demoVideoUrl.trim() || null,
      });
      for (const file of [...files, ...(recordedVideo ? [recordedVideo] : [])]) {
        await uploadAttachment(project.id, file);
      }
      navigate(`/projects/${project.slug}`, { state: { created: true } });
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setWorking(false);
    }
  }

  return (
    <section className="py-16 sm:py-20">
      <Container size="md">
        <Button type="button" variant="ghost" size="sm" onClick={() => navigate("/dashboard")} className="!px-0">Back to dashboard</Button>
        <div className="mt-6 max-w-3xl">
          <div className="pill bg-brand-50 text-brand-700 ring-1 ring-inset ring-brand-200">Proposal workspace</div>
          <h1 className="mt-4 font-display text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">Explain the problem, idea, and proof.</h1>
          <p className="mt-4 text-base leading-7 text-slate-600">The team lead saves one proposal, adds source or documents, and records or uploads a short intro video before final submission.</p>
        </div>

        {error ? <div role="alert" className="mt-8 rounded-xl bg-red-50 p-4 text-sm text-red-700">{error}</div> : null}

        {existingProjects.length > 0 ? <div className="mt-8 rounded-2xl border border-brand-200 bg-brand-50/50 p-5"><p className="text-sm font-semibold text-brand-900">Existing team proposals</p><div className="mt-3 flex flex-wrap gap-2">{existingProjects.map((project) => <Button key={project.id} to={`/projects/${project.slug}`} variant="secondary" size="sm">{project.title} - {project.status}</Button>)}</div></div> : null}

        <form className="card mt-8 space-y-6" onSubmit={saveProject}>
          <div>
            <label className="block text-sm font-semibold text-slate-700" htmlFor="project-team">Registered team you lead</label>
            <select id="project-team" required value={teamId} onChange={(event) => setTeamId(event.target.value)} disabled={teamsLoading} className="mt-2 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm">
              <option value="">{teamsLoading ? "Loading teams..." : "Choose a registered team"}</option>
              {eligibleTeams.map((team) => <option key={team.id} value={team.id}>{team.name} - {team.hackathon_title}</option>)}
            </select>
            {selectedTeam ? <div className="mt-3 rounded-xl bg-slate-50 p-4 text-sm text-slate-700"><span className="font-semibold">Official problem:</span> {selectedTeam.problem_statement_title || "Not selected"}</div> : null}
            {!teamsLoading && eligibleTeams.length === 0 ? <p className="mt-2 text-xs text-amber-700">First create a team, complete its roster, lock it, and register for the hackathon.</p> : null}
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            <label className="text-sm font-semibold text-slate-700">Project name<input required value={title} onChange={(event) => setTitle(event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm" placeholder="e.g. Sehat Saathi" /></label>
            <label className="text-sm font-semibold text-slate-700">One-line promise<input required value={tagline} onChange={(event) => setTagline(event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm" placeholder="What changes for the user?" /></label>
          </div>
          <label className="block text-sm font-semibold text-slate-700">Solution summary<textarea required rows={3} value={shortDescription} onChange={(event) => setShortDescription(event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm" placeholder="Who has the problem, what will you build, and what impact will it make?" /></label>
          <label className="block text-sm font-semibold text-slate-700">Detailed proposal<textarea required rows={8} value={description} onChange={(event) => setDescription(event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm" placeholder="Approach, users, implementation plan, expected impact, and what can be completed during the hackathon." /></label>

          <div className="grid gap-5 md:grid-cols-2">
            <label className="text-sm font-semibold text-slate-700">Participation mode<select value={buildMode} onChange={(event) => setBuildMode(event.target.value as (typeof buildModes)[number])} className="mt-2 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm">{buildModes.map((mode) => <option key={mode} value={mode}>{mode[0].toUpperCase() + mode.slice(1)}</option>)}</select></label>
            <label className="text-sm font-semibold text-slate-700">Tools and technologies<input value={technologies} onChange={(event) => setTechnologies(event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm" placeholder="React, Django, Figma" /></label>
          </div>
          <div className="grid gap-5 md:grid-cols-3">
            <label className="text-sm font-semibold text-slate-700">Repository URL<input type="url" value={repoUrl} onChange={(event) => setRepoUrl(event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm" /></label>
            <label className="text-sm font-semibold text-slate-700">Live demo URL<input type="url" value={demoUrl} onChange={(event) => setDemoUrl(event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm" /></label>
            <label className="text-sm font-semibold text-slate-700">Hosted video URL<input type="url" value={demoVideoUrl} onChange={(event) => setDemoVideoUrl(event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm" /></label>
          </div>

          <div className="rounded-2xl border border-slate-200 p-5">
            <div className="flex flex-wrap items-start justify-between gap-4"><div><h2 className="font-display text-xl font-semibold text-slate-900">Record a 60-90 second team intro</h2><p className="mt-1 text-sm text-slate-500">Introduce the problem, your solution, and why your team can build it.</p></div>{recordedVideo ? <span className="pill bg-emerald-50 text-emerald-700">Intro recorded</span> : null}</div>
            <video ref={previewRef} src={videoPreview || undefined} muted={recording} controls={!!videoPreview} playsInline className="mt-5 aspect-video w-full rounded-2xl bg-slate-950 object-cover" />
            <div className="mt-4 flex flex-wrap gap-3">
              {!recording ? <Button type="button" size="sm" onClick={() => void startRecording()}>{recordedVideo ? "Record again" : "Start camera recording"}</Button> : <Button type="button" size="sm" onClick={stopRecording}>Stop and save recording</Button>}
              {recordedVideo ? <button type="button" className="text-sm font-semibold text-red-600 hover:underline" onClick={() => { setRecordedVideo(null); setVideoPreview(""); }}>Remove recording</button> : null}
            </div>
          </div>

          <label className="block text-sm font-semibold text-slate-700">Proposal files or pre-recorded video
            <input type="file" multiple accept=".pdf,.ppt,.pptx,.doc,.docx,.zip,image/*,video/*" onChange={(event) => setFiles(Array.from(event.target.files || []))} className="mt-2 block w-full rounded-xl border border-slate-300 px-4 py-3 text-sm" />
            <span className="mt-2 block text-xs font-normal text-slate-500">Add a proposal deck, report, screenshots, source archive, or video. You can also use links above.</span>
          </label>
          <div className="flex flex-wrap items-center justify-between gap-4 border-t border-slate-100 pt-5"><span className="text-xs text-slate-500">{projectsLoading ? "Checking proposals..." : `${files.length + (recordedVideo ? 1 : 0)} file${files.length + (recordedVideo ? 1 : 0) === 1 ? "" : "s"} ready`}</span><Button type="submit" disabled={working || !teamId}>{working ? "Uploading and saving..." : "Save proposal draft"}</Button></div>
        </form>
      </Container>
    </section>
  );
}
