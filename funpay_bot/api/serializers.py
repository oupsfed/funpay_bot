import datetime

from rest_framework import serializers

from lots.models import FollowingLot, Game, Item, Lot, Server
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


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = ('id', 'game', 'name')


class LotSerializer(serializers.ModelSerializer):
    game = serializers.SerializerMethodField()
    game_id = serializers.SerializerMethodField()

    class Meta:
        model = Lot
        fields = ('id', 'name', 'link', 'game', 'game_id', 'allow_monitoring')

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


class FollowingLotSerializer(serializers.ModelSerializer):
    lot = LotSerializer()
    server = ServerSerializer()
    user = UserSerializer()

    class Meta:
        model = FollowingLot
        fields = ('id', 'lot', 'server', 'price', 'user',
                  'monitoring_online_sellers')
