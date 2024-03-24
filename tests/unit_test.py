import json
import os
import unittest

from imdb_app.api.urls import app
from imdb_app.common.definitions import Collection
from imdb_app.core.config import CONF
from imdb_app.db.mongo_adapters import MongoAdapter


class IMDBAppTestCases(unittest.TestCase):

    def setUp(self):
        CONF(default_config_files=["/tmp/config/imdb_app.conf"])
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        # Assuming the MongoAdapter is properly configured in test_config.conf
        self.adapter = MongoAdapter(Collection.USERS)
        self.user_data = {"email": "test@example.com", "password": "test123"}
        self.user_data_no_password = {"email": "test2@gmail.com"}

    def tearDown(self):
        # Clean up the test users
        self.adapter.remove_document({"email": self.user_data["email"]})
        self.user_data_no_password = {"email": "test2@gmail.com"}

    def test_user_registration(self):
        response = self.client.post("/register",
                                    data=json.dumps(self.user_data),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_invalid_registration(self):
        response = self.client.post("/register",
                                    data=json.dumps(self.user_data_no_password),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_empty_credentials(self):
        empty_data = {"email": "", "password": ""}
        response = self.client.post("/authenticate",
                                    data=json.dumps(empty_data),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_invalid_login(self):
        wrong_password_data = {"email": self.user_data["email"], "password": "wrong"}
        response = self.client.post("/authenticate",
                                    data=json.dumps(wrong_password_data),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_login_response_format(self):
        self.client.post("/register",
                         data=json.dumps(self.user_data),
                         content_type="application/json")

        response = self.client.post("/authenticate",
                                    data=json.dumps(self.user_data),
                                    content_type="application/json")
        data = json.loads(response.data)
        self.assertIn("token", data)
        self.assertIsInstance(data["token"]["key"], str)

    def test_csv_upload_with_invalid_authentication(self):
        current_directory = os.getcwd()
        with open(os.path.join(current_directory, "test.txt"), 'rb') as file:
            response = self.client.post("/upload",
                                        content_type="multipart/form-data",
                                        data={
                                            "file": file
                                        }
                                        # No auth header
                                        )
            self.assertEqual(response.status_code, 403)

    def test_csv_upload_without_authentication(self):
        self.client.post("/register",
                         data=json.dumps(self.user_data),
                         content_type="application/json")

        auth_response = self.client.post("/authenticate",
                                         data=json.dumps(self.user_data),
                                         content_type="application/json")
        data = json.loads(auth_response.data)

        current_directory = os.getcwd()
        with open(os.path.join(current_directory, "test.txt"), 'rb') as file:
            response = self.client.post("/upload",
                                        content_type="multipart/form-data",
                                        data={
                                            "file": file
                                        },
                                        headers={
                                            "Auth-Token": data["token"]["key"][:-2]
                                        })
            self.assertEqual(response.status_code, 401)

    def test_invalid_file_format(self):
        self.client.post("/register",
                         data=json.dumps(self.user_data),
                         content_type="application/json")

        auth_response = self.client.post("/authenticate",
                                         data=json.dumps(self.user_data),
                                         content_type="application/json")
        data = json.loads(auth_response.data)

        current_directory = os.getcwd()
        with open(os.path.join(current_directory, "test.txt"), 'rb') as file:
            response = self.client.post("/upload",
                                        content_type="multipart/form-data",
                                        data={
                                            "file": file
                                        },
                                        headers={
                                            "Auth-Token": data["token"]["key"]
                                        })
            self.assertEqual(response.status_code, 400)

    def test_valid_movies_list_request(self):
        self.client.post("/register",
                         data=json.dumps(self.user_data),
                         content_type="application/json")

        auth_response = self.client.post("/authenticate",
                                         data=json.dumps(self.user_data),
                                         content_type="application/json")
        auth_data = json.loads(auth_response.data)

        response = self.client.get("/movies?page=1&page_size=5",
                                   headers={
                                       "Auth-Token": auth_data["token"]["key"]
                                   })
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue("movies" in data)
        self.assertTrue(len(data['movies']) <= 5)

    def test_invalid_pagination_parameters(self):
        self.client.post("/register",
                         data=json.dumps(self.user_data),
                         content_type="application/json")

        auth_response = self.client.post("/authenticate",
                                         data=json.dumps(self.user_data),
                                         content_type="application/json")
        auth_data = json.loads(auth_response.data)

        response = self.client.get("/movies?page=-1&page_size=5",
                                   headers={
                                       "Auth-Token": auth_data["token"]["key"]
                                   })
        self.assertEqual(response.status_code, 400)  # Assuming 400 Bad Request for invalid params

    def test_movies_list_without_authentication(self):
        response = self.client.get('/movies?page=1&limit=5')
        # Assuming 403 Forbidden - Token missing
        self.assertEqual(response.status_code, 403)

    def test_movies_list_response_structure(self):
        self.client.post("/register",
                         data=json.dumps(self.user_data),
                         content_type="application/json")

        auth_response = self.client.post("/authenticate",
                                         data=json.dumps(self.user_data),
                                         content_type="application/json")
        auth_data = json.loads(auth_response.data)
        
        response = self.client.get("/movies?page=1&page_size=5",
                                   headers={
                                       "Auth-Token": auth_data["token"]["key"]
                                   })
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        # Check if all expected fields are present in each movie
        for movie in data["movies"]:
            self.assertIn("movie_id", movie)
            self.assertIn("show_id", movie)
            self.assertIn("type", movie)
            self.assertIn("title", movie)
            self.assertIn("director", movie)
            self.assertIn("cast", movie)
            self.assertIn("country", movie)
            self.assertIn("date_added", movie)
            self.assertIn("release_year", movie)
            self.assertIn("rating", movie)
            self.assertIn("duration", movie)
            self.assertIn("listed_in", movie)
            self.assertIn("description", movie)
            self.assertIn("file_process_id", movie)
            self.assertIn("created_at", movie)
            self.assertIn("updated_at", movie)


if __name__ == '__main__':
    unittest.main()
