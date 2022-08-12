"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from sqlite3 import IntegrityError
from unittest import TestCase

from models import db, User, Message, Follows, Like

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


class MessageModelTestCase(TestCase):
    """Test for model of Message"""

    def setUp(self):
        """Make demo data"""
        Like.query.delete()
        Message.query.delete()
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        m1 = Message(text="Message 1 text", user_id=self.u1_id)
        m2 = Message(text="Message 2 text", user_id=self.u1_id)

        db.session.add_all([m1, m2])
        db.session.commit()

        self.m1_id = m1.id
        self.m2_id = m2.id

        self.client = app.test_client()

    def tearDown(self):
        """Clean up fouled transactions"""
        db.session.rollback()

    def test_message_belongs_to_correct_user(self):
        """ messages should belong to user1"""

        m1 = Message.query.get(self.m1_id)
        m2 = Message.query.get(self.m2_id)
        u1 = User.query.get(self.u1_id)

        self.assertEqual(m1.user_id, self.u1_id)
        self.assertEqual(m2.user_id, self.u1_id)

        self.assertEqual(len(u1.messages), 2)
# FIXME: separate liking and unliking

    def test_liking_message(self):
        """test is_liked_by_user method when user likes and un-likes a message"""

        m1 = Message.query.get(self.m1_id)
        u2 = User.query.get(self.u2_id)
        u1 = User.query.get(self.u1_id)

        u2.liked_messages.append(m1)
        db.session.commit()

        self.assertTrue(m1.is_liked_by_user(u2))
        self.assertFalse(m1.is_liked_by_user(u1))

        # Unlike a message
        u2.liked_messages.remove(m1)
        db.session.commit()
        self.assertFalse(m1.is_liked_by_user(u2))

# TODO How to check database errors


# TODO:check timestamp? how?
