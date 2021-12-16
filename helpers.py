import re
import time

def is_what(string):

    string = str(string)
    alpha_num = r'\W'

    if string.isalpha():
        return 'ALPHA'
    elif string.isdigit():
        return 'DIGIT'
    elif not bool(re.search(alpha_num, string)):
        return 'ALPHA_NUM'
    else:
        return 'VARIOUS'


def split_url(url):

    reg_pattern = r'(https?://)'
    url = re.sub(reg_pattern, '', url)
    search_slash = r'/[^/\?]+'
    search_params = r'[\?|\&]([^=]+\=[^&]+)'

    route_pattern = re.compile(search_slash)
    params_pattern = re.compile(search_params)

    routes = route_pattern.findall(url)
    routes = [w.replace('/', '') for w in routes]

    params = params_pattern.findall(url)
    params = [w.replace('/', '') for w in params]

    return {"routes": routes, "params": params}

def split_param(param):

    param = dict([param.split("=")])

    return param


def create_path(existing_tree, routes, params, scraped_jobs):

    new_tree = existing_tree
    root_pos = len(new_tree)
    root = {
        root_pos: { 'content_type': is_what(str(routes[0])),
                    'len_content': len(str(routes[0])),
                    'value': routes[0],
                    'params': {},
                    'len_route': 0,
                    'len_equivalent': 1
        }
    }

    for idx, par in enumerate(params): #iterate through the parameters of the URL
        param = split_param(par)
        root[root_pos]['params'][list(param)[0]] = param[list(param)[0]]

    new_tree.append(root)

    for k in range(1, len(routes)): #iterate through the routes of the URL
        if scraped_jobs != 0:

            new_route = { 'value': routes[k],
                          'content_type': is_what(str(routes[k])),
            }
            new_tree[root_pos][root_pos][k] = new_route
            new_tree[root_pos][root_pos]['len_route'] += 1

    return new_tree


def todict(obj, classkey=None):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        return todict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, todict(value, classkey))
                     for key, value in obj.__dict__.items()
                     if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj
def wait_until(somepredicate, timeout, period=0.25, *args, **kwargs):
    mustend = time.time() + timeout
    while time.time() < mustend:
        if somepredicate(*args, **kwargs):
            return True
        time.sleep(period)
    return False