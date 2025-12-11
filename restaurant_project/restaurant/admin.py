from django.contrib import admin
from .models import MenuItem, Reservation, Order, OrderItem

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_available')
    search_fields = ('name', 'description')



class ReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'date', 'time', 'party_size', 'confirmed', 'created_at')
    list_filter = ('date', 'confirmed')
    search_fields = ('name', 'email', 'phone')

admin.site.register(Reservation, ReservationAdmin)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('menu_item', 'quantity', 'price')
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'created_at', 'status', 'total')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]
