from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from vote.models import Session, Election, Voter, Application


@receiver(post_save, sender=Session)
def on_session_update(sender, instance, **kwargs):
    election_managers = instance.managers.all()
    for election_manager in election_managers:
        async_to_sync(get_channel_layer().group_send)(
            f'api-election-manager-{election_manager.id}',
            {'type': 'send_update', 'table': 'session', 'instance_id': instance.pk}
        )
    async_to_sync(get_channel_layer().group_send)(
        f'api-vote-session-{instance.pk}',
        {'type': 'send_update', 'table': 'session',  'instance_id': instance.pk}
    )


@receiver(post_delete, sender=Election)
@receiver(post_save, sender=Election)
def on_election_update(sender, instance, **kwargs):
    election_managers = instance.session.managers.all()
    for election_manager in election_managers:
        async_to_sync(get_channel_layer().group_send)(
            f'api-election-manager-{election_manager.id}',
            {'type': 'send_update', 'table': 'election', 'instance_id': instance.pk}
        )
    async_to_sync(get_channel_layer().group_send)(
        f'api-vote-session-{instance.session.pk}',
        {'type': 'send_update', 'table': 'election', 'instance_id': instance.pk}
    )


@receiver(post_delete, sender=Voter)
@receiver(post_save, sender=Voter)
def on_voter_update(sender, instance, **kwargs):
    election_managers = instance.session.managers.all()
    for election_manager in election_managers:
        async_to_sync(get_channel_layer().group_send)(
            f'api-election-manager-{election_manager.id}',
            {'type': 'send_update', 'table': 'voter', 'instance_id': instance.pk}
        )
    async_to_sync(get_channel_layer().group_send)(
        f'api-vote-session-{instance.session.pk}',
        {'type': 'send_update', 'table': 'voter', 'instance_id': instance.pk}
    )


@receiver(post_delete, sender=Application)
@receiver(post_save, sender=Application)
def on_application_update(sender, instance, **kwargs):
    election_managers = instance.election.session.managers.all()
    for election_manager in election_managers:
        async_to_sync(get_channel_layer().group_send)(
            f'api-election-manager-{election_manager.id}',
            {'type': 'send_update', 'table': 'election', 'instance_id': instance.pk}
        )
    async_to_sync(get_channel_layer().group_send)(
        f'api-vote-session-{instance.election.session.pk}',
        {'type': 'send_update', 'table': 'election', 'instance_id': instance.pk}
    )


