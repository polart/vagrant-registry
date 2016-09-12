from django.db.models.signals import post_delete
from django.dispatch import receiver

from apps.boxes.models import BoxUpload


@receiver(post_delete, sender=BoxUpload,
          dispatch_uid='box_upload_delete_handler')
def box_upload_delete_handler(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)
