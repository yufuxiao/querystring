from django.conf import settings

from parsers import parser_datetime


def get_str(request, name, default=None):
    """
    获取一个 str 类型的 querystring 参数

    :param request: HttpRequest 对象
    :param name: 参数名称
    :param default: 如果 querystring 中没有该参数，则返回 default。
    :return:
    """
    value = request.GET.get(name)
    if value is None:
        return default

    return value


def get_boolean(request, name, default=None):
    """
    获取一个 str 类型的 querystring 参数

    由于 querystring 的值只能是字符串，因此我们用字符串表示真假：
    * 真：true, t, yes, y, 1 （不区分大小写）
    * 假：false, f, no, n, 0 （不区分大小写）

    返回 True 或 False，如果 querystring 中没有该参数，则返回 default。
    如果参数的值不是有效的真或假，则同样返回 default。
    """
    value = request.GET.get(name)
    if value is None:
        return default

    if value.lower() in ('true', 't', 'yes', 'y', '1'):
        return True

    if value.lower() in ('false', 'f', 'no', 'n', '0'):
        return False

    return default


def get_int(request, name, default=None, raise_on_value_error=False):
    """
    获取一个 int 类型的 querystring 参数

    参数的值必须是整数（支持负数），不支持小数。

    :param request: HttpRequest 对象。
    :param name: 参数名称。
    :param default: 如果 querystring 中没有该参数，则返回 default。
    :param raise_on_value_error: 若为 True，当参数值不是合法整数时，将抛出 ValueError，若为 False（默认），则返回 default 值。
    """
    value = request.GET.get(name)
    if value is None:
        return default

    try:
        return int(value)
    except ValueError as e:
        if raise_on_value_error:
            raise e
        return default


def get_list(request, name, default=None, *, type=str, delim=",", raise_on_value_error=False):
    """
    获取一个数组类型的 querystring 参数

    由于 querystring 的值只能是 str，因此我们使用英文逗号（,）进行分割。分割符也可以使用 `delim` 参数指定。

    :param request: HttpRequest 对象。
    :param name: 参数名称。
    :param type: 转化数据类型，仅支持几个简单的类型，str、int、float、bool 等。
    :param delim: 分割符，默认为英文逗号。
    :param default: 如果 querystring 中没有该参数，则返回 default。
    :param raise_on_value_error: 若为 True，当参数值不是合法整数时，将抛出 ValueError，若为 False（默认），则返回 default 值。
    """
    value = request.GET.get(name)
    if value is None:
        return default

    result_list = []
    items = value.split(delim)
    for item in items:
        item = item.strip()
        if not item:
            continue

        try:
            item = type(item)
        except ValueError as e:
            if raise_on_value_error:
                raise e
            continue

        result_list.append(item)

    return result_list


def get_datetime(request, name, default=None,
                 *,
                 format='%Y-%m-%d %H:%M:%S',
                 align=None,
                 aware=settings.USE_TZ,
                 raise_on_value_error=False,
                 ):
    """
    获取一个 datetime 类型的 querystring 参数。

    :param request: HttpRequest 对象。
    :param name: 参数名称。
    :param default: 如果 querystring 中没有该参数，则返回 default。
    :param format: 时间格式，默认为 "%Y-%m-%d %H:%M:%S"。
    :param align: 取值 "start"、"end" 或 None，
      若为 start，则返回的时间时分秒被设置为 00:00:00，
      若为 end，则返回的时间时分秒被设置为 23:59:59。
    :param aware: 返回的时间是否带有时区，默认取值 settings.USE_TZ。
    :param raise_on_value_error: 若为 True，当参数值不是合法整数时，将抛出 ValueError，若为 False（默认），则返回 default 值。
    """
    value = request.GET.get(name)
    if value is None:
        return default

    try:
        return parser_datetime(value, format, align=align, aware=aware)
    except ValueError as e:
        if raise_on_value_error:
            raise e
        return default


def get_datetime_range(request, name, default=None,
                       *,
                       format='%Y-%m-%d %H:%M:%S',
                       delim=',',
                       align=None,
                       aware=settings.USE_TZ,
                       raise_on_value_error=False,
                       ):
    """
    获取一个 datetime 类型的 querystring 参数。

    :param request: HttpRequest 对象。
    :param name: 参数名称。
    :param default: 如果 querystring 中没有该参数，则返回 default。
    :param format: 时间格式，默认为 "%Y-%m-%d %H:%M:%S"。
    :param delim: 分割符，默认为英文逗号。
    :param align: 取值 "start"、"end" 或 None，
      若为 start，则返回的时间时分秒被设置为 00:00:00，
      若为 end，则返回的时间时分秒被设置为 23:59:59。
    :param aware: 返回的时间是否带有时区，默认取值 settings.USE_TZ。
    :param raise_on_value_error: 若为 True，当参数值不是合法整数时，将抛出 ValueError，若为 False（默认），则返回 default 值。
    """
    value = request.GET.get(name)
    if value is None:
        return default

    if delim not in value:
        if raise_on_value_error:
            raise ValueError(f'datetime range value must contain a delim: {delim}')
        return (default, default)

    start_value, end_value = value.split(delim)
    try:
        _align = "start" if align else None
        start = parser_datetime(start_value, format, align=align, aware=aware)
    except ValueError as e:
        if raise_on_value_error:
            raise e
        return (default, default)

    try:
        _align = "end" if align else None
        end = parser_datetime(end_value, format, align=align, aware=aware)
    except ValueError as e:
        if raise_on_value_error:
            raise e
        return (default, default)

    return (start, end)
