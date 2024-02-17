import asyncio
from graphql_client import Client
from graphql_client.exceptions import GraphQLClientGraphQLError, GraphQLClientGraphQLMultiError

async def main():
    # This is a legitimate but expired token
    headers = {"Authorization": "eyJhbGciOiJSUzI1NiIsImlzcyI6Imh0dHBzOi8vYXBpLmVvbm5leHQta3Jha2VuLmVuZXJneS92MS9ncmFwaHFsLyIsImprdSI6Imh0dHBzOi8vYXV0aC5lb25uZXh0LWtyYWtlbi5lbmVyZ3kvLndlbGwta25vd24vandrcy5qc29uIiwia2lkIjoiVzEwejZYZDFESDlTSUlndTZnUjhWN2RBM2h6ajk4S0FFU3VZYlZHSnpEQSIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJrcmFrZW58YWNjb3VudC11c2VyOjExMTMzNDEwIiwiZ3R5IjoiRU1BSUwtQU5ELVBBU1NXT1JEIiwiZW1haWwiOiJhd2Vuc2F1bmRlcnNAZ21haWwuY29tIiwidG9rZW5Vc2UiOiJhY2Nlc3MiLCJpc3MiOiJodHRwczovL2FwaS5lb25uZXh0LWtyYWtlbi5lbmVyZ3kvdjEvZ3JhcGhxbC8iLCJpYXQiOjE3MDgxMTk0MTAsImV4cCI6MTcwODEyMzAxMCwib3JpZ0lhdCI6MTcwODExOTQxMH0.JM5fd-IqmJI28RH1st5XOji9IYhxSx6S5jdr31SnuxN9MiqNlxWH8N_vXRmmofIDBnS0zV9s3qI21sBQMjApQTye-HtBdDRGZzwd-eq5WZ1HrvveCwTF7wdjXF5-ycOk60uewkWl0wfaN9qdQF-D5he00ResT8MsQU1nocWruV4oW7Gvm0FqJ35ifcmZzbOn_StTJOIZWehB_hjOMSiuAtOH-vmm5dMmJUluAWQRki0HyZqI3jcGWCwAV-IDO8Yy8w-vnNIp94pWlVAz2vO9HZ7dXfampafegUmRK0hb7qAviqkefMLv-Ncgia6BvLoSPrbmlPS4HXxMTqdzaxt7Eg"}
    c = Client("https://api.eonnext-kraken.energy/v1/graphql/", headers=headers)
    try:
        res = await c.get_account_info()
    except GraphQLClientGraphQLMultiError as e:
        # Unfortunately graphql errors don't give nice status codes, so we will just assume its auth related.
        print(e)
    print(res)


if __name__ == "__main__":
    asyncio.run(main())