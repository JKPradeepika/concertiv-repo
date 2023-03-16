from django.db.models import QuerySet
from rest_framework import parsers, viewsets

from api.filtersets.DocumentFilterSet import DocumentFilterSet
from api.models.Document import Document
from api.policies import CustomDjangoModelPermissions, DocumentAccessPolicy
from api.serializers.DocumentSerializer import DocumentSerializer, DocumentMetadataSerializer
from api.viewsets.ViewSetHelpers import PageSetPagination


class DocumentViewSet(viewsets.ModelViewSet):
    parser_classes = (parsers.MultiPartParser, parsers.FileUploadParser, parsers.JSONParser)
    permission_classes = [CustomDjangoModelPermissions, DocumentAccessPolicy]
    pagination_class = PageSetPagination
    filterset_class = DocumentFilterSet
    serializer_class = DocumentSerializer

    def get_serializer_class(self):
        if self.request.method.upper() == "PATCH":
            return DocumentMetadataSerializer
        return super().get_serializer_class()

    def get_parsers(self):
        if self.request.method.upper() == "PATCH":
            return [parsers.JSONParser()]
        return super().get_parsers()

    def get_queryset(self) -> QuerySet[Document]:
        queryset = Document.objects.order_by("id")
        return DocumentAccessPolicy.scope_queryset(self.request, queryset)
