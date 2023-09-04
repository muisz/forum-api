from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError, NotFound

from .models import Forum, ForumParticipant

User = get_user_model()


class ForumModelTest(TestCase):
    def setUp(self):
        self.user = User.register("Muhamad Abdul Muis", "abdulmuis", "password")
        self.setUpParticipants()
    
    def setUpParticipants(self):
        participants = []
        for number in range(3):
            user = User.register(f"user {number}", f"user{number}", "password")
            participants.append(user)
        self.participants = participants
    
    def test_set_topic_method(self):
        forum = Forum()
        forum.set_topic("Testing Topic")

        self.assertEqual(forum.topic_lowercase, "testing topic")

    def test_create_forum_method_with_zero_participants(self):
        try:
            forum = Forum.create_forum(
                topic="testing",
                description="description",
                initiator=self.user,
                participants=[]
            )
            
            self.assertTrue(False)
        except Exception as error:
            self.assertIsInstance(error, ValidationError)
            self.assertIn("cannot create forum with 0 participants", str(error))
    
    def test_create_forum_method_with_invalid_participant(self):
        try:
            forum = Forum.create_forum(
                topic="testing",
                description="description",
                initiator=self.user,
                participants=[100]
            )
        except Exception as error:
            self.assertIsInstance(error, NotFound)
            self.assertIn(f"user with id of 100 not found", str(error))

    def test_create_forum_method(self):
        forum = Forum.create_forum(
            topic="testing",
            description="description",
            initiator=self.user,
            participants=[participant.id for participant in self.participants]
        )

        self.assertIsInstance(forum.id, int)
    
    def test_get_participants_method(self):
        forum = Forum.create_forum(
            topic="testing",
            description="description",
            initiator=self.user,
            participants=[participant.id for participant in self.participants]
        )
        participants_in_forum = forum.get_participants()
        self.participants.append(self.user) # initiator

        self.assertEqual(len(participants_in_forum), len(self.participants))

    def test_get_participants_users_method(self):
        forum = Forum.create_forum(
            topic="testing",
            description="description",
            initiator=self.user,
            participants=[participant.id for participant in self.participants]
        )
        participants_in_forum = forum.get_participant_users()
        self.participants.append(self.user) # initiator

        for participant in participants_in_forum:
            self.assertIn(participant, self.participants)

    def test_add_participant_method(self):
        forum = Forum.create_forum(
            topic="testing",
            description="description",
            initiator=self.user,
            participants=[self.participants[0].id]
        )
        forum.add_participant(self.participants[1])
        participants_in_forum = forum.get_participants()

        self.assertEqual(len(participants_in_forum), 3) # with initiator


class ForumParticipantModelTest(TestCase):
    def setUp(self):
        self.setUpForum()

    def setUpForum(self):
        self.user = User.register("Muhamad Abdul Muis", "abdulmuis", "password")
        self.setUpParticipants()

        self.forum = Forum(description="tes")
        self.forum.set_topic("testing")
        self.forum.save()

    
    def setUpParticipants(self):
        participants = []
        for number in range(3):
            user = User.register(f"user {number}", f"user{number}", "password")
            participants.append(user)
        self.participants = participants

    def test_create_participant_method_with_initiator_true(self):
        participant = ForumParticipant.create_participant(self.forum, self.user, True)

        self.assertTrue(participant.initiator)
        self.assertEqual(participant.status, ForumParticipant.ACCEPT)
    
    def test_create_participant_method_with_initiator_false(self):
        participant = ForumParticipant.create_participant(self.forum, self.user, False)

        self.assertFalse(participant.initiator)
        self.assertEqual(participant.status, ForumParticipant.WAITING)
