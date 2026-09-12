from django.test import TestCase
from rest_framework.test import APIClient
from vision.feature_extractor import extract_features


class FeatureExtractorTests(TestCase):
    def test_detects_a_raw_ip_and_at_symbol(self):
        features = extract_features("http://192.168.1.10/login@evil.example/verify")
        self.assertEqual(features["has_ip_address"], 1)
        self.assertEqual(features["has_at_symbol"], 1)


class CheckURLApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_suspicious_url_is_saved_and_explained(self):
        response = self.client.post("/api/check-url/", {"url": "http://192.168.1.10/secure-login/verify-account"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["data"]["verdict"], "phishing")
        self.assertTrue(response.data["data"]["explanations"])

    def test_url_without_scheme_is_accepted(self):
        response = self.client.post("/api/check-url/", {"url": "www.example.com"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["data"]["url"], "https://www.example.com")
