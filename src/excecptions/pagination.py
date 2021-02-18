from flask import url_for


def pagination(url, requestor, search):
    prev_page = ''
    next_page = ''
    if search:
        if requestor.has_next:
            extra_args = {'search': search, 'page': requestor.next_num}
            next_page = url_for(url, **extra_args)
        if requestor.has_prev:
            extra_args = {'search': search, 'page': requestor.prev_num}
            prev_page = url_for(url, **extra_args)
    else:
        if requestor.has_next:
            extra_args = {'page': requestor.next_num}
            next_page = url_for(url, **extra_args)
        if requestor.has_prev:
            extra_args = {'page': requestor.prev_num}
            prev_page = url_for(url, **extra_args)

    return prev_page, next_page
