from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MovimientoInventario, Inventario


@receiver(post_save, sender=MovimientoInventario)
def actualizar_existencias(sender, instance, created, **kwargs):
    if created:
        inv, _ = Inventario.objects.get_or_create(producto=instance.producto)
        if instance.tipo == 'entrada':
            inv.cantidad_actual += instance.cantidad
        elif instance.tipo == 'salida':
            inv.cantidad_actual = max(0, inv.cantidad_actual - instance.cantidad)
        inv.save()