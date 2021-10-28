from django.urls import include, path
from rest_framework_nested import routers
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from wahlfang_api.views import (
    TokenObtainVoterView,
    TokenObtainElectionManagerView,
    ElectionViewset,
    VoterInfoView,
    SpectatorView,
    ManagerSessionView
)

app_name = 'rest_api'

router = routers.SimpleRouter()
router.register('vote/elections', ElectionViewset)

urlpatterns = [
    path('', include(router.urls)),
    path('vote/spectator/<str:uuid>/', SpectatorView.as_view(), name='spectator'),
    path('vote/voter_info/', VoterInfoView.as_view(), name='voter_info'),
    path('auth/code/token/', TokenObtainVoterView.as_view(), name='token_obtain_access_code'),
    path('auth/token/', TokenObtainElectionManagerView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('manager/add-session', ManagerSessionView.as_view(), name='add_session'),
    path('drf/', include('rest_framework.urls', namespace='rest_framework'))
]
