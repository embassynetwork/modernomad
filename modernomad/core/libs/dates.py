import datetime


def dates_within(start, end):
    result = []
    delta = end - start
    for i in range(delta.days + 1):
        day = start + datetime.timedelta(days=i)
        result.append(day)
    return result


def count_range_objects_on_day(objects, day):
    return sum(object.arrive <= day and object.depart > day for object in objects)
