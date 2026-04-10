def classFactory(iface):
    from .layer_health_checker import LayerHealthChecker
    return LayerHealthChecker(iface)