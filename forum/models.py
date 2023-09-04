from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.exceptions import ValidationError, NotFound

from util.models import BaseModel

User = get_user_model()


class Forum(BaseModel):
    topic = models.CharField(max_length=100)
    topic_lowercase = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=True)
    
    OPEN = 1
    CLOSED = 2
    STATUS_CHOICES = (
        (OPEN, 'Open'),
        (CLOSED, 'Closed'),
    )
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=OPEN)
    closed_at = models.DateTimeField(null=True)

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
        self.check_forum_is_closed()
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

    def close_by(self, user):
        self.check_forum_is_closed()
        initiator = ForumParticipant.get_initiator(self)
        if user != initiator:
            raise ValidationError("only initiator user can close this forum")
        self.closed_at = timezone.now()
        self.status = self.CLOSED
        self.save()
    
    def check_forum_is_closed(self):
        if self.status == self.CLOSED:
            raise ValidationError("forum already closed")


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

    @classmethod
    def get_initiator(cls, forum):
        initiator = cls.objects.filter(forum=forum, initiator=True).first()
        if initiator is None:
            raise NotFound("initiator not found")
        return initiator.user
