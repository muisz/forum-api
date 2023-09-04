from django.db import models
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from util.models import BaseModel

User = get_user_model()


class Forum(BaseModel):
    topic = models.CharField(max_length=100)
    topic_lowercase = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=True)

    @classmethod
    def create_forum(cls, topic: str, description: str, initiator: User, participants: list):
        if len(participants) == 0:
            raise ValidationError("cannot create forum with 0 participants")

        forum = cls(description=description)
        forum.set_topic(topic)
        forum.save()
        
        ForumParticipant.create_participant(forum, initiator, True)

        for participant_id in participants:
            user = User.get_active_user(participant_id)
            forum.add_participant(user)
        
        return forum
    
    def set_topic(self, name: str):
        self.topic = name
        self.topic_lowercase = name.lower()
    
    def add_participant(self, user):
        participant = ForumParticipant.create_participant(
            forum=self,
            user=user,
            initiator=False,
        )
        return participant

    def get_participant_users(self):
        participants = self.get_participants().select_related('user')
        return [participant.user for participant in participants]
    
    def get_participants(self):
        return ForumParticipant.objects.filter(forum=self).order_by('-created_at')


class ForumParticipant(BaseModel):
    forum = models.ForeignKey(Forum, on_delete=models.PROTECT, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='participants')
    initiator = models.BooleanField(default=False)

    ACCEPT = 1
    DENY = 2
    WAITING = 3
    STATUS_CHOICES = (
        (ACCEPT, 'Accept'),
        (DENY, 'Deny'),
        (WAITING, 'Waiting'),
    )
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=WAITING)

    @classmethod
    def create_participant(cls, forum: Forum, user: User, initiator: bool):
        participant = cls(forum=forum, user=user, initiator=initiator)
        if initiator is True:
            participant.status = cls.ACCEPT
        participant.save()
        return participant
