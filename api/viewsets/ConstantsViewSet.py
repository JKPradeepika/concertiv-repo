from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.constants import CONSTANTS_OBJECTS
from api.helpers import ConstantEntity


class ConstantViewSet(viewsets.ViewSet):
    """
    Dynamic Viewset for constants based on basename
    """

    permission_classes = (AllowAny,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.obj = CONSTANTS_OBJECTS[self.__dict__["basename"]]

    def list(self, request):
        if isinstance(self.obj, tuple):
            return Response([ConstantEntity(x).to_dict() for x in self.obj])
        return Response(self.obj)

    def retrieve(self, request, pk=None):
        try:
            pk = int(pk)
        except ValueError:
            pass

        try:
            if isinstance(self.obj, tuple):
                return Response(ConstantEntity([x for x in self.obj if x[0] == pk][0]).to_dict())
            return Response(self.obj[pk])
        except Exception as ex:
            return Response({"error": ex.__str__()}, status=status.HTTP_404_NOT_FOUND)
