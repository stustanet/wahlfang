from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.views import TokenViewBase

from rest_api.authentication import IsVoter
from rest_api.serializers import (
    TokenObtainVoterSerializer,
    TokenObtainElectionManagerSerializer,
    ElectionSerializer,
    VoterDetailSerializer, EditApplicationSerializer
)
from vote.forms import VoteForm
from vote.models import Election, Voter, Application


class TokenObtainVoterView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    throttle_classes = [AnonRateThrottle]
    serializer_class = TokenObtainVoterSerializer


class TokenObtainElectionManagerView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    throttle_classes = [AnonRateThrottle]
    serializer_class = TokenObtainElectionManagerSerializer


class VoterInfoView(generics.RetrieveAPIView):
    queryset = Voter.objects.all()
    permission_classes = [IsVoter]
    serializer_class = VoterDetailSerializer

    def get_object(self):
        return self.request.user


class ElectionViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Election.objects.all()
    permission_classes = [IsVoter]
    serializer_class = ElectionSerializer

    def get_queryset(self):
        voter_session = self.request.user.session
        return Election.objects.filter(session=voter_session)

    @action(detail=True, methods=['post'])
    def perform_vote(self, request, pk=None):
        election = self.get_object()

        form = VoteForm(request, election=election, data=request.data)
        if form.is_valid():
            form.save()
            async_to_sync(get_channel_layer().group_send)(
                f'api-vote-session-{election.session.pk}',
                {'type': 'send_update', 'table': 'election'}
            )
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(data=form.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'])
    def application(self, request, pk=None):
        election = self.get_object()
        application = request.user.application.first()

        if request.method == 'POST':
            if not application:
                application = Application(election=election, voter=request.user)

            serializer = EditApplicationSerializer(data=request.data, instance=application)
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            if not application:
                return Response(data={'error': 'not found'}, status=status.HTTP_404_NOT_FOUND)
            application.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)
