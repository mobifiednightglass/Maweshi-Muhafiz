"""
End-to-end smoke test for the Maweshi Muhafiz backend.

Runs against a LIVE server (default http://127.0.0.1:5000) and exercises
the real request/response contract of:

    GET    /api/health
    POST   /api/auth/signup           {name, email, password}
    POST   /api/auth/login            {email, password}
    GET    /api/auth/me               Bearer token
    POST   /api/animals               {name, animal_type, ...}
    GET    /api/animals
    GET    /api/animals/<id>
    PUT    /api/animals/<id>
    DELETE /api/animals/<id>
    POST   /api/animals/<id>/assessments      multipart: image + symptoms
    GET    /api/animals/<id>/assessments
    GET    /api/assessments/<id>
    GET    /api/images/<image_id>             raw image bytes
    GET    /api/animals/<id>/assessments/compare?assessment_id_1&assessment_id_2
    POST   /api/animals/<id>/reminders        {reminder_type, due_date, notes?}
    GET    /api/animals/<id>/reminders
    DELETE /api/reminders/<reminder_id>

Response contract (all JSON endpoints):
    success → {"success": true,  "message": "...", "data": ...}
    error   → {"success": false, "message": "...", "error":  "..."}
    auth    → Authorization: Bearer <token>   (signup/login return "token",
              NOT "access_token"; ids are "id", NOT "_id")

Usage:
    1. Start the server:  venv/Scripts/python.exe run.py
    2. Run this script:   venv/Scripts/python.exe e2e_test.py
       (override target with E2E_BASE_URL, e.g. http://127.0.0.1:5000/api)

Note: the AI assessment may return a safe fallback ("status": "failed")
when no valid GEMINI_API_KEY is configured — the HTTP response is still
200 with a full record, so that is treated as success here.
"""

import os
import sys
import time

import cv2
import numpy as np
import requests

BASE_URL = os.environ.get("E2E_BASE_URL", "http://127.0.0.1:5000/api")

_password = "e2e-password-123"
_passed = 0
_failed = 0


def check(name, condition, detail=""):
    global _passed, _failed
    if condition:
        _passed += 1
        print(f"  PASS  {name}")
    else:
        _failed += 1
        print(f"  FAIL  {name}" + (f"  [{detail}]" if detail else ""))


def section(title):
    print(f"\n=== {title} ===")


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


def make_test_jpeg():
    """Bright, noisy 400x400 JPEG — passes the quality gate
    (min 200x200 resolution, mean brightness >= 50)."""
    rng = np.random.default_rng(42)
    img = np.full((400, 400, 3), 160, dtype=np.uint8)
    img = cv2.add(img, rng.integers(0, 60, size=img.shape, dtype=np.uint8))
    ok, buf = cv2.imencode(".jpg", img)
    if not ok:
        raise RuntimeError("could not encode test image")
    return buf.tobytes()


