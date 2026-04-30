"""
BEFORE RUNNING THIS FILE, RUN THIS IN THE TERMINAL --
run the following command in the terminal to execute the tests in this file:
export PYTHONPATH=/workspaces/Capstone-Project-2527:$PYTHONPATH && /workspaces/Capstone-Project-2527/.venv/bin/python -m unittest app.tests.resources_activities -v
"""

import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.resources import activities

class TestActivitiesResource(unittest.TestCase):
    """Test suite for the ActivitiesResource class in app.resources.activities."""
    def setUp(self):
        self.activities_resource = activities.ActivitiesResource()

    def test_get_all(self):
        with patch('app.resources.activities.db.get_activities', return_value=[{'id': 1, 'title': 'Test Activity'}]):
            result = self.activities_resource.get_all()
            self.assertIsInstance(result, list)
            for activity in result:
                self.assertIsInstance(activity, dict)

    def test_get_completed(self):
        with patch('app.resources.activities.db.get_completed_activities', return_value=[{'id': 2, 'title': 'Completed Activity'}]):
            result = self.activities_resource.get_completed()
            self.assertIsInstance(result, list)
            for activity in result:
                self.assertIsInstance(activity, dict)

    def test_get_upcoming(self):
        with patch('app.resources.activities.db.get_upcoming_activities', return_value=[{'id': 3, 'title': 'Upcoming Activity'}]):
            result = self.activities_resource.get_upcoming()
            self.assertIsInstance(result, list)
            for activity in result:
                self.assertIsInstance(activity, dict)

    def test_get_owned_valid_user_id(self):
        with patch('app.resources.activities.db.get_owned', return_value=[{'id': 4, 'title': 'Owned Activity'}]):
            result = self.activities_resource.get_owned(1)
            self.assertIsInstance(result, list)
            for activity in result:
                self.assertIsInstance(activity, dict)

    def test_get_owned_invalid_user_id(self):
        with self.assertRaises(ValueError):
            self.activities_resource.get_owned(-1)

    def test_get_joined_valid_user_id(self):
        with patch('app.resources.activities.db.get_joined', return_value=[{'id': 5, 'title': 'Joined Activity'}]):
            result = self.activities_resource.get_joined(1)
            self.assertIsInstance(result, list)
            for activity in result:
                self.assertIsInstance(activity, dict)

    def test_get_joined_invalid_user_id(self):
        with self.assertRaises(ValueError):
            self.activities_resource.get_joined(-1)

    def test_create_activity_valid_activity_data(self):
        with patch('app.resources.activities.db.create_activity', return_value=1):
            result = self.activities_resource.create_activity({
                'started_at': '2023-01-01',
                'ended_at': '2023-01-02',
                'title': 'Test Activity',
                'description': 'A test activity.',
                'created_by': 1,
                'venue': 'Test Venue'
            })
            self.assertIsInstance(result, int)
            self.assertEqual(result, 1)

    def test_create_activity_invalid_activity_data(self):
        with self.assertRaises(ValueError):
            self.activities_resource.create_activity({'invalid': 'data'})

    def test_create_activity_missing_fields(self):
        with self.assertRaises(ValueError):
            self.activities_resource.create_activity({
                'started_at': '2023-01-01',
                'ended_at': '2023-01-02',
                'title': 'Test Activity',
                'description': 'A test activity.',
                'created_by': 1
            })

    def test_activity_valid_activity_id(self):
        result = self.activities_resource.activity(16)
        self.assertIsInstance(result, activities.ActivityResource)

    def test_activity_invalid_activity_id(self):
        with self.assertRaises(ValueError):
            self.activities_resource.activity(-1)

class TestActivityResource(unittest.TestCase):
    """Test suite for the ActivityResource class in app.resources.activities."""
    def setUp(self):
        self.activity_resource = activities.ActivityResource(16)
        self.nonexistent_activity_resource = activities.ActivityResource(999)

    def test_get_valid_activity_id(self):
        with patch('app.resources.activities.db.get_activity_by_id', return_value={
            'id': 16,
            'title': 'Test Activity',
            'description': 'Test',
            'started_at': '2023-01-01T00:00:00Z',
            'ended_at': '2023-01-02T00:00:00Z',
            'created_by': 1,
            'venue': 'Test Venue'
        }):
            result = self.activity_resource.get()
            self.assertIsInstance(result, dict)

    def test_get_invalid_activity_id(self):
        with patch('app.resources.activities.db.get_activity_by_id', return_value=None):
            with self.assertRaises(ValueError):
                self.nonexistent_activity_resource.get()

if __name__ == '__main__':
    unittest.main()
