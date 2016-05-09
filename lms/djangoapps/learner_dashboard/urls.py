"""
Learner's Dashboard urls
"""

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^programs/(?P<programId>[0-9]+)/$', views.view_program_details, name='program_details_view'),
    url(r'^programs/$', views.view_programs, name='program_listing_view'),
]
