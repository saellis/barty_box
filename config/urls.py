from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import barty_box.views

# Examples:
# url(r'^$', 'gettingstarted.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

urlpatterns = [
    url(r'^$', barty_box.views.index, name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^auth_url/', barty_box.views.auth_url, name='auth_url'),
    url(r'^ride_finder/', barty_box.views.ride_finder, name='ride_finder'),
    url(r'^caller/', barty_box.views.caller, name='caller'),
    url(r'^wait/', barty_box.views.wait, name='wait'),
    url(r'^get_ride_update/', barty_box.views.get_ride_update, name='get_ride_update'),
    url(r'^surge_accept/', barty_box.views.surge_accept, name='surge_accept'),
    url(r'^get_ride_request/', barty_box.views.get_ride_request, name='get_ride_request'),
]
