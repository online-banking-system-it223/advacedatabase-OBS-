from django.test import TestCase
import unittest
from .userManagement import RegisterUser
# Create your tests here.

class Tests(unittest.TestCase):
	"""docstring for test"""
	self.email = RegisterUser.clean_email()
	def test_1(self):
		self.assertTrue(self.email('jonhcs2d2000@gmail.com'))

	def test_1(self):
		self.assertFalse(self.email('myf_city@yahoo.com'))


if __name__ == "__main__":
    unittest.main()
		