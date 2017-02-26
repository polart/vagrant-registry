from django.contrib import admin
from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe

from apps.boxes.models import Box, BoxVersion, BoxProvider, BoxUpload


class BoxVersionAdminInline(admin.TabularInline):
    model = BoxVersion
    extra = 1
    show_change_link = True


class BoxAdmin(admin.ModelAdmin):
    model = Box

    readonly_fields = ('date_created', 'date_modified', )
    list_filter = ('visibility', )
    list_display = ('__str__', 'owner', 'name', 'visibility', )
    search_fields = ['owner__username', 'name']

    inlines = [
        BoxVersionAdminInline,
    ]

    class Media:
        css = {
            "all": ("css/admin.css", 'css/select2.min.css', )
        }
        js = (
            'js/jquery-3.1.1.min.js',
            'js/select2.min.js',
            'js/init-select2.js',
        )


class BoxProviderAdminInline(admin.TabularInline):
    model = BoxProvider
    extra = 0
    show_change_link = True
    fields = ('provider', 'file', 'human_file_size', 'date_modified', 'pulls', )
    readonly_fields = ('file', 'human_file_size', 'date_modified', 'pulls',)

    def has_add_permission(self, request):
        return False

    def human_file_size(self, obj):
        return obj.human_file_size
    human_file_size.short_description = 'File size'


class BoxVersionAdmin(admin.ModelAdmin):
    model = BoxVersion

    fields = ('box', 'version', 'changes', 'date_created', 'date_modified',)
    readonly_fields = ('date_created', 'date_modified', )
    list_filter = ('box__visibility', )
    list_display = ('__str__', 'owner', 'name', 'version', 'visibility',)
    search_fields = ['box__owner__username', 'box__name', 'version', ]

    inlines = [
        BoxProviderAdminInline,
    ]

    class Media:
        css = {
            "all": ("css/admin.css", 'css/select2.min.css', )
        }
        js = (
            'js/jquery-3.1.1.min.js',
            'js/select2.min.js',
            'js/init-select2.js',
        )

    def owner(self, obj):
        return obj.owner
    owner.admin_order_field = 'box__owner'

    def name(self, obj):
        return obj.box.name
    name.admin_order_field = 'box__name'

    def visibility(self, obj):
        return obj.box.get_visibility_display()
    visibility.admin_order_field = 'box__visibility'


class BoxProviderAdmin(admin.ModelAdmin):
    model = BoxProvider

    fields = ('version', 'provider', 'file_link', 'human_file_size',
              'date_created', 'date_modified', 'pulls', )
    readonly_fields = ('file_link', 'human_file_size', 'date_created',
                       'date_modified', 'pulls',)
    list_filter = ('version__box__visibility', 'provider', )
    list_display = ('__str__', 'owner', 'name', 'version_name', 'provider',
                    'visibility',)
    search_fields = ['box__owner__username', 'box__name', 'version',
                     'provider', ]

    class Media:
        css = {
            "all": ("css/admin.css", 'css/select2.min.css', )
        }
        js = (
            'js/jquery-3.1.1.min.js',
            'js/select2.min.js',
            'js/init-select2.js',
        )

    def has_add_permission(self, request):
        return False

    def human_file_size(self, obj):
        return obj.human_file_size
    human_file_size.short_description = 'File size'

    def owner(self, obj):
        return obj.owner
    owner.admin_order_field = 'version__box__owner'

    def name(self, obj):
        return obj.version.box.name
    name.admin_order_field = 'version__box__name'

    def version_name(self, obj):
        return obj.version.version
    version_name.admin_order_field = 'version__version'
    version_name.short_description = 'Version'

    def visibility(self, obj):
        return obj.version.box.get_visibility_display()
    visibility.admin_order_field = 'version__box__visibility'

    def file_link(self, obj):
        return mark_safe('<a href="{}">{}.box</a>'.format(
            obj.download_url,
            obj.provider,
        ))
    file_link.short_description = 'File'


class BoxUploadForm(forms.ModelForm):
    api_upload_url = forms.CharField(widget=forms.HiddenInput,)

    class Meta:
        model = BoxUpload
        fields = ('box', 'version', 'provider', 'file', 'api_upload_url', )

    def __init__(self, *args, **kwargs):
        super(BoxUploadForm, self).__init__(*args, **kwargs)

        self.fields['file'].required = True
        self.fields['file'].widget = forms.FileInput()

        if self.instance.box_id:
            self.fields['file'].help_text = \
                'To continue upload select original file and submit the form'
            self.fields['api_upload_url'].initial = reverse(
                'api:v1:boxupload-detail',
                kwargs={
                    'username': self.instance.owner.username,
                    'box_name': self.instance.box.name,
                    'pk': self.instance.id
                }
            )


class BoxUploadAdmin(admin.ModelAdmin):
    model = BoxUpload
    form = BoxUploadForm

    fields = ('box', 'version', 'provider', 'file',
              'api_upload_url',
              'human_file_size', 'progress_percent', 'status', 'checksum_type', 'checksum',
              'date_created', 'date_modified', )
    readonly_fields = ('human_file_size', 'status', 'checksum_type',
                       'checksum', 'date_created', 'date_modified', 'progress_percent', )
    list_filter = ('status', 'box__visibility', 'provider', )
    list_display = ('__str__', 'owner', 'name', 'version', 'provider',
                    'visibility', 'progress', 'status', )
    search_fields = ['box__owner__username', 'box__name', 'version',
                     'provider', ]

    class Media:
        css = {
            "all": ("css/admin.css", 'css/select2.min.css', )
        }
        js = (
            'js/jquery-3.1.1.min.js',
            'js/select2.min.js',
            'js/jquery.ui.widget.js',
            'js/jquery.fileupload.js',
            'js/spark-md5.min.js',
            'js/box-upload.js',
            'js/init-select2.js',
        )

    def get_form(self, request, obj=None, **kwargs):
        return self.form

    def get_readonly_fields(self, request, obj=None):
        if obj:
            if obj.status == BoxUpload.COMPLETED:
                return (
                    'box', 'version', 'provider', 'file',
                    'human_file_size', 'status', 'checksum_type', 'checksum',
                    'date_created', 'date_modified', 'progress_percent',
                )
            else:
                return (
                    'box', 'version', 'provider',
                    'human_file_size', 'status', 'checksum_type', 'checksum',
                    'date_created', 'date_modified', 'progress_percent',
                )
        else:
            return self.readonly_fields

    def human_file_size(self, obj):
        return obj.human_file_size
    human_file_size.short_description = 'File size'

    def owner(self, obj):
        return obj.owner
    owner.admin_order_field = 'box__owner'

    def name(self, obj):
        return obj.box.name
    name.admin_order_field = 'box__name'

    def visibility(self, obj):
        return obj.box.get_visibility_display()
    visibility.admin_order_field = 'box__visibility'

    def progress_percent(self, obj):
        return '{:.0f}%'.format(obj.progress_percent)
    progress_percent.short_description = 'Progress'

    def progress(self, obj):
        return '{:.0f}% ({}/{})'.format(
            obj.progress_percent,
            obj.progress_size,
            obj.human_file_size,
        )
    visibility.admin_order_field = 'offset'


admin.site.register(Box, BoxAdmin)
admin.site.register(BoxVersion, BoxVersionAdmin)
admin.site.register(BoxProvider, BoxProviderAdmin)
admin.site.register(BoxUpload, BoxUploadAdmin)
