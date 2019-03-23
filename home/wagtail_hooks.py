from wagtail.core import hooks
from hitcount.models import HitCount
from hitcount.views import HitCountMixin


@hooks.register('before_serve_page')
def register_hit_count(page, request, serve_args, serve_kwargs):
    # get hit_count for page
    hit_count = HitCount.objects.get_for_object(page)

    # attempt to register hit
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    return
    '''
    if not request.is_preview:
        # first get the related HitCount object for your model object
        hit_count = HitCount.objects.get_for_object(self)
        # next, you can attempt to count a hit and get the response
        # you need to pass it the request object as well
        hit_count_response = HitCountMixin.hit_count(request, hit_count)
    return super().serve(request, *args, **kwargs)

    #if request.META.get('HTTP_USER_AGENT') == 'GoogleBot':
    #    return HttpResponse("<h1>bad googlebot no cookie</h1>")
    '''