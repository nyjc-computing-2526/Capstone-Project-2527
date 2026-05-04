"""
BEFORE RUNNING THIS FILE, RUN THIS IN THE TERMINAL --
run the following command in the terminal to execute the tests in this file:
export PYTHONPATH=/workspaces/Capstone-Project-2527:$PYTHONPATH && /workspaces/Capstone-Project-2527/.venv/bin/python -m unittest testing.utils_profanity_checker -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.profanity_checker import check_profanity

class TestProfanityChecker(unittest.TestCase):
    """Test suite for the profanity_checker utility function."""

    def test_check_profanity_clean_text(self):
        """Test check_profanity with clean text."""
        result = check_profanity("Hello world")
        self.assertTrue(result["valid"])
        self.assertEqual(result["message"], "Input is clean")
        self.assertEqual(result["msg"], "Input is clean")
        self.assertEqual(result["score"], 0.0)

    def test_check_profanity_profane_text(self):
        """Test check_profanity with profane text."""
        result = check_profanity("This is a damn test")
        self.assertFalse(result["valid"])
        self.assertEqual(result["message"], "Inappropriate language detected")
        self.assertEqual(result["msg"], "Inappropriate language detected")
        self.assertEqual(result["score"], 1.0)

    def test_check_profanity_non_string_input(self):
        """Test check_profanity with non-string input."""
        result = check_profanity(123)
        self.assertFalse(result["valid"])
        self.assertEqual(result["message"], "Input must be a string")
        self.assertEqual(result["msg"], "Input must be a string")
        self.assertEqual(result["score"], 1.0)

    def test_check_profanity_empty_string(self):
        """Test check_profanity with empty string."""
        result = check_profanity("")
        self.assertTrue(result["valid"])
        self.assertEqual(result["message"], "Input is clean")
        self.assertEqual(result["msg"], "Input is clean")
        self.assertEqual(result["score"], 0.0)

    def test_check_profanity_mixed_case_profanity(self):
        """Test check_profanity with mixed case profane words."""
        result = check_profanity("This is a DaMn test")
        self.assertFalse(result["valid"])
        self.assertEqual(result["message"], "Inappropriate language detected")
        self.assertEqual(result["msg"], "Inappropriate language detected")
        self.assertEqual(result["score"], 1.0)

    def test_check_profanity_multiple_profanities(self):
        """Test check_profanity with multiple profane words."""
        result = check_profanity("This damn shit is a test")
        self.assertFalse(result["valid"])
        self.assertEqual(result["message"], "Inappropriate language detected")
        self.assertEqual(result["msg"], "Inappropriate language detected")
        self.assertEqual(result["score"], 1.0)

    def test_check_profanity_return_type(self):
        """Test that check_profanity returns a dictionary with expected keys."""
        result = check_profanity("Hello world")
        self.assertIsInstance(result, dict)
        self.assertIn("valid", result)
        self.assertEqual(True, result["valid"])
        self.assertEqual(result["message"], "Inappropriate language detected")
        self.assertIn("message", result)
        self.assertIn("msg", result)
        self.assertIn("score", result)

    def test_check_profanity_return_type(self):
        """test that check_profanity returns a dictionary with expected keys"""
        result = check_profanity("肏你妈")
        self.assertIsInstance(result, dict)
        self.assertIn("valid", result)
        self.assertEqual(False, result["valid"])
        self.assertEqual(result["message"], "Inappropriate language detected")
        self.assertIn("message", result)
        self.assertIn("msg", result)
        self.assertIn("score", result)

    def test_check_profanity_return_type(self):
        """test that check_profanity returns a dictionary with expected keys"""
        result = check_profanity("chink")
        self.assertIsInstance(result, dict)
        self.assertIn("valid", result)
        self.assertEqual(False, result["valid"])
        self.assertEqual(result["message"], "Inappropriate language detected")
        self.assertIn("message", result)
        self.assertIn("msg", result)
        self.assertIn("score", result)
    
    def test_check_profanity_return_type(self):
        """test that check_profanity returns a dictionary with expected keys"""
        result = check_profanity("chigga")
        self.assertIsInstance(result, dict)
        self.assertIn("valid", result)
        self.assertEqual(False, result["valid"])
        self.assertEqual(result["message"], "Inappropriate language detected")
        self.assertIn("message", result)
        self.assertIn("msg", result)
        self.assertIn("score", result)

    def test_check_profanity_return_type(self):
        """test that check_profanity returns a dictionary with expected keys"""
        result = check_profanity("cotton picker")
        self.assertIsInstance(result, dict)
        self.assertIn("valid", result)
        self.assertEqual(False, result["valid"])
        self.assertEqual(result["message"], "Inappropriate language detected")
        self.assertIn("message", result)
        self.assertIn("msg", result)
        self.assertIn("score", result)

    def test_check_profanity_return_type(self):
        """test that check_profanity returns a dictionary with expected keys"""
        result = check_profanity("stupid")
        self.assertIsInstance(result, dict)
        self.assertIn("valid", result)
        self.assertEqual(False, result["valid"])
        self.assertEqual(result["message"], "Inappropriate language detected")
        self.assertIn("message", result)
        self.assertIn("msg", result)
        self.assertIn("score", result)

    def test_check_profanity_return_type(self):
        """test that check_profanity returns a dictionary with expected keys"""
        result = check_profanity("你妈的")
        self.assertIsInstance(result, dict)
        self.assertIn("valid", result)
        self.assertEqual(False, result["valid"])
        self.assertEqual(result["message"], "Inappropriate language detected")
        self.assertIn("message", result)
        self.assertIn("msg", result)
        self.assertIn("score", result)

    def test_check_profanity_return_type(self):
        """test that check_profanity returns a dictionary with expected keys"""
        result = check_profanity("cunt")
        self.assertIsInstance(result, dict)
        self.assertIn("valid", result)
        self.assertEqual(False, result["valid"])
        self.assertEqual(result["message"], "Inappropriate language detected")
        self.assertIn("message", result)
        self.assertIn("msg", result)
        self.assertIn("score", result)

    def test_check_profanity_return_type(self):
        """test that check_profanity returns a dictionary with expected keys"""
        result = check_profanity("kys")
        self.assertIsInstance(result, dict)
        self.assertIn("valid", result)
        self.assertEqual(False, result["valid"])
        self.assertEqual(result["message"], "Inappropriate language detected")
        self.assertIn("message", result)
        self.assertIn("msg", result)
        self.assertIn("score", result)

    def test_check_profanity_return_type(self):
        """test that check_profanity returns a dictionary with expected keys"""
        result = check_profanity("Neggar")
        self.assertIsInstance(result, dict)
        self.assertIn("valid", result)
        self.assertEqual(False, result["valid"])
        self.assertEqual(result["message"], "Inappropriate language detected")
        self.assertIn("message", result)
        self.assertIn("msg", result)
        self.assertIn("score", result)

    def test_check_profanity_return_type(self):
        """test that check_profanity returns a dictionary with expected keys"""
        result = check_profanity("i hope you kill youself")
        self.assertIsInstance(result, dict)
        self.assertIn("valid", result)
        self.assertEqual(False, result["valid"])
        self.assertEqual(result["message"], "Inappropriate language detected")
        self.assertIn("message", result)
        self.assertIn("msg", result)
        self.assertIn("score", result)

    def test_check_profanity_return_type(self):
        """test that check_profanity returns a dictionary with expected keys"""
        result = check_profanity("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus. Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, dolor. Cras elementum ultrices diam. Maecenas ligula massa, varius a, semper congue, euismod non, mi.Proin porttitor, orci nec nonummy molestie, enim est eleifend mi, non fermentum diam nisl sit amet erat. Duis semper. Duis arcu massa, scelerisque vitae, consequat in, pretium a, enim. Pellentesque congue.Ut in risus volutpat libero pharetra tempor. Cras vestibulum bibendum augue. Praesent egestas leo in pede. Praesent blandit odio eu enim. Pellentesque sed dui ut augue blandit sodales Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Aliquam nibh. Mauris ac mauris sed pede pellentesque fermentum. Maecenas adipiscing ante non diam sodales hendrerit. Fuck")
        self.assertIsInstance(result, dict)
        self.assertIn("valid", result)
        self.assertEqual(False, result["valid"])
        self.assertEqual(result["message"], "Inappropriate language detected")
        self.assertIn("message", result)
        self.assertIn("msg", result)
        self.assertIn("score", result)

    def test_check_profanity_return_type(self):
        """test that check_profanity returns a dictionary with expected keys"""
        result = check_profanity("penis")
        self.assertIsInstance(result, dict)
        self.assertIn("valid", result)
        self.assertEqual(True, result["valid"])
        self.assertEqual(result["message"], "Inappropriate language detected")
        self.assertIn("message", result)
        self.assertIn("msg", result)
        self.assertIn("score", result)

if __name__ == '__main__':
    unittest.main()