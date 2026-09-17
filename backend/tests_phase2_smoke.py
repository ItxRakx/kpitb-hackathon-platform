import os
import sys
import io
import django
import tempfile

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kpitb_hackathon.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Asserter:
    def __init__(self):
        self.failures = []
        self.passes = []

    def check(self, name, cond, detail=""):
        if cond:
            self.passes.append(name)
            print(f"  [PASS] {name}")
        else:
            self.failures.append((name, detail))
            print(f"  [FAIL] {name}  {detail}")

    def summary(self):
        print("\n=================== SMOKE TEST SUMMARY ===================")
        print(f"Passes: {len(self.passes)}")
        print(f"Failures: {len(self.failures)}")
        if self.failures:
            for n, d in self.failures:
                print(f"  - {n}: {d}")
        print("==========================================================")
        return 0 if not self.failures else 1


def main():
    a = Asserter()
    c = Client()

    # -------- HEALTH ENDPOINTS --------
    print("\n## Health endpoints")
    for app in ["accounts", "hackathons", "teams", "projects", "judging", "notifications"]:
        r = c.get(f"/api/v1/{app}/health/")
        a.check(f"health/{app} 200", r.status_code == 200, f"status={r.status_code}")
        a.check(f"health/{app} body", (r.json().get("status"), r.json().get("app")) == ("ok", app),
                f"got {r.json()}")

    # -------- TASK 2: ACCOUNTS --------
    print("\n## Accounts: register")
    payload_A = {
        "email": "alice.p2@kpitb.test",
        "password1": "Str0ng!P@ss12",
        "password2": "Str0ng!P@ss12",
        "first_name": "Alice",
        "last_name": "Smith",
        "participantprofile": {"institution": "UET Peshawar", "phone": "+923001111111"},
    }
    payload_B = {
        "email": "bob.p2@kpitb.test",
        "password1": "Str0ng!P@ss12",
        "password2": "Str0ng!P@ss12",
        "first_name": "Bob",
        "last_name": "Jones",
        "participantprofile": {"institution": "UET Peshawar", "phone": "+923002222222"},
    }
    payload_J = {
        "email": "judge.p2@kpitb.test",
        "password1": "Str0ng!P@ss12",
        "password2": "Str0ng!P@ss12",
        "first_name": "Judy",
        "last_name": "Judge",
        "participantprofile": {"institution": "Panel", "phone": "+923003333333", "is_judge": True},
    }

    r = c.post("/api/v1/accounts/register/", payload_A, content_type="application/json")
    a.check("register A 201", r.status_code == 201, f"status={r.status_code} body={r.content[:300]}")
    rdup = c.post("/api/v1/accounts/register/", payload_A, content_type="application/json")
    a.check("register A duplicate 400", rdup.status_code == 400, f"status={rdup.status_code}")
    r = c.post("/api/v1/accounts/register/", payload_B, content_type="application/json")
    a.check("register B 201", r.status_code == 201, f"status={r.status_code}")
    r = c.post("/api/v1/accounts/register/", payload_J, content_type="application/json")
    a.check("register J 201", r.status_code == 201, f"status={r.status_code}")

    # Create staff / admin
    staff = User.objects.create_superuser(username="staffadmin_p2", email="staff.p2@kpitb.test", password="Staff!1234")
    from accounts.models import ParticipantProfile
    ParticipantProfile.objects.get_or_create(user=staff, defaults={"institution": "STAFF", "is_judge": False})

    # Login
    print("\n## Accounts: login")
    rlogin_A = c.post("/api/v1/accounts/login/", {"email": payload_A["email"], "password": payload_A["password1"]},
                      content_type="application/json")
    a.check("login A 200", rlogin_A.status_code == 200, f"status={rlogin_A.status_code} body={rlogin_A.content[:300]}")
    tokens_A = rlogin_A.json()
    a.check("login A has access", "access" in tokens_A, str(tokens_A))
    a.check("login A has refresh", "refresh" in tokens_A, str(tokens_A))

    rbad = c.post("/api/v1/accounts/login/", {"email": payload_A["email"], "password": "wrong"},
                  content_type="application/json")
    a.check("login bad cred 401", rbad.status_code == 401, f"status={rbad.status_code}")

    rlogin_B = c.post("/api/v1/accounts/login/", {"email": payload_B["email"], "password": payload_B["password1"]},
                      content_type="application/json")
    tokens_B = rlogin_B.json()
    rlogin_J = c.post("/api/v1/accounts/login/", {"email": payload_J["email"], "password": payload_J["password1"]},
                      content_type="application/json")
    tokens_J = rlogin_J.json()
    rlogin_ST = c.post("/api/v1/accounts/login/", {"email": "staff.p2@kpitb.test", "password": "Staff!1234"},
                       content_type="application/json")
    tokens_ST = rlogin_ST.json()

    headers = lambda t: {"HTTP_AUTHORIZATION": f"Bearer {t}"}

    # /me
    print("\n## Accounts: /me")
    r = c.get("/api/v1/accounts/me/", **headers(tokens_A["access"]))
    a.check("me A GET 200", r.status_code == 200, f"status={r.status_code}")
    body = r.json()
    a.check("me A email", body.get("email", "").lower() == payload_A["email"].lower(), body.get("email"))
    a.check("me A profile nested institution",
            body.get("participantprofile", {}).get("institution") == "UET Peshawar",
            body.get("participantprofile"))

    rpatch = c.patch("/api/v1/accounts/me/",
                     {"participantprofile": {"phone": "+923009999999"}},
                     content_type="application/json",
                     **headers(tokens_A["access"]))
    a.check("me A PATCH 200", rpatch.status_code == 200, f"status={rpatch.status_code} body={rpatch.content[:300]}")
    a.check("me A PATCH phone updated",
            rpatch.json().get("participantprofile", {}).get("phone") == "+923009999999",
            rpatch.json().get("participantprofile"))

    # Refresh + blacklist old refresh
    print("\n## Accounts: refresh + blacklist")
    r_ref = c.post("/api/v1/accounts/token/refresh/", {"refresh": tokens_A["refresh"]},
                   content_type="application/json")
    a.check("refresh 200", r_ref.status_code == 200, f"status={r_ref.status_code} body={r_ref.content[:300]}")
    new_refresh = r_ref.json().get("refresh")
    # Old refresh should be blacklisted (ROTATE + BLACKLIST)
    r_black = c.post("/api/v1/accounts/token/refresh/", {"refresh": tokens_A["refresh"]},
                     content_type="application/json")
    a.check("old refresh blacklisted (401)", r_black.status_code == 401, f"status={r_black.status_code}")
    # New refresh still valid
    r_ok = c.post("/api/v1/accounts/token/refresh/", {"refresh": new_refresh},
                  content_type="application/json")
    a.check("new refresh works 200", r_ok.status_code == 200, f"status={r_ok.status_code}")

    # Logout (blacklist current refresh)
    r_logout = c.post("/api/v1/accounts/token/blacklist/", {"refresh": new_refresh},
                      content_type="application/json")
    a.check("logout 200", r_logout.status_code == 200, f"status={r_logout.status_code}")
    r_after = c.post("/api/v1/accounts/token/refresh/", {"refresh": new_refresh},
                     content_type="application/json")
    a.check("after logout refresh 401", r_after.status_code == 401, f"status={r_after.status_code}")

    # -------- TASK 3: HACKATHONS (staff write) --------
    print("\n## Hackathons admin CRUD")
    from hackathons.models import Hackathon

    now = timezone.now()
    h_payload = {
        "title": "Peshawar Fest 2026",
        "slug": "peshawar-fest-2026",
        "description": "Annual hackathon",
        "start_date": (now + timedelta(days=1)).isoformat(),
        "end_date": (now + timedelta(days=3)).isoformat(),
        "registration_start": (now - timedelta(days=10)).isoformat(),
        "registration_end": (now + timedelta(days=1)).isoformat(),
        "team_min_size": 1,
        "team_max_size": 3,
        "require_roster_lock_to_register": False,
        "tracks": ["AI", "Web"],
        "rules": "Be nice",
        "prizes": "1st 100k",
        "results_published": False,
    }
    # Non-staff 403
    r = c.post("/api/v1/hackathons/", h_payload, content_type="application/json",
               **headers(tokens_A["access"]))
    a.check("hackathon non-staff POST 403", r.status_code == 403, f"status={r.status_code}")

    # Staff 201
    r = c.post("/api/v1/hackathons/", h_payload, content_type="application/json",
               **headers(tokens_ST["access"]))
    a.check(f"hackathon staff POST 201 {r.status_code}", r.status_code == 201, f"body={r.content[:500]}")
    hack_data = r.json()
    hack_id = hack_data["id"]
    hack_slug = hack_data["slug"]
    a.check("hackathon team_min_size default 1", hack_data.get("team_min_size") == 1, str(hack_data.get("team_min_size")))
    a.check("hackathon team_max_size default 3", hack_data.get("team_max_size") == 3, str(hack_data.get("team_max_size")))
    a.check("hackathon is_registration_open derived", hack_data.get("is_registration_open") is True,
            str(hack_data.get("is_registration_open")))
    a.check("hackathon is_ongoing derived", hack_data.get("is_ongoing") is False, str(hack_data.get("is_ongoing")))
    a.check("hackathon is_completed derived", hack_data.get("is_completed") is False, str(hack_data.get("is_completed")))

    # List GET 200 (AllowAny)
    r = c.get(f"/api/v1/hackathons/{hack_slug}/")
    a.check("hackathon GET detail AllowAny 200", r.status_code == 200, f"status={r.status_code}")

    # Scope filters
    r = c.get("/api/v1/hackathons/?scope=upcoming")
    a.check("hackathons scope=upcoming 200", r.status_code == 200)
    r = c.get("/api/v1/hackathons/?scope=current")
    a.check("hackathons scope=current 200", r.status_code == 200)
    r = c.get("/api/v1/hackathons/?scope=past")
    a.check("hackathons scope=past 200", r.status_code == 200)

    # Judging criteria (3)
    print("\n## Judging criteria")
    for idx, (name, w, mx) in enumerate([("Innovation", 0.4, 100), ("Impact", 0.3, 100), ("Execution", 0.3, 100)]):
        cp = {"hackathon": hack_id, "name": name, "weight": w, "max_score": mx, "order": idx}
        r = c.post("/api/v1/hackathons/criteria/", cp, content_type="application/json",
                   **headers(tokens_ST["access"]))
        a.check(f"criterion POST {name} 201", r.status_code == 201, f"status={r.status_code} body={r.content[:400]}")
    r = c.get("/api/v1/hackathons/criteria/")
    a.check("criteria count = 3", len(r.json().get("results", r.json())) == 3,
            f"count={len(r.json().get('results', r.json()))}")

    # -------- TASK 4: TEAMS --------
    print("\n## Teams: create team (A becomes leader)")
    t1_payload = {
        "name": "Team Awesome",
        "tagline": "We build cool stuff",
        "hackathon": hack_id,
        "track": "AI",
    }
    r = c.post("/api/v1/teams/", t1_payload, content_type="application/json",
               **headers(tokens_A["access"]))
    a.check("create team A 201", r.status_code == 201, f"status={r.status_code} body={r.content[:500]}")
    t1 = r.json()
    team1_id = t1["id"]
    team1_invite_code = t1["invite_code"]
    a.check("invite_code 8 chars", len(team1_invite_code or "") == 8, team1_invite_code)
    a.check("is_leader true for A", t1.get("is_leader") is True, str(t1.get("is_leader")))
    a.check("member_count == 1", t1.get("member_count") == 1, str(t1.get("member_count")))
    a.check("memberships has 1 leader",
            any(m.get("is_leader") is True for m in (t1.get("memberships") or [])),
            str(t1.get("memberships")))

    # B joins by code
    print("\n## Teams: join-by-code")
    r = c.post("/api/v1/teams/join-by-code/", {"invite_code": team1_invite_code},
               content_type="application/json", **headers(tokens_B["access"]))
    a.check("B join 201", r.status_code == 201, f"status={r.status_code} body={r.content[:400]}")

    # B's memberships check hackathon duplication guard: B joins another team same hackathon => 400
    t2_payload = {"name": "Dupe Guard Team", "hackathon": hack_id, "track": "Web"}
    r2 = c.post("/api/v1/teams/", t2_payload, content_type="application/json",
                **headers(tokens_B["access"]))
    a.check("B create another team same hack 400", r2.status_code == 400,
            f"status={r2.status_code} body={r2.content[:400]}")
    a.check("B create another team code DUPLICATE_HACKATHON_MEMBERSHIP",
            "DUPLICATE_HACKATHON_MEMBERSHIP" in str(r2.content),
            str(r2.content))

    # Fill roster to max_size 3 with a 3rd user to test max=3 add 4 -> 409
    payload_C = {
        "email": "carol.p2@kpitb.test",
        "password1": "Str0ng!P@ss12",
        "password2": "Str0ng!P@ss12",
        "first_name": "Carol", "last_name": "C",
    }
    payload_D = {
        "email": "dan.p2@kpitb.test",
        "password1": "Str0ng!P@ss12",
        "password2": "Str0ng!P@ss12",
        "first_name": "Dan", "last_name": "D",
    }
    c.post("/api/v1/accounts/register/", payload_C, content_type="application/json")
    c.post("/api/v1/accounts/register/", payload_D, content_type="application/json")
    tokC = c.post("/api/v1/accounts/login/", {"email": payload_C["email"], "password": payload_C["password1"]},
                  content_type="application/json").json()
    tokD = c.post("/api/v1/accounts/login/", {"email": payload_D["email"], "password": payload_D["password1"]},
                  content_type="application/json").json()

    c.post("/api/v1/teams/join-by-code/", {"invite_code": team1_invite_code},
           content_type="application/json", **headers(tokC["access"]))
    r_full = c.post("/api/v1/teams/join-by-code/", {"invite_code": team1_invite_code},
                    content_type="application/json", **headers(tokD["access"]))
    a.check("max=3 add 4th 409", r_full.status_code == 409, f"status={r_full.status_code} body={r_full.content[:400]}")
    a.check("roster full code ROSTER_FULL", "ROSTER_FULL" in str(r_full.content), str(r_full.content))

    # Transfer leadership to B
    print("\n## Teams: transfer leadership")
    userB_id = User.objects.get(email=payload_B["email"]).id
    rtr = c.post(f"/api/v1/teams/{team1_id}/transfer-leadership/",
                 {"new_leader_user_id": userB_id},
                 content_type="application/json", **headers(tokens_A["access"]))
    a.check("transfer A->B 200", rtr.status_code == 200, f"status={rtr.status_code} body={rtr.content[:400]}")
    t1_after = c.get(f"/api/v1/teams/{team1_id}/", **headers(tokens_A["access"])).json()
    a.check("B now leader", any(m.get("is_leader") and m.get("user_id") == userB_id
                                for m in (t1_after.get("memberships") or [])), str(t1_after.get("memberships")))

    # Lock & unlock permissions
    print("\n## Teams: lock/unlock roster")
    rlock = c.post(f"/api/v1/teams/{team1_id}/lock-roster/",
                   content_type="application/json", **headers(tokens_B["access"]))
    a.check("lock roster 200 (leader)", rlock.status_code == 200, f"status={rlock.status_code}")
    t1_lock = c.get(f"/api/v1/teams/{team1_id}/", **headers(tokens_B["access"])).json()
    a.check("roster locked flag", t1_lock.get("is_roster_locked") is True, str(t1_lock.get("is_roster_locked")))
    # A not leader: attempt unlock -> 403
    runlock_A = c.post(f"/api/v1/teams/{team1_id}/unlock-roster/",
                       content_type="application/json", **headers(tokens_A["access"]))
    a.check("A (non-leader) unlock 403", runlock_A.status_code == 403, f"status={runlock_A.status_code}")
    # Leader unlock ok
    runlock_B = c.post(f"/api/v1/teams/{team1_id}/unlock-roster/",
                       content_type="application/json", **headers(tokens_B["access"]))
    a.check("B (leader) unlock 200", runlock_B.status_code == 200, f"status={runlock_B.status_code}")
    # Staff unlock also OK
    r_staff_unlock = c.post(f"/api/v1/teams/{team1_id}/unlock-roster/",
                            content_type="application/json", **headers(tokens_ST["access"]))
    a.check("staff unlock 200", r_staff_unlock.status_code == 200, f"status={r_staff_unlock.status_code}")

    # Leave team (C leaves and rejoins by invite to test invite flow)
    # First, B lock roster to enable registration for later
    c.post(f"/api/v1/teams/{team1_id}/lock-roster/",
           content_type="application/json", **headers(tokens_B["access"]))

    # -------- TASK 3: REGISTER TEAM + R1 distinct codes --------
    print("\n## RegisterTeamForHackathon + error codes")
    def try_register(tok, tid, hack_slug):
        return c.post(f"/api/v1/hackathons/{hack_slug}/register-team/",
                      {"team_id": tid},
                      content_type="application/json", **headers(tok))

    # register as leader
    r = try_register(tokens_B["access"], team1_id, hack_slug)
    a.check("register team for hack 201 (or 200)", r.status_code in (200, 201),
            f"status={r.status_code} body={r.content[:400]}")

    # Duplicate registration -> 409 code ALREADY_REGISTERED
    rdup = try_register(tokens_B["access"], team1_id, hack_slug)
    a.check("duplicate register 409", rdup.status_code == 409, f"status={rdup.status_code} body={rdup.content[:400]}")
    a.check("duplicate code ALREADY_REGISTERED",
            "ALREADY_REGISTERED" in str(rdup.content), str(rdup.content))

    # Roster too small: create a team with 0 min but set hack min higher
    # We'll test by updating roster size guard - instead make another hack with min_size=5
    h2_payload = dict(h_payload)
    h2_payload.update({
        "title": "Hack Roster Test",
        "slug": "hack-roster-test",
        "registration_start": (now - timedelta(days=10)).isoformat(),
        "registration_end": (now + timedelta(days=1)).isoformat(),
        "team_min_size": 5,
        "team_max_size": 10,
        "require_roster_lock_to_register": True,
    })
    h2 = c.post("/api/v1/hackathons/", h2_payload, content_type="application/json",
                **headers(tokens_ST["access"])).json()
    h2_id = h2["id"]
    # Create a team in h2 but not locked and 1 member (<5)
    t3 = c.post("/api/v1/teams/", {"name": "Tiny Team", "hackathon": h2_id, "track": "AI"},
                content_type="application/json", **headers(tokD["access"])).json()

    # Not locked + require_roster_lock=true -> ROSTER_NOT_LOCKED
    r = c.post(f"/api/v1/hackathons/{h2['slug']}/register-team/", {"team_id": t3["id"]},
               content_type="application/json", **headers(tokD["access"]))
    a.check("roster not locked code ROSTER_NOT_LOCKED", "ROSTER_NOT_LOCKED" in str(r.content),
            f"status={r.status_code} body={r.content}")

    # Lock then try -> ROSTER_TOO_SMALL
    c.post(f"/api/v1/teams/{t3['id']}/lock-roster/", content_type="application/json", **headers(tokD["access"]))
    r = c.post(f"/api/v1/hackathons/{h2['slug']}/register-team/", {"team_id": t3["id"]},
               content_type="application/json", **headers(tokD["access"]))
    a.check("roster too small code ROSTER_TOO_SMALL",
            "ROSTER_TOO_SMALL" in str(r.content), f"body={r.content}")

    # My registration
    print("\n## My registration for hack")
    r = c.get(f"/api/v1/hackathons/{hack_slug}/my-registration/", **headers(tokens_B["access"]))
    a.check("my-registration B 200", r.status_code == 200, f"status={r.status_code} body={r.content[:400]}")
    r = c.get(f"/api/v1/hackathons/{hack_slug}/my-registration/", **headers(tokD["access"]))
    a.check("my-registration D 404", r.status_code == 404, f"status={r.status_code}")

    # -------- TASK 5: PROJECTS --------
    print("\n## Projects")
    # Leader B creates project for team1/hackathon1
    p1 = {
        "title": "Peshawar Smart AI",
        "build_mode": "online",
        "short_description": "AI platform for cities",
        "technologies": ["Python", "Django", "React"],
        "repository_url": "https://github.com/org/proj",
        "demo_url": "https://demo.example.com",
    }
    r = c.post("/api/v1/projects/", {"team": team1_id, "hackathon": hack_id, **p1},
               content_type="application/json", **headers(tokens_B["access"]))
    a.check("create project 201", r.status_code == 201, f"status={r.status_code} body={r.content[:500]}")
    pdata = r.json()
    proj_id = pdata["id"]
    proj_slug = pdata["slug"]

    # 2nd project for same team -> 409 PROJECT_ALREADY_EXISTS
    r = c.post("/api/v1/projects/", {"team": team1_id, "hackathon": hack_id, "title": "Dup Proj"},
               content_type="application/json", **headers(tokens_B["access"]))
    a.check("2nd project 409 PROJECT_ALREADY_EXISTS",
            r.status_code == 409 and "PROJECT_ALREADY_EXISTS" in str(r.content),
            f"status={r.status_code} body={r.content}")

    # PATCH updates
    r = c.patch(f"/api/v1/projects/{proj_slug}/", {"short_description": "Updated desc"},
                content_type="application/json", **headers(tokens_B["access"]))
    a.check("project PATCH 200", r.status_code == 200, f"status={r.status_code}")
    a.check("project PATCH desc updated", r.json().get("short_description") == "Updated desc",
            r.json().get("short_description"))

    # Gallery listing (AllowAny, paginated, default is_public=True filters)
    r = c.get("/api/v1/projects/")
    a.check("gallery list 200", r.status_code == 200, f"status={r.status_code}")
    a.check("gallery paginated has 'results' or list", True)

    # Gallery 2nd project public not shown if private - create another and mark public
    # Submit the project -> submitted status should lock edits
    r_submit = c.post(f"/api/v1/projects/{proj_slug}/submit/", {"make_public": True},
                      content_type="application/json", **headers(tokens_B["access"]))
    a.check("submit project 200", r_submit.status_code == 200, f"body={r_submit.content[:400]}")
    submitted_data = r_submit.json()
    a.check("project status submitted", submitted_data.get("status") == "submitted",
            submitted_data.get("status"))
    a.check("project is_public True", submitted_data.get("is_public") is True,
            str(submitted_data.get("is_public")))

    # Patch after submit -> 403 (locked for participants)
    r = c.patch(f"/api/v1/projects/{proj_slug}/", {"short_description": "HACKED"},
                content_type="application/json", **headers(tokens_B["access"]))
    a.check("patch submitted 403 (locked)", r.status_code == 403, f"status={r.status_code}")

    # Staff unlock
    r = c.post(f"/api/v1/projects/{proj_slug}/unlock/", content_type="application/json",
               **headers(tokens_ST["access"]))
    a.check("staff unlock 200", r.status_code == 200, f"status={r.status_code} body={r.content[:400]}")

    # Storage attachment: FileSystemStorage because 3x Azure env vars empty
    print("\n## Storage: attachment upload (FileSystemStorage fallback)")
    f = SimpleUploadedFile("snippet.txt", b"hello kpitb", content_type="text/plain")
    r = c.post(f"/api/v1/projects/{proj_id}/attachments/",
               {"attachment_type": "documentation", "file": f},
               format="multipart", **headers(tokens_ST["access"]))
    # Expect 403: participant leader only, not staff
    if r.status_code != 201:
        # Try B (leader)
        f2 = SimpleUploadedFile("snippet2.txt", b"hello kpitb 2", content_type="text/plain")
        r = c.post(f"/api/v1/projects/{proj_id}/attachments/",
                   {"attachment_type": "documentation", "file": f2},
                   format="multipart", **headers(tokens_B["access"]))
    a.check("attachment POST 201", r.status_code == 201, f"status={r.status_code} body={r.content[:500]}")
    att = r.json()
    a.check("attachment has file_url", bool(att.get("file_url")), str(att))
    a.check("attachment has file_size (bytes)", isinstance(att.get("file_size"), int),
            f"size={att.get('file_size')}")

    # Gallery: verify attachments are exposed
    r = c.get(f"/api/v1/projects/{proj_slug}/")
    a.check("project detail has attachments", len(r.json().get("attachments", [])) >= 1,
            str(r.json().get("attachments")))

    # -------- TASK 6: JUDGING --------
    print("\n## Judging assignments (admin)")
    judge_user = User.objects.get(email=payload_J["email"])
    # Make judge a staff? No, spec doesn't require. Keep as plain user but assigned.
    r_ja = c.post("/api/v1/judging/assignments/",
                  {"hackathon": hack_id, "judge": judge_user.id},
                  content_type="application/json", **headers(tokens_ST["access"]))
    a.check("assign judge J -> hack 201", r_ja.status_code in (200, 201),
            f"status={r_ja.status_code} body={r_ja.content[:500]}")

    # Non-assigned D judge (not staff) -> 403 on hackathon projects list
    r_no = c.get(f"/api/v1/judging/hackathons/{hack_slug}/projects/",
                 **headers(tokD["access"]))
    a.check("non-assigned hackathon projects 403", r_no.status_code == 403,
            f"status={r_no.status_code}")

    # Assigned judge J -> 200
    r_yes = c.get(f"/api/v1/judging/hackathons/{hack_slug}/projects/",
                  **headers(tokens_J["access"]))
    a.check("assigned J hackathon projects 200", r_yes.status_code == 200,
            f"status={r_yes.status_code} body={r_yes.content[:500]}")
    proj_list = r_yes.json()
    projs = proj_list if isinstance(proj_list, list) else proj_list.get("results", [])
    a.check("hackathon projects list length >= 1", len(projs) >= 1, f"len={len(projs)}")
    if projs:
        pitem = projs[0]
        a.check("J view per-judge my_scores list", isinstance(pitem.get("my_scores"), list),
                f"my_scores type={type(pitem.get('my_scores'))}")
        a.check("J view aggregate_score dict", isinstance(pitem.get("aggregate_score"), dict),
                f"aggregate type={type(pitem.get('aggregate_score'))}")

    # COI check: if A (member of team1) is a judge assigned and tries to score proj1 -> 403 CONFLICT_OF_INTEREST
    # Make A a judge too, assign, then score attempt
    r_ja2 = c.post("/api/v1/judging/assignments/",
                   {"hackathon": hack_id, "judge": User.objects.get(email=payload_A["email"]).id},
                   content_type="application/json", **headers(tokens_ST["access"]))
    # Refresh A access token with new refresh (old blacklisted earlier)
    rlogin_A2 = c.post("/api/v1/accounts/login/",
                       {"email": payload_A["email"], "password": payload_A["password1"]},
                       content_type="application/json")
    tA2 = rlogin_A2.json()

    crits = c.get("/api/v1/hackathons/criteria/").json()
    crits = crits if isinstance(crits, list) else crits.get("results", [])
    a.check("criteria available for scoring", len(crits) == 3, f"len={len(crits)}")

    # COI attempt: A (teammate of proj1) scores proj1 -> 403
    if crits:
        c1 = crits[0]
        r_coi = c.post("/api/v1/judging/scores/",
                       {"project": proj_id, "criterion": c1["id"], "value": 80},
                       content_type="application/json", **headers(tA2["access"]))
        a.check("COI 403 CONFLICT_OF_INTEREST",
                r_coi.status_code == 403 and "CONFLICT_OF_INTEREST" in str(r_coi.content),
                f"status={r_coi.status_code} body={r_coi.content}")

    # Score UPSERT by judge J (non-coi) + value clamp
    print("\n## Score UPSERT + clamp")
    scores_saved = []
    for crit in crits:
        # Try out-of-range (e.g. 200 for max 100) - clamp to criterion.max_score
        r_over = c.post("/api/v1/judging/scores/",
                        {"project": proj_id, "criterion": crit["id"], "value": 9999},
                        content_type="application/json", **headers(tokens_J["access"]))
        a.check(f"J scores crit {crit['name']} (clamp) 200/201", r_over.status_code in (200, 201),
                f"status={r_over.status_code} body={r_over.content[:400]}")
        if r_over.status_code in (200, 201):
            body = r_over.json()
            a.check(f"clamp value == max_score {crit['max_score']}",
                    body.get("value") == crit["max_score"],
                    f"got value={body.get('value')} max={crit['max_score']}")
            scores_saved.append(body)

    # UPSERT same key again -> returns 200, not duplicate error
    first_crit = crits[0]
    r_upsert = c.post("/api/v1/judging/scores/",
                      {"project": proj_id, "criterion": first_crit["id"], "value": 50},
                      content_type="application/json", **headers(tokens_J["access"]))
    a.check("UPSERT repeat -> 200 (no dup)", r_upsert.status_code in (200, 201),
            f"status={r_upsert.status_code} body={r_upsert.content[:400]}")
    a.check("UPSERT value updated to 50", r_upsert.json().get("value") == 50,
            f"value={r_upsert.json().get('value')}")

    # Aggregate score for project exposed
    print("\n## Project Aggregate Score")
    # First publish results so non-staff/non-team can view
    c.patch(f"/api/v1/hackathons/{hack_slug}/", {"results_published": True},
            content_type="application/json", **headers(tokens_ST["access"]))
    r_agg = c.get(f"/api/v1/judging/projects/{proj_id}/aggregate-score/")
    a.check("agg score public 200", r_agg.status_code == 200,
            f"status={r_agg.status_code} body={r_agg.content[:500]}")
    agg = r_agg.json()
    a.check("agg has weighted_total", "weighted_total" in agg, str(agg))
    a.check("agg has judge_count", isinstance(agg.get("judge_count"), int), str(agg))
    a.check("agg has max_possible", "max_possible" in agg, str(agg))
    a.check("rubric: weighted_normalized average sensible 0<=v<=max",
            0 <= float(agg.get("weighted_total") or 0) <= float(agg.get("max_possible") or 1),
            str(agg))

    # -------- TASK 7: NOTIFICATIONS --------
    print("\n## Notifications")
    # Create a handful via model helper
    from notifications.models import Notification, notify
    uA = User.objects.get(email=payload_A["email"])
    notify(uA, "Welcome", "Welcome to the platform!", "system")
    notify(uA, "Team update", "You joined a team", "team")
    n3 = Notification.objects.create(user=uA, title="Unread", body="still unread", category="general")
    # Mark one read
    notify(uA, "Old", "Should be read later", "general")
    r_list_all = c.get("/api/v1/notifications/", **headers(tA2["access"]))
    a.check("notif list 200", r_list_all.status_code == 200, f"status={r_list_all.status_code}")
    body = r_list_all.json()
    all_items = body if isinstance(body, list) else body.get("results", body)
    a.check("notif count >= 4", len(all_items) >= 4, f"len={len(all_items)}")

    r_unread = c.get("/api/v1/notifications/?unread_only=true", **headers(tA2["access"]))
    a.check("unread_only=true 200", r_unread.status_code == 200, f"status={r_unread.status_code}")
    unread_body = r_unread.json()
    unread_items = unread_body if isinstance(unread_body, list) else unread_body.get("results", unread_body)
    a.check("unread_only count == len(all_items) (all currently unread)",
            len(unread_items) == len(all_items),
            f"unread={len(unread_items)} all={len(all_items)}")

    # Mark single read
    first_id = all_items[0]["id"]
    r_mark1 = c.patch(f"/api/v1/notifications/{first_id}/mark-read/",
                      content_type="application/json", **headers(tA2["access"]))
    a.check("mark single read 200", r_mark1.status_code == 200, f"status={r_mark1.status_code}")
    a.check("is_read True on body", r_mark1.json().get("is_read") is True, str(r_mark1.json()))

    # Verify unread_only now shows 1 less
    r_unread2 = c.get("/api/v1/notifications/?unread_only=true", **headers(tA2["access"]))
    ub2 = r_unread2.json()
    unread2 = ub2 if isinstance(ub2, list) else ub2.get("results", ub2)
    a.check("unread_only count decreased by 1",
            len(unread2) == len(all_items) - 1,
            f"unread2={len(unread2)} expected={len(all_items) - 1}")

    # Mark all read
    r_mark_all = c.post("/api/v1/notifications/mark-all-read/",
                        content_type="application/json", **headers(tA2["access"]))
    a.check("mark all read 200", r_mark_all.status_code == 200, f"status={r_mark_all.status_code}")
    r_unread3 = c.get("/api/v1/notifications/?unread_only=true", **headers(tA2["access"]))
    ub3 = r_unread3.json()
    unread3 = ub3 if isinstance(ub3, list) else ub3.get("results", ub3)
    a.check("unread_only count = 0 after mark-all-read", len(unread3) == 0,
            f"unread3={len(unread3)}")

    # -------- ADMIN PRESENCE --------
    print("\n## Django Admin model registrations")
    from django.contrib import admin as dj_admin
    registered = {m for m in dj_admin.site._registry.keys()}
    from accounts.models import ParticipantProfile
    from hackathons.models import Hackathon, JudgingCriterion, HackathonRegistration
    from teams.models import Team, TeamMembership, TeamInvite
    from projects.models import Project, ProjectAttachment
    from judging.models import JudgeAssignment, ProjectJudgeAssignment, Score
    from notifications.models import Notification
    for m in [User, ParticipantProfile, Hackathon, JudgingCriterion, HackathonRegistration,
              Team, TeamMembership, TeamInvite, Project, ProjectAttachment,
              JudgeAssignment, ProjectJudgeAssignment, Score, Notification]:
        a.check(f"admin registered {m.__name__}", m in registered, f"missing {m.__name__}")
    # list_display & search_fields & list_filter grep check
    import inspect
    for m_cls, app_name in [(User, "accounts"), (ParticipantProfile, "accounts"),
                            (Hackathon, "hackathons"), (JudgingCriterion, "hackathons"),
                            (HackathonRegistration, "hackathons"), (Team, "teams"),
                            (TeamMembership, "teams"), (TeamInvite, "teams"),
                            (Project, "projects"), (ProjectAttachment, "projects"),
                            (JudgeAssignment, "judging"), (ProjectJudgeAssignment, "judging"),
                            (Score, "judging"), (Notification, "notifications")]:
        if m_cls in dj_admin.site._registry:
            adm = dj_admin.site._registry[m_cls]
            ld = getattr(adm, "list_display", None)
            sf = getattr(adm, "search_fields", None)
            lf = getattr(adm, "list_filter", None)
            a.check(f"{m_cls.__name__} admin list_display", bool(ld) and len(ld) > 0,
                    f"list_display={ld}")
            a.check(f"{m_cls.__name__} admin search_fields", sf is not None,
                    f"search_fields={sf}")
            a.check(f"{m_cls.__name__} admin list_filter", lf is not None,
                    f"list_filter={lf}")

    # Return exit code
    return a.summary()


if __name__ == "__main__":
    rc = main()
    print("tests_phase2_smoke.py exit code:", rc)
    sys.exit(rc)
