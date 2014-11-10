from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^getEnergyVm$', 'energy.views.get_vm_menu'),
    url('^getVariation$', 'energy.views.get_variation'),
    url(r'^getProject$', 'energy.views.get_project_menu'),

    url(r'^$','energy.views.login'),
    url(r'^energy_vm$','energy.views.get_energy_per_vm'),
    url(r'^overview$','energy.views.get_overview_menu'),
    url(r'^authentication$','energy.views.authentication_request'),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^adm$', 'energy.views-admin.home'),
    url(r'^admOverview$', 'energy.views.get_admin_overview'),
    url(r'^admHosts$', 'energy.views.get_admin_hosts'),
    url(r'^admProj$', 'energy.views.get_admin_project_menu'),
    url(r'^admVariation$', 'energy.views.get_admin_variation'),
)
