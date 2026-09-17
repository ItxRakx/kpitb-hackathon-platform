import { Routes, Route } from "react-router-dom";
import AppLayout from "./components/layout/AppLayout";
import LandingPage from "./pages/LandingPage";
import GalleryPage from "./pages/GalleryPage";
import HackathonsPage from "./pages/HackathonsPage";
import HackathonDetailPage from "./pages/HackathonDetailPage";
import ProjectDetailPage from "./pages/ProjectDetailPage";
import AboutPage from "./pages/AboutPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import NotFoundPage from "./pages/NotFoundPage";
import DashboardPage from "./pages/DashboardPage";
import TeamPage from "./pages/TeamPage";
import ProjectSubmissionPage from "./pages/ProjectSubmissionPage";
import NotificationsPage from "./pages/NotificationsPage";
import JudgeDashboardPage from "./pages/JudgeDashboardPage";
import AdminDashboardPage from "./pages/AdminDashboardPage";
import AccountRecoveryPage from "./pages/AccountRecoveryPage";
import ProblemStatementsPage from "./pages/ProblemStatementsPage";
import ProfilePage from "./pages/ProfilePage";
import SupportPage from "./pages/SupportPage";
import ProtectedRoute from "./components/auth/ProtectedRoute";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<LandingPage />} />
        <Route path="/gallery" element={<GalleryPage />} />
        <Route path="/hackathons" element={<HackathonsPage />} />
        <Route path="/hackathons/:slug" element={<HackathonDetailPage />} />
        <Route path="/problems" element={<ProblemStatementsPage />} />
        <Route path="/projects/:slug" element={<ProjectDetailPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/password-reset" element={<AccountRecoveryPage />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/team" element={<TeamPage />} />
          <Route path="/project" element={<ProjectSubmissionPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/support" element={<SupportPage />} />
          <Route path="/judge" element={<JudgeDashboardPage />} />
          <Route path="/admin" element={<AdminDashboardPage />} />
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
