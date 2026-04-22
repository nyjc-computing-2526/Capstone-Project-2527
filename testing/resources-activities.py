"""
BEFORE RUNNING THIS FILE, RUN THIS IN THE TERMINAL --
run the following command in the terminal to execute the tests in this file:
export PYTHONPATH=/workspaces/Capstone-Project-2527:$PYTHONPATH && /workspaces/Capstone-Project-2527/.venv/bin/python -m unittest app.tests.resources_activities -v
"""

from app.resources import activities

import unittest 

class TestActivitiesResource(unittest.TestCase):
    """Test suite for the ActivitiesResource class in app.resources.activities."""
    def setUp(self):
        """Set up the test case by initializing the ActivitiesResource instance."""
        self.activities_resource = activities.ActivitiesResource()
        
    def test_get_all(self):
        """Test the get_all method to ensure it returns a list of dictionaries."""
        result = self.activities_resource.get_all()
        self.assertIsInstance(result, list)
        for activity in result:
            self.assertIsInstance(activity, dict)

    def test_get_completed(self):
        """Test the get_completed method to ensure it returns a list of dictionaries."""
        result = self.activities_resource.get_completed()
        self.assertIsInstance(result, list)
        for activity in result:
            self.assertIsInstance(activity, dict)

    def test_get_upcoming(self):
        """Test the get_upcoming method to ensure it returns a list of dictionaries."""
        result = self.activities_resource.get_upcoming()
        self.assertIsInstance(result, list)
        for activity in result:
            self.assertIsInstance(activity, dict)

    def test_get_owned_valid_user_id(self):
        """Test the get_owned method with a valid user ID to ensure it returns a list of dictionaries."""
        result = self.activities_resource.get_owned(1)
        self.assertIsInstance(result, list)
        for activity in result:
            self.assertIsInstance(activity, dict)

    def test_get_owned_invalid_user_id(self):
        """Test the get_owned method with an invalid user ID to ensure it raises a ValueError."""
        with self.assertRaises(ValueError):
            self.activities_resource.get_owned(-1)

    def test_get_joined_valid_user_id(self):
        """Test the get_joined method with a valid user ID to ensure it returns a list of dictionaries."""
        result = self.activities_resource.get_joined(1)
        self.assertIsInstance(result, list)
        for activity in result:
            self.assertIsInstance(activity, dict)

    def test_get_joined_invalid_user_id(self):
        """Test the get_joined method with an invalid user ID to ensure it raises a ValueError."""
        with self.assertRaises(ValueError):
            self.activities_resource.get_joined(-1)