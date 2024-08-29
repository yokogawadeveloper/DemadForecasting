from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from django.contrib.auth.models import User
from rest_framework.decorators import permission_classes, api_view


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
	@classmethod
	def get_token(cls, user):
		token = super().get_token(user)
		token['role'] = user.roleOfEmployee
		return token


class Login(TokenObtainPairView):
	serializer_class = MyTokenObtainPairSerializer




# @csrf_exempt
# @permission_classes((IsAuthenticated, ))
# @api_view(['GET',])
# def logout(request):
# 	username = request.user.username
# 	if username is not None:
# 		# User.objects.filter(username=username).update(last_login=datetime.datetime.now())
# 		try:
# 			auth.logout(request)
# 			return Response({'statustext': 'Success','status':status.HTTP_200_OK})
# 		except Exception as e:
# 			return Response({'error':str(e),'status':status.HTTP_400_BAD_REQUEST})
# 	else:
# 		return Response({'error': 'username not provided','status':status.HTTP_404_NOT_FOUND})





# class Login(APIView):
# 	permission_classes = (AllowAny,)

# 	def post(self, request, format=None):
# 		# print(username, password)
# 		username = request.data.get('username')
# 		password = request.data.get('password')
# 		if username is None or password is None:
# 			return Response({'error': 'Please provide both username and password','status':status.HTTP_404_NOT_FOUND})

# 		user = authenticate(username=username, password=password)
# 		if not user:
# 			return Response({'error':'Invalid Credentials','status':status.HTTP_404_NOT_FOUND})
# 		token, created = Token.objects.get_or_create(user=user)
# 		return Response({'message': "Login successful","token":token.key, "status":status.HTTP_200_OK})
# 		# return Response({'message': message}, status=status.HTTP_200_OK)



# class Logout(APIView):
# 	permission_classes = (IsAuthenticated,)

# 	def get(self, request, format=None):
# 		print(request.user)
# 		if request.user: 
# 			request.user.auth_token.delete()
# 			return Response("logged out",status=status.HTTP_200_OK)
# 		return Response("No permission",status=status.HTTP_404_NOT_FOUND)