def main():
    global _passed, _failed
    session = requests.Session()

    # ------------------------------------------------------------------ preflight
    section("Preflight")
    try:
        resp = session.get(f"{BASE_URL}/health", timeout=10)
    except requests.RequestException as exc:
        print(f"\nERROR: cannot reach {BASE_URL} — is the server running?")
        print(f"       Start it with:  venv/Scripts/python.exe run.py")
        print(f"       ({exc})")
        return 1
    check("GET /health -> 200", resp.status_code == 200, f"got {resp.status_code}")
    check(
        "GET /health -> success envelope",
        resp.json().get("success") is True,
        resp.text[:200],
    )

    # ------------------------------------------------------------------ auth
    section("Auth (POST /auth/signup, /auth/login, GET /auth/me)")
    email = f"e2e-{int(time.time())}-{os.getpid()}@example.com"
    signup_body = {"name": "E2E Tester", "email": email, "password": _password}

    resp = session.post(f"{BASE_URL}/auth/signup", json=signup_body)
    body = resp.json()
    check("signup -> 201", resp.status_code == 201, f"got {resp.status_code}: {body}")
    check("signup -> data.token (key 'token')", isinstance(body.get("data", {}).get("token"), str) and len(body["data"]["token"]) > 20, str(body)[:200])
    check("signup -> data.user.id (key 'id')", isinstance(body.get("data", {}).get("user", {}).get("id"), str), str(body)[:200])
    check("signup -> no password_hash leaked", "password_hash" not in body.get("data", {}).get("user", {}))

    token = body["data"]["token"]
    user_id = body["data"]["user"]["id"]

    resp = session.post(f"{BASE_URL}/auth/signup", json=signup_body)
    check("duplicate signup -> 409", resp.status_code == 409, f"got {resp.status_code}")

    resp = session.post(f"{BASE_URL}/auth/login", json={"email": email, "password": _password})
    body = resp.json()
    check("login -> 200", resp.status_code == 200, f"got {resp.status_code}: {body}")
    check("login -> data.token", isinstance(body.get("data", {}).get("token"), str))
    check("login -> data.user.id matches signup", body.get("data", {}).get("user", {}).get("id") == user_id)

    resp = session.post(f"{BASE_URL}/auth/login", json={"email": email, "password": "wrong-password"})
    check("login wrong password -> 401", resp.status_code == 401, f"got {resp.status_code}")

    resp = session.get(f"{BASE_URL}/auth/me", headers=bearer(token))
    body = resp.json()
    check("GET /auth/me -> 200", resp.status_code == 200)
    check("GET /auth/me -> data.email matches", body.get("data", {}).get("email") == email)

    resp = session.get(f"{BASE_URL}/auth/me")
    check("GET /auth/me without token -> 401", resp.status_code == 401, f"got {resp.status_code}")

    auth = bearer(token)

    # ------------------------------------------------------------------ animals
    section("Animals (POST/GET/PUT/DELETE /animals)")
    payload = {
        "name": "Bholu",
        "animal_type": "Cow",
        "breed": "Sahiwal",
        "gender": "male",
        "age": 4,
        "weight": 450.5,
        "color": "brown",
        "health_status": "healthy",
        "region": "Punjab",
        "notes": "E2E test animal",
    }
    resp = session.post(f"{BASE_URL}/animals", json=payload, headers=auth)
    body = resp.json()
    animal = body.get("data", {})
    check("create animal -> 201", resp.status_code == 201, f"got {resp.status_code}: {body}")
    check("create -> data.id is a string (key 'id', not '_id')", isinstance(animal.get("id"), str), str(animal)[:200])
    check("create -> data.user_id set from token", animal.get("user_id") == user_id, f"got {animal.get('user_id')!r}")
    check("create -> fields echoed", animal.get("name") == "Bholu" and animal.get("animal_type") == "Cow" and animal.get("region") == "Punjab")
    check("create -> timestamps present", bool(animal.get("created_at")) and bool(animal.get("updated_at")))

    animal_id = animal["id"]

    resp = session.post(f"{BASE_URL}/animals", json={"animal_type": "Goat"}, headers=auth)
    check("create without name -> 400", resp.status_code == 400, f"got {resp.status_code}")

    resp = session.get(f"{BASE_URL}/animals", headers=auth)
    body = resp.json()
    check("list animals -> 200", resp.status_code == 200)
    check("list -> contains created animal", any(a.get("id") == animal_id for a in body.get("data", [])))

    resp = session.get(f"{BASE_URL}/animals/{animal_id}", headers=auth)
    check("get animal -> 200 and id matches", resp.status_code == 200 and resp.json().get("data", {}).get("id") == animal_id)

    resp = session.get(f"{BASE_URL}/animals/000000000000000000000000", headers=auth)
    check("get nonexistent animal -> 404", resp.status_code == 404, f"got {resp.status_code}")

    resp = session.put(f"{BASE_URL}/animals/{animal_id}", json={"name": "Bholu Jr", "health_status": "recovering"}, headers=auth)
    body = resp.json()
    check("update animal -> 200", resp.status_code == 200, f"got {resp.status_code}: {body}")
    check("update -> name changed, animal_type untouched", body.get("data", {}).get("name") == "Bholu Jr" and body.get("data", {}).get("animal_type") == "Cow")

    # ------------------------------------------------------ health assessments
    section("Health assessments (multipart POST, list, get, image, compare)")
    image_bytes = make_test_jpeg()

    resp = session.post(
        f"{BASE_URL}/animals/{animal_id}/assessments",
        headers=auth,
        data={"symptoms": "Limping on front left leg, slight swelling."},
        files={"image": ("leg.jpg", image_bytes, "image/jpeg")},
    )
    body = resp.json()
    a1 = body.get("data", {})
    check("create assessment -> 200", resp.status_code == 200, f"got {resp.status_code}: {str(body)[:300]}")
    check("assessment -> data.id present", isinstance(a1.get("id"), str))
    check("assessment -> image_ids non-empty (image references)", isinstance(a1.get("image_ids"), list) and len(a1["image_ids"]) == 1, str(a1.get("image_ids")))
    check("assessment -> symptoms echoed", a1.get("symptoms") == "Limping on front left leg, slight swelling.")
    check("assessment -> status completed or failed (AI fallback ok)", a1.get("status") in ("completed", "failed"), f"got {a1.get('status')!r}")
    check("assessment -> diagnosis_result is a dict", isinstance(a1.get("diagnosis_result"), dict))
    check("assessment -> red-flag fields present", "is_red_flag" in a1 and "red_flag_reasons" in a1)

    resp = session.post(
        f"{BASE_URL}/animals/{animal_id}/assessments",
        headers=auth,
        data={"symptoms": "No visible improvement, still favoring the leg."},
        files={"image": ("leg2.jpg", image_bytes, "image/jpeg")},
    )
    a2 = resp.json().get("data", {})
    check("second assessment -> 200", resp.status_code == 200, f"got {resp.status_code}")

    resp = session.post(
        f"{BASE_URL}/animals/{animal_id}/assessments",
        headers=auth,
        files={"image": ("leg.jpg", image_bytes, "image/jpeg")},  # no symptoms field
    )
    check("assessment without symptoms -> 400", resp.status_code == 400, f"got {resp.status_code}")

    resp = session.get(f"{BASE_URL}/animals/{animal_id}/assessments", headers=auth)
    body = resp.json()
    ids = [a.get("id") for a in body.get("data", [])]
    check("list assessments -> 200 with both records", resp.status_code == 200 and a1.get("id") in ids and a2.get("id") in ids, f"ids={ids}")

    resp = session.get(f"{BASE_URL}/assessments/{a1['id']}", headers=auth)
    check("get single assessment -> 200 and id matches", resp.status_code == 200 and resp.json().get("data", {}).get("id") == a1["id"])

    resp = session.get(f"{BASE_URL}/images/{a1['image_ids'][0]}", headers=auth)
    check("get image -> 200 raw bytes", resp.status_code == 200 and len(resp.content) > 0, f"got {resp.status_code}")
    check("get image -> Content-Type image/jpeg", resp.headers.get("Content-Type", "").startswith("image/jpeg"), resp.headers.get("Content-Type"))
    check("get image -> bytes match uploaded file", resp.content == image_bytes, f"{len(resp.content)} vs {len(image_bytes)} bytes")

    resp = session.get(
        f"{BASE_URL}/animals/{animal_id}/assessments/compare",
        params={"assessment_id_1": a1["id"], "assessment_id_2": a2["id"]},
        headers=auth,
    )
    body = resp.json()
    data = body.get("data", {})
    check("compare -> 200", resp.status_code == 200, f"got {resp.status_code}: {str(body)[:300]}")
    check(
        "compare -> data.assessment_1 / data.assessment_2 with full records",
        data.get("assessment_1", {}).get("id") == a1["id"]
        and data.get("assessment_2", {}).get("id") == a2["id"]
        and isinstance(data.get("assessment_1", {}).get("image_ids"), list),
    )

    resp = session.get(
        f"{BASE_URL}/animals/{animal_id}/assessments/compare",
        params={"assessment_id_2": a2["id"]},
        headers=auth,
    )
    check("compare missing assessment_id_1 -> 400", resp.status_code == 400, f"got {resp.status_code}")

    # ------------------------------------------------------------------ reminders
    section("Reminders (POST/GET /animals/<id>/reminders, DELETE /reminders/<id>)")
    reminder_payload = {
        "reminder_type": "vaccination",
        "due_date": "2030-01-15",
        "notes": "Foot and mouth booster",
    }
    resp = session.post(f"{BASE_URL}/animals/{animal_id}/reminders", json=reminder_payload, headers=auth)
    body = resp.json()
    reminder = body.get("data", {})
    check("create reminder -> 201", resp.status_code == 201, f"got {resp.status_code}: {body}")
    check("reminder -> data.id present", isinstance(reminder.get("id"), str))
    check("reminder -> server-set user_id / animal_id", reminder.get("user_id") == user_id and reminder.get("animal_id") == animal_id, f"got {reminder.get('user_id')!r}/{reminder.get('animal_id')!r}")
    check("reminder -> fields echoed", reminder.get("reminder_type") == "vaccination" and reminder.get("due_date") == "2030-01-15")

    resp = session.post(f"{BASE_URL}/animals/{animal_id}/reminders", json={"reminder_type": "deworming"}, headers=auth)
    check("reminder without due_date -> 400", resp.status_code == 400, f"got {resp.status_code}")

    resp = session.get(f"{BASE_URL}/animals/{animal_id}/reminders", headers=auth)
    body = resp.json()
    check("list reminders -> 200 with one record", resp.status_code == 200 and len(body.get("data", [])) == 1, f"got {len(body.get('data', []))}")

    resp = session.delete(f"{BASE_URL}/reminders/{reminder['id']}", headers=auth)
    check("delete reminder -> 200", resp.status_code == 200, f"got {resp.status_code}")

    resp = session.delete(f"{BASE_URL}/reminders/{reminder['id']}", headers=auth)
    check("delete same reminder again -> 404", resp.status_code == 404, f"got {resp.status_code}")

    resp = session.get(f"{BASE_URL}/animals/{animal_id}/reminders", headers=auth)
    check("list reminders after delete -> empty", resp.status_code == 200 and resp.json().get("data") == [])

    # ------------------------------------------------------------------ cleanup
    section("Cleanup")
    resp = session.delete(f"{BASE_URL}/animals/{animal_id}", headers=auth)
    check("delete animal -> 200", resp.status_code == 200, f"got {resp.status_code}")
    resp = session.get(f"{BASE_URL}/animals/{animal_id}", headers=auth)
    check("deleted animal -> 404 afterwards", resp.status_code == 404, f"got {resp.status_code}")

    # ------------------------------------------------------------------ summary
    print(f"\n{'=' * 60}")
    print(f"RESULT: {_passed} passed, {_failed} failed")
    print("=" * 60)
    return 1 if _failed else 0


if __name__ == "__main__":
    sys.exit(main())
