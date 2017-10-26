[![Build Status](https://travis-ci.org/andriyko/aiociscospark.svg?branch=master)](https://travis-ci.org/andriyko/aiociscospark)

# Python Cisco Spark API client

Python 3.6+ [Cisco Spark](https://developer.ciscospark.com) HTTP API wrapper written with [asyncio](https://docs.python.org/3/library/asyncio.html) and [aiohttp](http://aiohttp.readthedocs.io/en/stable/).

## Installation ##
```
pip install git+git://github.com/andriyko/aiociscospark.git@0.0.1
```

## Features ##
- Built-in pagination support
- Automatic rate-limit handling
- Automatic refresh of an access token
- Optionally can read Spark credentials from your local environment
- Allows to register custom response handlers

## Usage and examples ##

`aiociscospark.APIClient` delegates:

- HTTP communication to `aiociscospark.HTTPClient`
- REST API stuff (building URLs, parameters, handling of responses, pagination etc) to `aiociscospark.ApiService`.

`aiociscospark.APIClient` owns a set of REST API services that are used to communicate with corresponding API resources:

```python
import aiociscospark
client = aiociscospark.get_client({'access_token': '<token>'})
In [5]: for attr, svc in client.__dict__.items():
   ...:     if isinstance(svc, aiociscospark.services.BaseApiService):
   ...:         print(f'{svc.__class__.__name__:30} {svc.get_resource_url()}')
   ...:
   ...:
   ...:
ApiServiceContents             https://api.ciscospark.com/v1/contents
ApiServiceLicenses             https://api.ciscospark.com/v1/licenses
ApiServiceMessages             https://api.ciscospark.com/v1/messages
ApiServiceOrganizations        https://api.ciscospark.com/v1/organizations
ApiServicePeople               https://api.ciscospark.com/v1/people
ApiServiceRoles                https://api.ciscospark.com/v1/roles
ApiServiceRoomMemberships      https://api.ciscospark.com/v1/memberships
ApiServiceRooms                https://api.ciscospark.com/v1/rooms
ApiServiceTeamMemberships      https://api.ciscospark.com/v1/team/memberships
ApiServiceTeams                https://api.ciscospark.com/v1/teams
ApiServiceWebhooks             https://api.ciscospark.com/v1/webhooks
```

For example, to get current user:

```python
import asyncio
event_loop = asyncio.get_event_loop()
me = event_loop.run_until_complete(client.people.me())
print(me['displayName'])
```

To perform request without wrappers and get `aiohttp.ClientResponse` object:

```python
url = client.people.get_resource_url('me') # no outbound HTTP request, just build URL
resp = event_loop.run_until_complete(client.http_client.get(url))
resp.__class__ #  aiohttp.client_reqrep.ClientResponse
```

`aiociscospark.APIClient` expects credentials to be passed as a dictionary with at least `access_token` key. Other keys are optional: `client_id`, `client_secret`, `refresh_token`. Use `aiociscospark.Credentials` to read Spark credentials from your local environment.
It expects the following environment variables to be set: `CISCO_SPARK_ACCESS_TOKEN` (required), `CISCO_SPARK_REFRESH_TOKEN`, `CISCO_SPARK_CLIENT_ID`, `CISCO_SPARK_CLIENT_SECRET` (required only if you want to automatically refresh access token).

To register response handler:
```python
async def handle_unauthorized_response(resp):
    # do what you need
    pass

client.http_client.register_response_handler(401, handle_unauthorized_response)
```


## Running the tests ##

```bash
git clone git@github.com:andriyko/aiociscospark.git
cd aiociscospark
virtualenv -p python3 .venv
source .venv/bin/activate
pip install -r dev-requirements.txt
make test
```

## Contributing
First off, thanks for taking the time to contribute! :+1:
When contributing to this repository, please first discuss the change you wish to make via issue,
email, Spark (contact `andriyko`, you can find me in [#spark4dev](https://web.ciscospark.com/rooms/d2fde090-9d0c-11e5-aeed-2176fdcd8a58/chat) space), or any other method with the owners of this repository before making a change.

Please read [CONTRIBUTING.md](https://github.com/andriyko/aiociscospark/blob/master/.github/CONTRIBUTING.md) for the process for submitting pull requests.

## Authors

* [andriyko](https://github.com/andriyko)

See also the list of [contributors](CONTRIBUTORS.md) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
