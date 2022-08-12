"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from sqlite3 import IntegrityError
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()

db.create_all()


class UserModelTestCase(TestCase):
    """Test for model of User"""

    def setUp(self):
        """Make demo data"""
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        """Clean up fouled transactions"""
        db.session.rollback()

    def test_user_model(self):
        """ User should have no messages & no followers"""
        u1 = User.query.get(self.u1_id)

        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)

    def test_repr_method(self):
        """Does the repr method work as expected?"""
        u1 = User.query.get(self.u1_id)
        self.assertIn("u1@email.com", u1.__repr__())

    def test_following(self):
        """ Does is_following successfully detect when user1 is following user2?"""
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)
        u2.followers.append(u1)
        db.session.commit()

        self.assertTrue(u1.is_following(u2))
        self.assertEqual(len(u2.followers), 1)

    def test_not_following(self):
        """Does is_following successfully detect when user1 is not following user2?"""
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)
        u2.followers.append(u1)
        db.session.commit()
        u2.followers.remove(u1)
        db.session.commit()

        self.assertFalse(u1.is_following(u2))
        self.assertEqual(len(u2.followers), 0)

    def test_is_followed_by(self):
        """ Does is_followed_by successfully detect when user1 is followed by user2?"""
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)
        u1.followers.append(u2)
        db.session.commit()

        self.assertTrue(u1.is_followed_by(u2))
        self.assertEqual(len(u1.followers), 1)

    def test_is_not_followed_by(self):
        """Does is_followed_by successfully detect when user1 is not followed by user2?"""
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)
        u1.followers.append(u2)
        db.session.commit()
        u1.followers.remove(u2)
        db.session.commit()

        self.assertFalse(u1.is_followed_by(u2))
        self.assertEqual(len(u1.followers), 0)

    def test_sign_up(self):
        """ Does User.signup successfully create a new user given valid credentials?"""
        # TODO: maybe a different approach?
        u1 = User.query.get(self.u1_id)
        self.assertIsNotNone(u1)

    # def test_fail_sign_up(self):
        """ Does User.signup fail to create a new user if any of the validations (eg uniqueness, non-nullable fields) fail?"""
        # TODO: come back to this!
        # with self.assertRaises(IntegrityError) as context:
        #     u3 = User.signup("u1", "u1@email.com", "password", None)
        #     db.session.commit()
        # self.assertNotIsInstance(u3, User)

    def test_successful_auth(self):
        """# Tests user authentication"""
        u1 = User.query.get(self.u1_id)
        self.assertIsInstance(u1.authenticate('u1', 'password'), User)
        self.assertFalse(u1.authenticate('u1', 'passsadfasdfword'))
        self.assertFalse(u1.authenticate('u111', 'password'))
