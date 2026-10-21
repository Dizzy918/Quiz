from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import WaitingPlayer


class WaitingRoomJoinView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not WaitingPlayer.enqueue(request.user):
            return Response(
                {"detail": "Unable to join the waiting room."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"waiting": True}, status=status.HTTP_201_CREATED)


class WaitingRoomLeaveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        WaitingPlayer.withdraw(request.user)
        return Response({"waiting": False}, status=status.HTTP_200_OK)