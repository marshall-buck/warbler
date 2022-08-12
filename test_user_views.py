"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, Message, User, Like, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app


app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserBaseViewTestCase(TestCase):
    def setUp(self):
        Like.query.delete()
        Message.query.delete()
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)
        db.session.flush()

        m1 = Message(text="m1-text", user_id=u1.id)


        db.session.add_all([m1])
        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id
        self.m1_id = m1.id

        self.client = app.test_client()

class UserViewTestCase(UserBaseViewTestCase):
    def test_view_users(self):
        """test that a logged in user can view other users"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            # Now, that session setting is saved, so we can have
            # the rest of ours test
            resp = c.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("u2", html)
            self.assertIn("u1", html)


    # def list_users(self):

# @app.get('/users/<int:user_id>')
# def show_user(user_id):

class UserViewFollowTestCase(UserBaseViewTestCase):

    def test_show_following(self):
        """test user can see who they're following while logged in"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            u1_fs_u2 = Follows(user_being_followed_id=self.u2_id,
                                    user_following_id=self.u1_id)

            db.session.add_all([u1_fs_u2])
            db.session.commit()

            resp = c.get(f"/users/{self.u1_id}/following")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("u2", html)

    def test_show_followers(self):
        """test user can see who their followers while logged in"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id
            u1_fs_u2 = Follows(user_being_followed_id=self.u2_id,
                                    user_following_id=self.u1_id)

            db.session.add_all([u1_fs_u2])
            db.session.commit()

            resp = c.get(f"/users/{self.u1_id}/followers")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("u1", html)

# When you’re logged out, are you disallowed from visiting a user’s follower / following pages?
    def test_see_followers_logout(self):
        """test that a logged out user cannot see followers"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            c.post("/logout", follow_redirects=True)
            resp = c.get(f"/users/{self.u1_id}/followers", follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_see_following_logout(self):
        """test that a logged out user cannot see followers"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            c.post("/logout", follow_redirects=True)
            resp = c.get(f"/users/{self.u1_id}/following", follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

class UserActionFollowTestCase(UserBaseViewTestCase):
    def test_start_following(self):
        """test if user can follow another user"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(f'/users/follow/{self.u2_id}', follow_redirects = True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("u2", html)

    def test_start_following(self):
        """test if user can follow another user"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(f'/users/follow/{self.u2_id}', follow_redirects = True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("u2", html)

# @app.post('/users/stop-following/<int:follow_id>')
# def stop_following(follow_id):

# @app.route('/users/profile', methods=["GET", "POST"])
# def profile():

# @app.post('/users/delete')
# def delete_user():

# When you’re logged in, can you see the follower / following pages for any user?



