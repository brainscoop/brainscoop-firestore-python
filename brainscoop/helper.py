def id_from_name(first, last):
    return u'{}{}'.format(first[0].lower(), last.lower())


def dict_from_kv_opt(opt):
    d = {}
    try:
        k, v = opt.split('=', 1)
    except ValueError:
        raise ValueError('Error: wrong option format (-f key=value).')
    d[k] = u'{}'.format(v)
    return d
