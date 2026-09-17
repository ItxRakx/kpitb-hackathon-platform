from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from hackathons.models import (
    Hackathon, HackathonRegistration, JudgingCriterion,
    ParticipantEnrollment, ProblemStatement,
)
from judging.models import JudgeAssignment
from projects.models import Project
from teams.models import Team, TeamMembership

User = get_user_model()


class Command(BaseCommand):
    help = "Create safe, repeatable demo data for local development."

    def handle(self, *args, **options):
        now = timezone.now()
        hackathon, _ = Hackathon.objects.get_or_create(
            slug="kpitb-ai-builders-2026",
            defaults={
                "title": "KPITB AI Builders 2026",
                "tagline": "Build useful technology for Khyber Pakhtunkhwa.",
                "description": "A demo hackathon record for local development.",
                "starts_at": now + timedelta(days=14),
                "ends_at": now + timedelta(days=16),
                "registration_opens_at": now - timedelta(days=2),
                "registration_closes_at": now + timedelta(days=10),
                "team_min_size": 1,
                "team_max_size": 6,
                "tracks": ["AI for Good", "Civic Technology", "Future of Work"],
                "rules": "Demo seed data. Replace before production.",
                "prizes_text": "Demo prizes",
            },
        )

        criteria = [
            ("Innovation", 0.25),
            ("Technical Implementation", 0.25),
            ("Impact", 0.2),
            ("Feasibility", 0.15),
            ("Presentation", 0.15),
        ]
        for order, (name, weight) in enumerate(criteria):
            JudgingCriterion.objects.get_or_create(
                hackathon=hackathon,
                name=name,
                defaults={"weight": weight, "max_score": 100, "order": order},
            )

        problem_specs = [
            {
                "title": "Make public services easier to access",
                "category": "GovTech",
                "summary": "Help citizens discover requirements, offices, and status updates for a high-demand public service.",
                "description": "Design an accessible digital service that reduces confusion, repeat visits, and time spent finding reliable government service information.",
                "deliverables": "Working prototype, user journey, data approach, and a short impact measurement plan.",
                "difficulty": "intermediate",
            },
            {
                "title": "Early warning for climate and disaster risks",
                "category": "Climate Resilience",
                "summary": "Turn available weather and local reports into clear, timely community alerts.",
                "description": "Build a prototype that communicates risk to people with different languages, literacy levels, and connectivity conditions.",
                "deliverables": "Alert workflow, prototype, sample data, and an offline or low-bandwidth fallback.",
                "difficulty": "advanced",
            },
            {
                "title": "Connect youth skills to local opportunities",
                "category": "Future of Work",
                "summary": "Match young people across KP with projects, mentors, internships, or teams based on demonstrated skills.",
                "description": "Create a fair skills-first experience that helps users show what they can do and find relevant local opportunities.",
                "deliverables": "Participant profile, matching experience, working prototype, and fairness considerations.",
                "difficulty": "starter",
            },
        ]
        problems = []
        for spec in problem_specs:
            problem, _ = ProblemStatement.objects.update_or_create(
                hackathon=hackathon,
                title=spec["title"],
                defaults={**spec, "is_published": True},
            )
            problems.append(problem)

        participant, _ = User.objects.get_or_create(
            username="demo-participant",
            defaults={"email": "participant.demo@kpitb.test", "first_name": "Demo", "last_name": "Participant"},
        )
        participant.set_password("DemoPass!123")
        participant.save(update_fields=["password"])
        participant.profile.institution = "KPITB Demo University"
        participant.profile.phone = "+92 300 0000000"
        participant.profile.district = "Peshawar"
        participant.profile.education_level = "undergraduate"
        participant.profile.skills = ["React", "Django", "UX research"]
        participant.profile.is_verified = True
        participant.profile.save(update_fields=[
            "institution", "phone", "district", "education_level", "skills",
            "is_verified", "updated_at"
        ])
        ParticipantEnrollment.objects.update_or_create(
            hackathon=hackathon,
            user=participant,
            defaults={
                "selected_problem": problems[0],
                "participation_preference": "create_team",
                "primary_role": "developer",
                "experience_level": "intermediate",
                "attendance_mode": "flexible",
                "motivation": "Build a useful civic technology prototype for KP.",
                "agreed_to_rules": True,
                "status": "registered",
            },
        )

        judge, _ = User.objects.get_or_create(
            username="demo-judge",
            defaults={"email": "judge.demo@kpitb.test", "first_name": "Demo", "last_name": "Judge"},
        )
        judge.set_password("DemoPass!123")
        judge.save(update_fields=["password"])
        judge.profile.is_judge = True
        judge.profile.is_verified = True
        judge.profile.save(update_fields=["is_judge", "is_verified", "updated_at"])
        JudgeAssignment.objects.get_or_create(hackathon=hackathon, judge=judge)

        team, _ = Team.objects.get_or_create(
            hackathon=hackathon,
            name="Demo Builders",
            defaults={
                "tagline": "Seeded local development team.",
                "track": "AI for Good",
                "problem_statement": problems[0],
                "created_by": participant,
            },
        )
        if not team.problem_statement_id:
            team.problem_statement = problems[0]
            team.save(update_fields=["problem_statement", "updated_at"])
        TeamMembership.objects.get_or_create(team=team, user=participant, defaults={"is_leader": True, "role": "leader"})
        HackathonRegistration.objects.get_or_create(hackathon=hackathon, team=team, defaults={"registered_by": participant, "status": "confirmed"})
        project, created = Project.objects.get_or_create(
            team=team,
            defaults={
                "hackathon": hackathon,
                "problem_statement": problems[0],
                "title": "Demo Civic Lens",
                "tagline": "Make local service information easier to understand.",
                "short_description": "Seeded project for local development.",
                "description": "This is demo seed data and should be replaced before production.",
                "track": "AI for Good",
                "build_mode": "online",
                "technologies": ["React", "Django", "AI"],
                "repo_url": "https://github.com/example/civic-lens",
                "is_public": True,
                "status": "submitted",
                "submitted_at": now,
            },
        )
        if not created and project.hackathon_id != hackathon.id:
            self.stderr.write(self.style.WARNING("Existing team project was preserved."))
        elif not project.problem_statement_id:
            project.problem_statement = problems[0]
            project.save(update_fields=["problem_statement", "updated_at"])

        self.stdout.write(self.style.SUCCESS("Seed data is ready."))
        self.stdout.write("Demo participant: participant.demo@kpitb.test / DemoPass!123")
        self.stdout.write("Demo judge: judge.demo@kpitb.test / DemoPass!123")
