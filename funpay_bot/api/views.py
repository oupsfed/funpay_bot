from core import alert_users
from core.update import update_games_and_lots, update_items
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from lots.models import FindingLot, FollowingLot, Game, Item, Lot, Server
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from users.models import User

from .serializers import (FindingLotSerializer, FollowingLotSerializer,
                          GameSerializer, ItemSerializer, LotSerializer,
                          ServerSerializer, UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny, ]
    lookup_field = 'telegram_chat_id'
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('telegram_chat_id', 'is_staff')

    @action(
        methods=['GET'],
        permission_classes=(AllowAny,),
        detail=True,
        url_path='following',
    )
    def following(self, request, telegram_chat_id):
        user = get_object_or_404(User, telegram_chat_id=telegram_chat_id)
        following = FollowingLot.objects.filter(user=user)
        serializer = FollowingLotSerializer(data=following, many=True)
        serializer.is_valid()
        return Response(serializer.data, status.HTTP_200_OK)

    @action(
        methods=['POST'],
        permission_classes=(AllowAny,),
        detail=False,
        url_path='alert',
    )
    def alert(self, request):
        return Response(alert_users.alert())


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    pagination_class = None
    permission_classes = [AllowAny, ]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    @action(
        methods=['POST'],
        permission_classes=(AllowAny,),
        detail=False,
        url_path='update_games',
    )
    def update_games(self, request):
        for game in request.data:
            Game.objects.update_or_create(name=game['name'],
                                          loc=game['loc'],
                                          loc_id=game['loc_id']
                                          )
        serializer = self.get_serializer(data=Game.objects.all(), many=True)
        serializer.is_valid()
        return Response(serializer.data, status.HTTP_201_CREATED)

    @action(
        methods=['POST', 'DELETE'],
        permission_classes=(AllowAny,),
        detail=False,
        url_path='update_lots',
    )
    def update_lots(self, request):
        for lot in request.data:
            Lot.objects.update_or_create(
                name=lot['name'],
                game=get_object_or_404(Game, loc_id=lot['loc_id']),
                link=lot['link']
            )
        serializer = self.get_serializer(data=Game.objects.all(), many=True)
        serializer.is_valid()
        return Response(serializer.data, status.HTTP_201_CREATED)

    @action(
        methods=['POST'],
        permission_classes=(AllowAny,),
        detail=False,
        url_path='update',
    )
    def update_all(self, request):
        return Response(update_games_and_lots())

    @action(
        methods=['GET'],
        permission_classes=(AllowAny,),
        detail=False,
        url_path='lots',
    )
    def lots(self, request):
        serializer = LotSerializer(data=Lot.objects.all(), many=True)
        serializer.is_valid()
        return Response(serializer.data, status.HTTP_200_OK)


class LotViewSet(viewsets.ModelViewSet):
    queryset = Lot.objects.all()
    serializer_class = LotSerializer
    permission_classes = [AllowAny, ]
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('game__name',)
    filterset_fields = ('allow_monitoring',
                        'allow_finding')


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [AllowAny, ]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name', 'online')
    search_fields = ('name',)

    @action(
        methods=['GET'],
        permission_classes=(AllowAny,),
        detail=True,
        url_path='following',
    )
    def following(self, request, pk):
        user = get_object_or_404(User, telegram_chat_id=pk)
        servers = FollowingLot.objects.filter(user=user).values('server')
        items = Item.objects.filter(lot__following__user=user,
                                    server__in=servers)
        search = request.query_params.get('search')
        if search:
            items = items.filter(server__name__icontains=search)
        serializer = self.get_serializer(data=items, many=True)
        serializer.is_valid()
        return Response(serializer.data, status.HTTP_200_OK)

    @action(
        methods=['POST'],
        permission_classes=(AllowAny,),
        detail=False,
        url_path='update',
    )
    def update_all(self, request):
        updated_items = update_items()
        alerted_users = alert_users.alert()
        return Response(f'{updated_items} {alerted_users}')


class FollowingLotViewSet(viewsets.ModelViewSet):
    queryset = FollowingLot.objects.all()
    serializer_class = FollowingLotSerializer
    permission_classes = [AllowAny, ]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user__telegram_chat_id',)

    def create(self, request, *args, **kwargs):
        lot = get_object_or_404(Lot, pk=request.data['lot'])
        server = get_object_or_404(Server, pk=request.data['server'])
        user = get_object_or_404(User, telegram_chat_id=request.data['user'])
        data = FollowingLot.objects.create(lot=lot,
                                           server=server,
                                           user=user)
        serializer = FollowingLotSerializer(data=data)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=['POST'],
        permission_classes=(AllowAny,),
        detail=True,
        url_path='change_monitoring',
    )
    def change_monitoring(self, request, pk):
        following_lot = FollowingLot.objects.get(pk=pk)
        monitoring = following_lot.monitoring_online_sellers
        following_lot.monitoring_online_sellers = not monitoring
        following_lot.save()
        serializer = self.get_serializer(following_lot)
        return Response(serializer.data)


class FindingLotViewSet(viewsets.ModelViewSet):
    queryset = FindingLot.objects.all()
    serializer_class = FindingLotSerializer
    permission_classes = [AllowAny, ]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user__telegram_chat_id',)

    def create(self, request, *args, **kwargs):
        lot = get_object_or_404(Lot, pk=request.data['lot'])
        server = get_object_or_404(Server, pk=request.data['server'])
        user = get_object_or_404(User, telegram_chat_id=request.data['user'])
        data = FindingLot.objects.create(lot=lot,
                                         server=server,
                                         user=user,
                                         name=request.data['name'])
        serializer = FindingLotSerializer(data=data)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ServerViewSet(viewsets.ModelViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filterset_fields = ('game__id', 'game__lot__id')
    search_fields = ('name',)
