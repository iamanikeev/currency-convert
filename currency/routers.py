from rest_framework.routers import Route, DefaultRouter, DynamicDetailRoute


class CurrencyRouter(DefaultRouter):
    """
    Basic SimpleRouter, added with custom route for currency conversions
    """
    # def __init__(self, *args, **kwargs):
    #     self.trailing_slash = True
    #     super(CurrencyRouter, self).__init__(self, *args, **kwargs)

    routes = [
        DynamicDetailRoute(
            url=r'^{prefix}/{lookup}/convert/(?P<to>[a-zA-Z]{1,3})/(?P<amount>\d+[\.]?\d+&)',
            name='{basename}-{methodnamehyphen}',
            initkwargs={},
        ),
    ]
