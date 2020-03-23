class HeadRequestRemoveContentMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method == 'HEAD':
            # response['Content-Length'] = len(response.content)
            response.content = b''
        return response
