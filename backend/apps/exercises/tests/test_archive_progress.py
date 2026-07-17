"""Archive progress API — ticking a past BAC problem off in /arhiva.

The archive itself is static files nginx serves, so this endpoint is the only thing
the server knows about a student's way through it. Run with:

    python manage.py test apps.exercises.tests.test_archive_progress
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.exercises.models import ArchiveCompletion

URL = "/api/v1/exercises/arhiva/progress/"
PROBLEM = "mate-info-1-1/2026-model-114"

User = get_user_model()


class ArchiveProgressTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="elev@example.com", username="elev", password="pw12345!"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_requires_authentication(self):
        # The ticks are per-account; a visitor has nowhere to put them.
        anon = APIClient()
        self.assertEqual(anon.get(URL).status_code, 401)
        self.assertEqual(
            anon.post(URL, {"problem_id": PROBLEM, "done": True}, format="json").status_code,
            401,
        )

    def test_starts_empty(self):
        res = self.client.get(URL)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, {"count": 0, "done": []})

    def test_mark_and_unmark(self):
        res = self.client.post(URL, {"problem_id": PROBLEM, "done": True}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, {"count": 1, "done": [PROBLEM]})
        self.assertEqual(self.client.get(URL).data["done"], [PROBLEM])

        res = self.client.post(URL, {"problem_id": PROBLEM, "done": False}, format="json")
        self.assertEqual(res.data, {"count": 0, "done": []})
        self.assertEqual(self.client.get(URL).data["count"], 0)

    def test_marking_twice_is_idempotent(self):
        # The client retries on a flaky connection; a second tick must not 500 on the
        # unique constraint or double the count.
        for _ in range(2):
            res = self.client.post(URL, {"problem_id": PROBLEM, "done": True}, format="json")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.data["count"], 1)
        self.assertEqual(ArchiveCompletion.objects.filter(user=self.user).count(), 1)

    def test_unmarking_something_never_marked_is_a_no_op(self):
        res = self.client.post(URL, {"problem_id": PROBLEM, "done": False}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["count"], 0)

    def test_progress_is_per_user(self):
        other = User.objects.create_user(
            email="alt@example.com", username="alt", password="pw12345!"
        )
        ArchiveCompletion.objects.create(user=other, problem_id=PROBLEM)

        # Someone else's tick is invisible here, and unticking it does nothing.
        self.assertEqual(self.client.get(URL).data["count"], 0)
        self.client.post(URL, {"problem_id": PROBLEM, "done": False}, format="json")
        self.assertTrue(
            ArchiveCompletion.objects.filter(user=other, problem_id=PROBLEM).exists()
        )

    def test_rejects_a_problem_id_that_could_not_be_real(self):
        res = self.client.post(URL, {"problem_id": "x" * 200, "done": True}, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(ArchiveCompletion.objects.count(), 0)

    def test_done_is_required(self):
        # An omitted flag must not be read as "untick" — it's a client bug, not intent.
        res = self.client.post(URL, {"problem_id": PROBLEM}, format="json")
        self.assertEqual(res.status_code, 400)
