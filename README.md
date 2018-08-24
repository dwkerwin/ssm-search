# SSM-Search

Because Amazon made it difficult to search for SSM parameters by name in the AWS console, I created this small tool.

## Motivation Elaborated On

Let's say you have a SSM parameter name like the following:

/dev/another-prefix/my-really-long-service-name/MYSQL_CONNECTION_STRING

But when you go to search for it you can only remember "long-service", in the AWS Console you can only search by names that BEGIN with a string, so you would have to remember nearly the whole string to search that way!

## Installation

```shell
$ pip install ssm-search
```

## Usage

```shell
$ ssm-search -s long-service
SSM Search version 0.1.1
Searching SSM for ['long-service']
/dev/another-prefix/my-really-long-service-name/MYSQL_CONNECTION_STRING -> (SecureString)
/dev/another-prefix/my-really-long-service-name/LOG_LEVEL -> Warning
Found 2 matches out of 513 parameters from SSM

# search on both "long-service" and "connection", by the way it's case insensitive
$ ssm-search -s long-service -s connection
SSM Search version 0.1.2
Searching SSM for ['long-service', 'connection' ]
/dev/another-prefix/my-really-long-service-name/MYSQL_CONNECTION_STRING -> (SecureString)
Found 1 matches out of 513 parameters from SSM
```

If you need to specify an AWS profile to use, just add `--profile dev` (etc).

Results are cached to local disk for a short period to make subsequent requests faster.  By default this is 5 minutes but can be changed by setting an environment variable SSM_SEARCH_MAX_CACHE.  To force it to load without cache, add the `--no-cache` argument.

## Publishing Updates to PyPi

For the maintainer - to publish an updated version of ssm-search, increment the version number in version.py and run the following:

```shell
docker build -f ./Dockerfile.buildenv -t ssm-search:build .
docker run --rm -it --entrypoint make ssm-search:build publish
```

At the prompts, enter the username and password to the pypi.org repo.

## License

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
