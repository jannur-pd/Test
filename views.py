
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from .models import *
from functools import partial
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from .serializer import *

class PhotographerAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        photographers = Photographer.objects.all()
        serializer = PhotographerSerializer(photographers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        new_photographer = PhotographerSerializer(data=request.data)
        if new_photographer.is_valid():
            new_photographer.save(user=request.user)
            return Response(data={'message': 'New photographer Created'}, status=status.HTTP_200_OK)
        else:
            return Response(data=new_photographer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        photographer = Photographer.objects.get(id=request.data.get('id'))

        if photographer.user != request.user:
            return Response({'error': 'You do not have permission to edit this photographer profile'},
                            status=status.HTTP_403_FORBIDDEN)

        updated_ph = PhotographerSerializer(instance=photographer, data=request.data, partial=True)
        if updated_ph.is_valid():
            updated_ph.save()
            return Response(data={'message': 'Photographer Updated'}, status=status.HTTP_200_OK)
        else:
            return Response(data=updated_ph.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        photographer = Photographer.objects.get(id=request.data.get('id'))
        photographer.delete()
        return Response(data={'message': 'Photographer Deleted'}, status=status.HTTP_200_OK)


class ProfilePicAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = ProfilePicSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        user = request.user
        if user.role != 'photographer':
            raise PermissionDenied('Only photographers can upload profile pictures.')
        serializer = ProfilePicSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile picture updated successfully!'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PhotographerSearchAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        niche = request.GET.get('niche')
        max_price = request.GET.get('max_price')
        languages = request.GET.get('languages')

        photographers = Photographer.objects.all()

        if niche:
            photographers = photographers.filter(niche__name__icontains=niche)

        if max_price:
            try:
                max_price = int(max_price)
                photographers = photographers.filter(price_per_hour__lte=max_price)
            except ValueError:
                return Response({'error': 'Invalid value for max_price'}, status=status.HTTP_400_BAD_REQUEST)

        if languages:
            photographers = photographers.filter(languages_spoken__name__icontains=languages)

        data = PhotographerSerializer(photographers, many=True)
        return Response(data.data, status=status.HTTP_200_OK)




class AuthApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from django.contrib.auth import authenticate, login
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(data={'message': 'Username and password are required!'})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response(data={'message': 'Login successful!'}, status=status.HTTP_200_OK)
        else:
            return Response(data={'message': 'Invalid email or password!'},
                            status=status.HTTP_400_BAD_REQUEST)

class LogOutApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.contrib.auth import logout
        logout(request)
        return Response(data={'message': 'Logout successful!'}, status=status.HTTP_200_OK)



class QuotesApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        url = "https://zenquotes.io/api/random"

        try:

            response = requests.get(url)

            if response.status_code == 200:
                quote_data = response.json()
                quote = quote_data[0]['q']
                author = quote_data[0]['a']
                return Response({"quote": quote, "author": author})
            else:
                return Response({"error": "Failed to get the quote. Please try again later"}, status=500)

        except requests.exceptions.RequestException as e:
            return Response({"error": f"Error while connecting to the API: {e}"}, status=500)




# фотографам (доб. фоток)
class PhotoCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'photographer':
            return Response({'detail': 'Only photographers can upload photos.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        photographer = Photographer.objects.get(user=request.user)
        photo = Portfolio.objects.create(
            photographer=photographer,
            image=data.get('image'),
            description=data.get('description')
        )
        serializer = PhotoSerializer(photo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# клиентам (создание отзывов)
class ReviewCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'client':
            return Response({'detail': 'Only clients can leave reviews.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        review = Review.objects.create(
            client=request.user,
            photographer_id=data.get('photographer'),
            rating=data.get('rating'),
            comment=data.get('comment')
        )
        serializer = ReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_201_CREATED)




class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = ProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NewPhotographersApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        sorting = request.GET.get('sorting')
        if sorting is None:
            photographers = Photographer.objects.all()

        else:
            if sorting == 'ph-asc':
                photographers = Photographer.objects.all().order_by('price_per_hour')
            elif sorting == 'ph-desc':
                photographers = Photographer.objects.all().order_by('-price_per_hour')
            elif sorting == 'first_name-asc':
                photographers = Photographer.objects.all().order_by('first_name')
            elif sorting == 'first_name-desc':
                photographers = Photographer.objects.all().order_by('-first_name')
        data = PhotographerSerializer(instance=photographers, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)
