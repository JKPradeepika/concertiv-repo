from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from api.models.User import User
from api.serializers.UserSerializer import UserPasswordSerializer
from komodo_backend.settings import config

from django.core.mail import EmailMessage

import uuid


class ForgotPasswordViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = UserPasswordSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.data
        try:
            if User.objects.filter(email=user["email"]).exists():
                temp_pwd = uuid.uuid4().hex[:6]
                user_data = User.objects.filter(email=user["email"]).first()
                if user_data is not None:
                    user_data.set_password(temp_pwd)
                    user_data.save()
                subject = "C360 - Forgot Password"
                from_email = config["EMAIL_HOST_USER"]
                to_email = user_data.email
                login_url = config["BASE_URL"]
                html_content = (
                    "<p>Hi {0}, <br><br>Here's your temporary password for Concertiv 360 platform. "
                    "Please use this password to login <b><i>{1}</i></b><br><br>Click here {2} to login again.<br><br>"
                    "Regards,<br>Concertiv Admin Team</p>".format(user_data.get_first_name(), temp_pwd, login_url)
                )
                email = EmailMessage(subject, html_content, from_email, [to_email])
                email.content_subtype = "html"
                email.send(fail_silently=False)
        except User.DoesNotExist:
            raise ValueError("No user exists with the given email. Please check email and try again")
        return Response({"success": "Forgot Password - An email has been sent successfully"}, status=status.HTTP_200_OK)
