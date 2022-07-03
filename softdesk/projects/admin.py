from django.contrib import admin
from projects.models import Projects, Contributors, Comments, Issues


admin.site.register(Projects)
admin.site.register(Contributors)
admin.site.register(Comments)
admin.site.register(Issues)
