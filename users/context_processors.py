from .navigation import SIDEBAR_LINKS

def sidebar_menu(request):
    if not request.user.is_authenticated:
        return {'sidebar_links': []}

    authorized_links = []

    for link in SIDEBAR_LINKS:
        required_permission = link.get('permission')
        if not required_permission or request.user.has_perm(required_permission):
            link['is_active'] = (request.resolver_match.url_name == link['url'])
            authorized_links.append(link)
    return {'sidebar_links': authorized_links}