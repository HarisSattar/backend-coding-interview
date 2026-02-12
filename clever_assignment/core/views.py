from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class HealthCheckView(APIView):
    """
    API endpoint for health check.
    Returns a simple status response to verify service is running.
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """
        Handle GET request for health check.
        """
        return Response({"status": "ok"}, status=status.HTTP_200_OK)
