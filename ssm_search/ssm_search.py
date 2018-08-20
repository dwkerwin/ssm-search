from __future__ import print_function
import os
import sys
import re
import argparse
import boto3
import time
import shelve


class colors:
    BLUE = '\033[94m'
    CYAN   = '\033[36m'
    YELLOW = '\033[93m'
    ENDCOLOR = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def search_ssm_params(ssm_params, search_strings):
    num_matches = 0
    secure_string_label = '{}(SecureString){}'.format(colors.YELLOW, colors.ENDCOLOR)
    for parameter in ssm_params:
        found_count = 0
        for search_string in search_strings:
            try:
                if search_string.lower() in parameter['Name'].lower():
                    found_count += 1
            except Exception as e:
                raise ("Error processing parameter: {}\nParameter: {}".format(str(e), parameter))
        if found_count == len(search_strings):
            num_matches += 1
            print("{}{} {}->{} {}".format(
                colors.BLUE,
                parameter['Name'],
                colors.CYAN,
                colors.ENDCOLOR,
                secure_string_label if parameter['Type'] == 'SecureString' else parameter['Value']))


    print("Found {} matches out of {} parameters from SSM".format(
        num_matches,
        len(ssm_params)))


def load_ssm_params(start_prefix, profile_name = None):
    if profile_name:
        session = boto3.session.Session(profile_name=profile_name)
    else:
        session = boto3.session.Session()

    client = session.client('ssm')
    next_token = ''
    page = 1
    full_params = []

    print("Reading parameters from SSM path: {}".format(start_prefix))
    try:
        response = client.get_parameters_by_path(
            Path=start_prefix,
            Recursive=True,
            MaxResults=10,
            WithDecryption=True
        )
        full_params.extend(response['Parameters'])
        if 'NextToken' in response:
            next_token = response['NextToken']
    except Exception as e:
        print("Error querying list of ssm parameters: {}".format(repr(e)))
        raise

    while next_token:
        page += 1
        #print("Reading page {} of parameters by path...".format(page))
        sys.stdout.write('.')
        sys.stdout.flush()
        try:
            response = client.get_parameters_by_path(
                Path=start_prefix,
                Recursive=True,
                WithDecryption=True,
                MaxResults=10,
                NextToken=next_token
            )
            if not response['Parameters']:
                print("Error - No additional parameters found in subsequent page read!")
            full_params.extend(response['Parameters'])
            if 'NextToken' in response:
                next_token = response['NextToken']
            else:
                next_token = ''
        except Exception as e:
            print("Error querying list of ssm parameters: {}".format(repr(e)))
            raise
    sys.stdout.write('\n')

    return full_params


def ssm_cache_filename(start_prefix, profile_name):
    home_dir = os.path.expanduser("~")
    ssm_cache_dir = os.path.join(home_dir, ".ssm_cache")
    start_prefix_alphanumeric = re.sub(r'\W+', '', start_prefix)
    filename = "{}_{}".format(
        start_prefix_alphanumeric,
        profile_name if profile_name else 'default'
    ).replace(' ', '')
    return os.path.join(ssm_cache_dir, filename)


def write_ssm_cache(ssm_cache_filename, ssm_params):
    # cache the ssm results in a local file
    ssm_cache_dir = os.path.dirname(os.path.abspath(ssm_cache_filename))
    if not os.path.exists(ssm_cache_dir):
        os.makedirs(ssm_cache_dir)
    os.remove(ssm_cache_filename)
    shelf = shelve.open(ssm_cache_filename)
    shelf['ssm_params'] = ssm_params
    shelf.close()


def read_ssm_cache(ssm_cache_full_path):
    shelf = shelve.open(ssm_cache_full_path)
    return shelf['ssm_params']


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--search-string', required=True,
                        action='append', dest='search_string',
                        help='The string to search SSM for any parameters with this in the name.')
    parser.add_argument('--profile', required=False,
                        help='The AWS profile to run this request under.' )
    parser.add_argument('--prefix', default='/',
                        help='SSM prefix to start searching from')
    parser.add_argument('--no-cache', action='store_true', default=False,
                        help='Will force fresh loading of parameters from SSM')
    args = parser.parse_args()
    return args
    
    
def main():
    here = os.path.abspath(os.path.dirname(__file__))
    about = {}
    with open(os.path.join(here, 'version.py'), 'r') as f:
        exec(f.read(), about)

    print('SSM Search version {}'.format(about['__version__']))

    args = parse_args()

    print("Searching SSM for {}".format(args.search_string))

    cache_filename = ssm_cache_filename(args.prefix, args.profile)

    load_from_cache = False

    if not args.no_cache:
        if os.path.exists(cache_filename):
            ssm_cache_seconds_ago = \
                time.time() - os.path.getmtime(cache_filename)
            max_cache_age_seconds = os.environ.get('SSM_SEARCH_MAX_CACHE', 300)
            if ssm_cache_seconds_ago <= max_cache_age_seconds:
                load_from_cache = True
        
    if load_from_cache:
        ssm_params = read_ssm_cache(cache_filename)
    else:
        ssm_params = load_ssm_params(args.prefix, args.profile)
        write_ssm_cache(cache_filename, ssm_params)
        
    search_ssm_params(ssm_params, args.search_string)

if __name__ == '__main__':
    main()
