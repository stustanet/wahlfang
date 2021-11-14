from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.views import TokenViewBase

from vote.forms import VoteForm
from vote.models import Election, Voter, Application, Session
from wahlfang_api.authentication import IsVoter, IsElectionManager, ElectionManagerJWTAuthentication, \
    VoterJWTAuthentication
from wahlfang_api.serializers import (
    TokenObtainVoterSerializer,
    TokenObtainElectionManagerSerializer,
    ElectionSerializer,
    VoterDetailSerializer,
    EditApplicationSerializer,
    SpectatorSessionSerializer,
    SessionSerializer,
    ElectionSerializerManager
)


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
    authentication_classes = [VoterJWTAuthentication]
    queryset = Voter.objects.all()
    permission_classes = [IsVoter]
    serializer_class = VoterDetailSerializer

    def get_object(self):
        return self.request.user


class SpectatorView(generics.RetrieveAPIView):
    queryset = Session.objects.all()
    serializer_class = SpectatorSessionSerializer

    def get_object(self):
        return self.queryset.get(spectator_token=self.kwargs['uuid'])


# Management Sessions #

class ManagerSessionView(generics.ListCreateAPIView, generics.DestroyAPIView):
    authentication_classes = [ElectionManagerJWTAuthentication]
    permission_classes = [IsElectionManager]
    serializer_class = SessionSerializer

    def get_object(self):
        # TODO: Replace query parameter with correct REST guideline /:pk
        session = get_object_or_404(Session, pk=self.request.query_params.get('pk'))
        return session

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)

    def get_queryset(self):
        manager = self.request.user
        return manager.sessions.order_by('-pk')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ManagerElectionView(generics.ListCreateAPIView, generics.DestroyAPIView):
    authentication_classes = [ElectionManagerJWTAuthentication]
    permission_classes = [IsElectionManager]
    serializer_class = ElectionSerializerManager

    def get_object(self):
        election = get_object_or_404(Election, pk=self.request.query_params.get('pk'))
        return election

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        manager_sesions = self.request.user.sessions.all()
        elections_manager = Election.objects.filter(session__in=manager_sesions)
        return elections_manager

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ManagerSessionVoterView(generics.ListCreateAPIView, generics.DestroyAPIView):
    """
    Deals with Voters within a session
    """
    authentication_classes = [ElectionManagerJWTAuthentication]
    permission_classes = [IsElectionManager]
    serializer_class = VoterDetailSerializer

    def get_queryset(self):
        session = get_object_or_404(Session, pk=self.kwargs['pk'])
        return session.participants


class ElectionViewset(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [VoterJWTAuthentication]
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
