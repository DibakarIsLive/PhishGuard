from django.test import TestCase
from rest_framework.test import APIClient
from vision.feature_extractor import extract_features
from django.core.files.uploadedfile import SimpleUploadedFile


class FeatureExtractorTests(TestCase):
    def test_detects_a_raw_ip_and_at_symbol(self):
        features = extract_features("http://192.168.1.10/login@evil.example/verify")
        self.assertEqual(features["has_ip_address"], 1)
        self.assertEqual(features["has_at_symbol"], 1)

    def test_malformed_ipv6_style_url_does_not_stop_processing(self):
        features = extract_features("http://[invalid-ipv6/login")
        self.assertIn("url_length", features)


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

    def test_csv_upload_starts_an_all_rows_background_job(self):
        dataset = SimpleUploadedFile("demo.csv", b"URL,Label\nhttp://google.com@192.168.1.10/secure-login/verify-account,bad\nhttps://www.google.com,good\n", content_type="text/csv")
        response = self.client.post("/api/upload-csv/", {"file": dataset}, format="multipart")
        self.assertEqual(response.status_code, 202)
        self.assertIn("job_id", response.data["data"])
        self.assertEqual(response.data["data"]["status"], "queued")
