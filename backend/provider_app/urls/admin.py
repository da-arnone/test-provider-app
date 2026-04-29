from rest_framework.routers import DefaultRouter

from ..views.admin import ProviderAdminViewSet, ProviderFormAdminViewSet, QuestionAdminViewSet

router = DefaultRouter()
router.register(r"providers", ProviderAdminViewSet)
router.register(r"forms", ProviderFormAdminViewSet)
router.register(r"questions", QuestionAdminViewSet)

urlpatterns = router.urls

