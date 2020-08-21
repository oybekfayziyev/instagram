import types

def api_view_serializer_class_getter(serializer_class_getter):
    
    def _get_serializer_class(self):
        return serializer_class_getter()
    
    def _get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        return serializer_class(*args, **kwargs)
    
    def decorator(func):
        if not hasattr(func, 'cls'):
            raise Exception(
                "@api_view_serializer_class_getter can only decorate"
                "@api_view decorated functions"
        )

        api_cls = func.cls  
        api_cls.get_serializer_class = types.MethodType(_get_serializer_class, api_cls)
        
        if not hasattr(api_cls, 'get_serializer'):
            api_cls.get_serializer = types.MethodType(
                _get_serializer, api_cls
            )
            return func
        return decorator

def api_view_serializer_class(serializer_class):
    return api_view_serializer_class_getter(lambda: serializer_class)
