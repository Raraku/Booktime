from django.http import HttpResponse, Http404
import datetime
from django.shortcuts import render


def hello(request):
    return HttpResponse("Hello World")


def current_datetime(request, offset=None):
    if offset == None:
        now = datetime.datetime.now()
        return render(request, "dateapp/current_datetime.html", {"current_date": now})
    else:
        try:
            offset = int(offset)
        except ValueError:
            raise Http404
        dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
        html = "<html><body>In %s hour(s), it will be %s.</body></html>" % (offset, dt)
        return HttpResponse(html)
