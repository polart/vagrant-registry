from django.contrib import admin
from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe

from apps.boxes.models import Box, BoxVersion, BoxProvider, BoxUpload


class BoxVersionAdminInline(admin.TabularInline):
    model = BoxVersion
    extra = 1
    show_change_link = True
    fields = ('version', )


class BoxAdminInline(admin.TabularInline):
    model = Box
    extra = 1
    show_change_link = True
    fields = ('name', 'short_description', 'visibility', )


class BoxAdmin(admin.ModelAdmin):
    model = Box

    readonly_fields = ('date_created', 'date_modified', 'date_updated', )
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
    extra = 1
    show_change_link = True
    fields = ('provider', 'status', 'file_link', 'human_file_size', 'pulls', )
    readonly_fields = ('file_link', 'human_file_size', 'pulls', 'status',)

    def human_file_size(self, obj):
        return obj.human_file_size
    human_file_size.short_description = 'File size'

    def file_link(self, obj):
        if obj.status == BoxProvider.FILLED_IN:
            return mark_safe('<a href="{}">{}.box</a>'.format(
                obj.download_url,
                obj.provider,
            ))
        return None
    file_link.short_description = 'File'


class BoxVersionAdmin(admin.ModelAdmin):
    model = BoxVersion

    fields = ('box', 'version', 'changes', 'date_created', 'date_modified',
              'date_updated', )
    readonly_fields = ('date_created', 'date_modified', 'date_updated', )
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


class BoxUploadAdminInline(admin.TabularInline):
    model = BoxUpload
    extra = 0
    show_change_link = True
    fields = ('provider', 'progress',)
    readonly_fields = ('progress',)

    def has_add_permission(self, request):
        # Can be created only from Box Upload page,
        # since there is a custom JS
        return False

    def progress(self, obj):
        return '{:.0f}% ({}/{})'.format(
            obj.progress_percent,
            obj.progress_size,
            obj.human_file_size,
        )


class BoxProviderAdmin(admin.ModelAdmin):
    model = BoxProvider

    fields = ('version', 'provider', 'status', 'file_link', 'human_file_size',
              'date_created', 'date_modified', 'date_updated', 'pulls', )
    readonly_fields = ('file_link', 'human_file_size', 'date_created',
                       'date_modified', 'date_updated', 'pulls', 'status',)
    list_filter = ('version__box__visibility', 'provider', )
    list_display = ('__str__', 'owner', 'name', 'version_name', 'provider',
                    'visibility',)
    search_fields = ['box__owner__username', 'box__name', 'version',
                     'provider', ]
    inlines = [
        BoxUploadAdminInline,
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
        if obj.status == BoxProvider.FILLED_IN:
            return mark_safe('<a href="{}">{}.box</a>'.format(
                obj.download_url,
                obj.provider,
            ))
        return None
    file_link.short_description = 'File'


class BoxUploadForm(forms.ModelForm):
    api_upload_url = forms.CharField(widget=forms.HiddenInput,)

    class Meta:
        model = BoxUpload
        fields = ('provider', 'file', 'api_upload_url', )

    def __init__(self, *args, **kwargs):
        super(BoxUploadForm, self).__init__(*args, **kwargs)

        self.fields['file'].required = True
        self.fields['file'].widget = forms.FileInput()

        new_choices = [('', '---------')]
        for provider in BoxProvider.objects.empty():
            url = reverse(
                'api:v1:boxupload-list',
                kwargs={
                    'username': provider.owner.username,
                    'box_name': provider.box.name,
                    'version': provider.version.version,
                    'provider': provider.provider,
                }
            )
            new_choices.append((url, str(provider)))

        self.fields['provider'].choices = new_choices

        if self.instance.provider_id:
            self.fields['provider'].initial = reverse(
                'api:v1:boxupload-list',
                kwargs={
                    'username': self.instance.provider.owner.username,
                    'box_name': self.instance.provider.box.name,
                    'version': self.instance.provider.version.version,
                    'provider': self.instance.provider.provider,
                }
            )

        if self.instance.status == BoxUpload.IN_PROGRESS:
            self.fields['file'].help_text = \
                'To continue upload select original file and submit the form'
            self.fields['api_upload_url'].initial = reverse(
                'api:v1:boxupload-detail',
                kwargs={
                    'username': self.instance.owner.username,
                    'box_name': self.instance.box.name,
                    'version': self.instance.version.version,
                    'provider': self.instance.provider.provider,
                    'pk': self.instance.id
                }
            )


class BoxUploadAdmin(admin.ModelAdmin):
    model = BoxUpload
    form = BoxUploadForm

    fields = ('provider', 'file', 'api_upload_url',
              'human_file_size', 'progress_percent', 'status', 'checksum_type',
              'checksum', 'date_created', 'date_modified', )
    readonly_fields = ('human_file_size', 'status', 'checksum_type',
                       'checksum', 'date_created', 'date_modified', 'progress_percent', )
    list_filter = ('status', 'provider__version__box__visibility',
                   'provider__provider', )
    list_display = ('__str__', 'owner', 'name', 'version', 'provider',
                    'visibility', 'progress', 'status', )
    search_fields = [
        'provider__version__box__owner__username',
        'provider__version__box__name', 'version'
    ]

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
                    'provider', 'file',
                    'human_file_size', 'status', 'checksum_type', 'checksum',
                    'date_created', 'date_modified', 'progress_percent',
                )
            else:
                return (
                    'provider', 'human_file_size', 'status', 'checksum_type',
                    'checksum', 'date_created', 'date_modified',
                    'progress_percent',
                )
        else:
            return self.readonly_fields

    def human_file_size(self, obj):
        return obj.human_file_size
    human_file_size.short_description = 'File size'

    def owner(self, obj):
        return obj.owner
    owner.admin_order_field = 'provider__version__box__owner'

    def name(self, obj):
        return obj.box.name
    name.admin_order_field = 'provider__version__box__name'

    def visibility(self, obj):
        return obj.box.get_visibility_display()
    visibility.admin_order_field = 'provider__version__box__visibility'

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
