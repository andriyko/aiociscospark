import asyncio

import aiociscospark


async def run(loop):
    credentials = aiociscospark.Credentials()
    client = aiociscospark.get_client(credentials, loop=loop)
    me = await client.people.me()
    print('Me: ', me['displayName'])
    org_details = await client.organizations.get_organization(me['orgId'])
    print('Org: ', org_details['displayName'])
    roles = [
        (await client.roles.get_role(role_id))['name'] for role_id in me['roles']
    ]
    print('Roles: ', roles)
    licenses = [
        (await client.licenses.get_license(license_id))['name'] for license_id in me['licenses']
    ]
    print('Licenses: ', licenses)

    pc = 0
    async for person, _ in client.people.list_people(limit=100):
        pc += 1
        print(f'#{pc} Person: id="{person["id"]}"')

    await client.http_client.close_session()


event_loop = asyncio.get_event_loop()

try:
    print('starting coroutine')
    event_loop.run_until_complete(run(event_loop))
finally:
    print('closing event loop')
    event_loop.close()
