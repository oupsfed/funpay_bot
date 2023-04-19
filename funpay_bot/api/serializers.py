import datetime

from lots.models import FindingLot, FollowingLot, Game, Item, Lot, Server
from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    subscribe_time = serializers.DateTimeField(
        format='%d.%m.%Y',
        default=datetime.datetime.now() + datetime.timedelta(days=3))

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'telegram_chat_id',
            'subscribe_time',
            'is_staff'
        )
        read_only_fields = ('subscribe_time',)


class LotSerializer(serializers.ModelSerializer):
    game = serializers.SerializerMethodField()
    game_id = serializers.SerializerMethodField()

    class Meta:
        model = Lot
        fields = ('id', 'name', 'link', 'game', 'game_id',
                  'allow_monitoring',
                  'allow_finding')

    def get_game(self, obj):
        return f'{obj.game.name} {obj.game.loc}'

    def get_game_id(self, obj):
        return obj.game.id


class ItemSerializer(serializers.ModelSerializer):
    server = serializers.SerializerMethodField()
    lot = LotSerializer()

    class Meta:
        model = Item
        fields = ('id',
                  'server',
                  'seller',
                  'online',
                  'name',
                  'amount',
                  'price',
                  'lot',
                  'link'
                  )

    def get_server(self, obj):
        return f'{obj.server.name}'


class GameSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов для рецептов."""
    lots = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ('id', 'name', 'loc_id', 'loc', 'lots')

    def get_lots(self, obj):
        lots = Lot.objects.filter(game=obj)
        serializer = LotSerializer(data=lots, many=True)
        serializer.is_valid()
        return serializer.data


class ServerSerializer(serializers.ModelSerializer):
    game = GameSerializer()

    class Meta:
        model = Server
        fields = ('id', 'game', 'name')


class FollowingLotSerializer(serializers.ModelSerializer):
    lot = LotSerializer()
    server = ServerSerializer()
    user = UserSerializer()

    class Meta:
        model = FollowingLot
        fields = ('id', 'lot', 'server', 'price', 'user',
                  'monitoring_online_sellers')


class FindingLotSerializer(serializers.ModelSerializer):
    lot = LotSerializer()
    server = ServerSerializer()
    user = UserSerializer()

    class Meta:
        model = FindingLot
        fields = ('id', 'lot', 'server', 'price', 'user',
                  'name',
                  'monitoring_online_sellers')
