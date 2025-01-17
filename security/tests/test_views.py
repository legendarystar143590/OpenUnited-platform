from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.hashers import make_password

from .factories import UserFactory


class SignUpViewTest(TestCase):
    def setUp(self):
        self.url = reverse("sign-up")
        self.client = Client()

    def test_done(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        form_one = {
            "0-full_name": "John Doe",
            "0-email": "testuser@example.com",
            "0-preferred_name": "John",
            "sign_up_wizard-current_step": "0",
        }

        form_two = {
            "1-verification_code": "123456",
            "sign_up_wizard-current_step": "1",
        }

        form_three = {
            "2-username": "john",
            "2-password": "password",
            "2-password_confirm": "password",
            "sign_up_wizard-current_step": "2",
        }

        SIGN_UP_STEPS_DATA = [form_one, form_two, form_three]

        for data in SIGN_UP_STEPS_DATA:
            response = self.client.post(self.url, data)

            self.assertEqual(response.status_code, 200)
            self.assertIn(
                "security/sign_up/sign_up.html", response.template_name
            )

    def test_process_step_0(self):
        form_one = {
            "0-full_name": "John Doe",
            "0-email": "testuser@example.com",
            "0-preferred_name": "John",
            "sign_up_wizard-current_step": "0",
        }

        response = self.client.post(self.url, form_one)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.client.session.get("verification_code"))

    def test_process_step_1(self):
        form_one = {
            "0-full_name": "John Doe",
            "0-email": "testuser@example.com",
            "0-preferred_name": "John",
            "sign_up_wizard-current_step": "0",
        }

        response = self.client.post(self.url, form_one)
        self.assertEqual(response.status_code, 200)
        self.assertIn("security/sign_up/sign_up.html", response.template_name)

        form_two = {
            "1-verification_code": "123456",
            "sign_up_wizard-current_step": "1",
        }

        response = self.client.post(self.url, form_two)
        self.assertEqual(response.status_code, 200)
        self.assertIn("security/sign_up/sign_up.html", response.template_name)


class SignInViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("sign_in")

    def test_get_method(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_post_reset_required(self):
        user = UserFactory(
            username="testuser",
            password_reset_required=True,
        )

        response = self.client.post(
            self.url,
            {"username_or_email": user.username, "password": user.password},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("password_reset_required"))

    def test_post_reset_view(self):
        plain_password = "testuser"
        user = UserFactory(
            email="testuser@example.com",
            password=make_password(plain_password),
        )

        response = self.client.post(
            self.url,
            {"username_or_email": user.username, "password": "wrong password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The given credentials are not correct!")

        response = self.client.post(
            self.url,
            {"username_or_email": user.username, "password": "wrong password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The given credentials are not correct!")

        response = self.client.post(
            self.url,
            {"username_or_email": user.username, "password": "wrong password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The given credentials are not correct!")

        response = self.client.post(
            self.url,
            {"username_or_email": user.username, "password": "wrong password"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("password_reset_required"))

    def test_post_valid_email(self):
        plain_password = "testuser"
        user = UserFactory(
            email="testuser@example.com",
            password=make_password(plain_password),
        )

        response = self.client.post(
            self.url,
            data={
                "username_or_email": user.email,
                "password": plain_password,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("bounties"))

    def test_post_invalid_email(self):
        response = self.client.post(
            self.url,
            data={
                "username_or_email": "invalid_email@example.com",
                "password": "wrong_password",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "This username or e-mail is not registered"
        )

    def test_post_invalid_username(self):
        response = self.client.post(
            self.url,
            {"username_or_email": "non_existent_user", "password": "12345"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "This username or e-mail is not registered"
        )

    def test_post_valid_credentials(self):
        plain_password = "12345"
        hashed_password = make_password(plain_password)
        user = UserFactory(
            username="test_user",
            password=hashed_password,
        )

        response = self.client.post(
            self.url,
            data={
                "username_or_email": user.username,
                "password": plain_password,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("bounties"))

    def test_post_invalid_credentials(self):
        plain_password = "12345"
        invalid_password = "12344"
        user = UserFactory(
            username="test_user",
            password=plain_password,
        )

        response = self.client.post(
            self.url,
            data={
                "username_or_email": user.username,
                "password": invalid_password,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The given credentials are not correct!")


class PasswordResetViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("password_reset")

    def test_get(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_post_invalid_form(self):
        response = self.client.post(
            self.url, {"email": "not_exist@example.com"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This e-mail does not exist")

    def test_post_valid_form(self):
        user = UserFactory(email="exist@example.com")
        response = self.client.post(
            self.url, {"email": user.email}, follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("password_reset_done"))


class LogoutViewTest(TestCase):
    def setUp(self):
        self.url = reverse("log_out")
        self.client = Client()

    def test_logout_view_authenticated_user(self):
        plain_password = "12345"
        hashed_password = make_password(plain_password)
        user = UserFactory(username="username", password=hashed_password)

        self.client.login(username=user.username, password=plain_password)

        response = self.client.post(self.url)

        self.assertRedirects(response, reverse("home"))
        self.assertFalse("_auth_user_id" in self.client.session)

    def test_logout_view_unauthenticated_user(self):
        response = self.client.post(self.url, follow=True)

        expected_url = reverse("sign_in") + "?next=" + reverse("log_out")

        self.assertRedirects(response, expected_url)
        self.assertFalse("_auth_user_id" in self.client.session)
