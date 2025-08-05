from helpers import distance_between

def get_nearby_drivers(order, drivers, radius_km=20):
    """
    Filter drivers who are within a given radius (in km) of the order's destination.

    Args:
        order: An object with destination_latitude and destination_longitude attributes.
        drivers: A list of driver objects, each with latitude and longitude.
        radius_km (float): The distance radius in kilometers.

    Returns:
        list of tuples: (driver, distance) sorted by distance ascending.
    """
    nearby = []
    for driver in drivers:
        if all([
            driver.latitude is not None,
            driver.longitude is not None,
            order.destination_latitude is not None,
            order.destination_longitude is not None
        ]):
            distance = distance_between(
                {'lat': driver.latitude, 'lng': driver.longitude},
                {'lat': order.destination_latitude, 'lng': order.destination_longitude}
            ) or 0
            if distance <= radius_km:
                nearby.append(driver)
    return nearby
