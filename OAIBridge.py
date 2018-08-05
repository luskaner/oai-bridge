from os.path import join

import requests
import urllib.parse
from lxml import etree
from datetime import datetime

from yaml import load
from flask_caching import Cache
from flask import Flask, request, render_template, Response, send_from_directory


def set_config(configuration_data=None):
    if not configuration_data:
        with open('configuration.yaml', 'r') as configuration:
            return load(configuration)
    else:
        return configuration_data


# Init code
app = Flask(__name__)
data = set_config()
cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/<context>")
def root(context):
    if request.args.get('verb') == 'Identify':
        return identify()
    elif request.args.get('verb') == 'ListMetadataFormats':
        return list_metadata_formats()
    elif request.args.get('verb') == 'ListRecords':
        from_date = request.args.get('from')
        until_date = request.args.get('until')
        resumption_token = request.args.get('resumptionToken')
        return list_records(context, from_date, until_date, resumption_token)


def render_xml_template(template, **params):
    return Response(render_template(template + '.xml', **params, **get_default_variables()), mimetype='text/xml')


def get_default_variables():
    return {
        'time': datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    }


def xstr(s):
    return '' if s is None else str(s)


def clean_dict(d):
    return {k: v for k, v in d.items() if v is not None and v != ''}


def dict_empty_str_to_none(d):
    for k, v in d.items():
        if v == '':
            d[k] = None
    return d


def get_query_data(context, from_date=None, until_date=None, resumption_token=None, set_name=None, server_id=None):
    params = {'verb': 'ListRecords', 'from': from_date, 'until': until_date, 'metadataPrefix': 'oai_dc'}
    if resumption_token is not None:
        params['resumptionToken'], server_id, params['from'], params['until'], params['set'] = \
            extract_resumption_token(resumption_token)
        server = data['contexts'][context][server_id]['url']
    else:
        if server_id is None:
            server_id = next(iter(data['contexts'][context]))
        server_config = data['contexts'][context][server_id]
        server = server_config['url']
        if set_name is None and 'sets' in server_config:
            set_name = server_config['sets'][0]
        params['set'] = set_name

    params_clean = clean_dict(params)
    params['server_id'] = server_id
    if 'resumptionToken' in params_clean:
        for k in ['from', 'until', 'set', 'metadataPrefix']:
            params_clean.pop(k, None)
    return server, params_clean, dict_empty_str_to_none(params)


def identify():
    return render_xml_template("Identify", repositoryIdentifier=request.host.split(":")[0])


def list_metadata_formats():
    return render_xml_template("ListMetadataFormats")


@cache.memoize(timeout=60)
def get_records(url, params):
    print("GET: " + str(url) + "?" + urllib.parse.urlencode(params))
    response = requests.get(url, params=params)
    xml = etree.fromstring(response.content)
    ns = '{http://www.openarchives.org/OAI/2.0/}'
    new_resumption_token = xml.find("./{ns}ListRecords/{ns}resumptionToken".format(ns=ns))
    records = xml.findall("./{ns}ListRecords/{ns}record".format(ns=ns))
    records_text = ""
    if records is not None:
        for record in records:
            records_text += etree.tostring(record, encoding='unicode')
    return records_text, new_resumption_token.text if new_resumption_token is not None and new_resumption_token.text else None


def extract_resumption_token(resumption_token):
    if type(resumption_token) is not str:
        return None, None, None, None, None
    resumption_tokens = resumption_token.split("__")
    gen_resumption_token = resumption_tokens[0].split("/")
    if len(resumption_tokens) == 2:
        real_resumption_token = resumption_tokens[1]
    else:
        real_resumption_token = None
    server_id = gen_resumption_token[0]
    from_date = gen_resumption_token[1]
    until_date = gen_resumption_token[2]
    set_name = gen_resumption_token[3]
    return real_resumption_token, server_id, from_date, until_date, set_name


def create_resumption_token(server_id, from_date=None, until_date=None, set_name=None, original_rt=None):
    return "{ID_server}/{from_date}/{until_date}/{set}__{original_rt}".format(
        ID_server=server_id,
        from_date=xstr(from_date),
        until_date=xstr(until_date),
        set=xstr(set_name),
        original_rt=xstr(original_rt)
    )


def get_next_harvest_config(context, server_id, set_name):
    new_server_id = server_id
    new_set = set_name
    index_set = None
    sets = None
    if 'sets' in context[new_server_id]:
        sets = context[new_server_id]['sets']
        if set_name in sets:
            index_set = sets.index(set_name)
    if index_set is not None and index_set < len(sets) - 1:
        new_set = sets[index_set + 1]
    if new_set == set_name:
        servers = list(context.keys())
        for i in range(len(servers)):
            if servers[i] == new_server_id:
                break
        if (i + 1) < len(servers):
            new_server_id = servers[i + 1]
            if 'sets' in context[new_server_id]:
                new_set = context[new_server_id]['sets'][0]
            else:
                new_set = None
    if new_server_id == server_id and new_set == set_name:
        return None, None
    return new_server_id, new_set


def get_next_records_rt(context, from_date=None, until_date=None, resumption_token=None):
    records_text = ''
    current_set_name = None
    current_server_id = None
    changed_set_or_id = False
    while True:
        url, params, params_extra = get_query_data(
            context,
            from_date,
            until_date,
            resumption_token,
            current_set_name,
            current_server_id
        )
        resumption_token = None
        current_server_id, current_set_name, = params_extra['server_id'], params_extra['set']
        from_date, until_date = params_extra['from'], params_extra['until']
        if records_text:
            _, original_rt = get_records(url, params)
        else:
            records_text, original_rt = get_records(url, params)
        if original_rt:
            break

        current_server_id, current_set_name = get_next_harvest_config(
            data['contexts'][context], current_server_id, current_set_name
        )
        if current_server_id is None:
            break
        elif (current_server_id != params_extra['server_id'] or
              current_set_name != params_extra['set']) and records_text:
            changed_set_or_id = True
            break

    if records_text:
        if (original_rt or changed_set_or_id) and current_server_id:
            return records_text, create_resumption_token(current_server_id, from_date, until_date, current_set_name,
                                                         original_rt)
        return records_text, None
    return None, None


def list_records(context, from_date, until_date, resumption_token):
    records_text, new_resumption_token = get_next_records_rt(
        context,
        from_date,
        until_date,
        resumption_token
    )
    if new_resumption_token:
        return render_xml_template("ListRecords", records=records_text, resumptionToken=new_resumption_token)
    return render_xml_template("ListRecords", records=records_text)
