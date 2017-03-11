from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.boxes.models import BoxUpload, BoxProvider, BoxVersion, Box


@receiver(post_delete, sender=BoxUpload,
          dispatch_uid='box_upload_delete_handler')
def box_upload_delete_handler(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)


@receiver(post_save, sender=BoxProvider,
          dispatch_uid='box_provider_date_updated_handler')
def box_provider_date_updated_handler(sender, instance, raw, created, **kwargs):
    if created:
        BoxVersion.objects.filter(pk=instance.version_id).update(
            date_updated=instance.date_updated
        )
        Box.objects.filter(pk=instance.version.box_id).update(
            date_updated=instance.date_updated
        )


@receiver(post_save, sender=BoxVersion,
          dispatch_uid='box_version_date_updated_handler')
def box_version_date_updated_handler(sender, instance, raw, created, **kwargs):
    if created:
        Box.objects.filter(pk=instance.box_id).update(
            date_updated=instance.date_updated
        )
