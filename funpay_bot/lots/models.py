from django.db import models

from users.models import User


class Game(models.Model):
    name = models.CharField(max_length=150)
    loc_id = models.IntegerField(unique=True)
    loc = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f'{self.name} {self.loc}'


class Server(models.Model):
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='server'
    )
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Lot(models.Model):
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='lot'
    )
    name = models.TextField()
    link = models.URLField(unique=True)
    allow_monitoring = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.game.name} {self.game.loc} - {self.name}'


class Item(models.Model):
    server = models.ForeignKey(Server,
                               on_delete=models.CASCADE,
                               related_name='item',
                               null=True,
                               blank=True)
    seller = models.CharField(max_length=100)
    name = models.TextField()
    amount = models.IntegerField()
    price = models.FloatField()
    link = models.URLField(unique=True)
    lot = models.ForeignKey(
        Lot,
        on_delete=models.CASCADE,
        related_name='item'
    )
    online = models.BooleanField()


class FollowingLot(models.Model):
    lot = models.ForeignKey(Lot,
                            on_delete=models.CASCADE,
                            related_name='following')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='following')
    server = models.ForeignKey(Server,
                               on_delete=models.CASCADE,
                               related_name='following',
                               blank=True,
                               null=True)
    price = models.FloatField(blank=True, null=True)
    monitoring_online_sellers = models.BooleanField(default=False)
