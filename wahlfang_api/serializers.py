from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import serializers, fields
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken


from vote.models import Election, Session, Application, Voter


class TokenObtainVoterSerializer(serializers.Serializer):  # pylint: disable=W0223

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['access_code'] = serializers.CharField()

    def validate(self, attrs):
        authenticate_kwargs = {
            'access_code': attrs['access_code'],
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        user = authenticate(**authenticate_kwargs)
        if not user:
            raise serializers.ValidationError('could not authenticate user')

        refresh = self.get_token(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return data

    @classmethod
    def get_token(cls, user):
        token = RefreshToken.for_user(user)
        token[settings.JWT_CLAIM_USER_TYPE] = user.__class__.__name__
        return token


class TokenObtainElectionManagerSerializer(TokenObtainPairSerializer):  # pylint: disable=W0223
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token[settings.JWT_CLAIM_USER_TYPE] = user.__class__.__name__
        return token


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        exclude = ['email', 'voter']


class EditApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        exclude = ['voter', 'election', 'id']


class ElectionSummarySerializer(serializers.ModelSerializer):
    votes_accept = serializers.IntegerField()
    votes_reject = serializers.IntegerField()
    votes_abstention = serializers.IntegerField()

    class Meta:
        model = Application
        exclude = ['email', 'voter']


class ElectionSerializer(serializers.ModelSerializer):
    # TODO: also include whether the voter already voted
    applications = ApplicationSerializer(many=True, read_only=True)
    can_vote = serializers.SerializerMethodField()
    election_summary = ElectionSummarySerializer(source='public_election_summary', many=True, read_only=True)
    voter_application = serializers.SerializerMethodField()

    class Meta:
        model = Election
        fields = '__all__'

    def get_voter_application(self, obj):
        application = self.context['request'].user.application.first()
        if not application:
            return None

        return EditApplicationSerializer(application, read_only=True, many=False).data

    def get_can_vote(self, obj):
        return self.context['request'].user.can_vote(obj)


class SpectatorElectionSerializer(serializers.ModelSerializer):
    election_summary = ElectionSummarySerializer(source='public_election_summary', many=True, read_only=True)

    class Meta:
        model = Election
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Session
        fields = ['title', 'start_date']


class VoterDetailSerializer(serializers.ModelSerializer):
    session = SessionSerializer(many=False, read_only=True)

    class Meta:
        model = Voter
        exclude = ['logged_in', 'password']


class SpectatorSessionSerializer(serializers.ModelSerializer):
    elections = SpectatorElectionSerializer(many=True, read_only=True)

    class Meta:
        model = Session
        fields = ['title', 'meeting_link', 'elections']

