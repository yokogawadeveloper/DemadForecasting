from django.conf.urls import url
from .views.views import *
from .views.chartViews import *
from .views.SectorwiseView import *

urlpatterns = [
    url(r'^data/$', DataCrud.as_view(), name="DataCrud"),
    url(r'^download/$', DownloadData.as_view(), name="downloadFiles"),
    url(r'^alert/$', Alert.as_view(), name="Alert"),
    url(r'^staticfileupload/$', StaticFileUpload.as_view(),name="StaticFileUpload"),
    url(r'^chartdata/$', ChartData.as_view(), name="chartData"),
    url(r'^cpastokechartdata/$', CPAStokeChartData.as_view(),name="chartData"),
    url(r'^staticfilesdownload/$', DownloadStaticFiles.as_view(),name="staticfilesdownload"),
    url(r'^datesofinputfiles/$', DatesOfInputfiles.as_view(),name="datesofinputfiles"),
    url(r'^datesofstaticfiles/$', DatesOfStaticfiles.as_view(),name="datesofinputfiles"),
    url(r'^kanban/$', KanbanData.as_view(), name="kanbanData"),
    url(r'^modeltoparts/$', BomExplosion.as_view(),name="modelCodeBreakToParts"),
    url(r'^industrywise/$', Sectorwise.as_view(), name="Sectorwise"),
    url(r'^inventory/$', inventoryGraphData.as_view(), name="inventoryGraph"),
    ]
