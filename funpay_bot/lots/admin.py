from django.contrib import admin

from .models import FollowingLot, Item, Lot, Server


class LotAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'game',
        'link',
        'allow_monitoring',
    )
    list_display_links = ('name',)
    list_filter = ('allow_monitoring',
                   'name',)
    search_fields = ('game__name',)
    empty_value_display = '-пусто-'


class FollowingLotAdmin(admin.ModelAdmin):
    list_display = (
        'lot',
        'user',
        'link'
    )
    list_display_links = ('lot',)
    empty_value_display = '-пусто-'

    def lot(self, obj):
        return obj.lot.filter(allow_monitoring=True)

    def link(self, obj):
        return obj.lot.link


admin.site.register(Lot, LotAdmin)
admin.site.register(FollowingLot, FollowingLotAdmin)
admin.site.register(Server)
admin.site.register(Item)
