This project exists to access the kraken api to gather information about a customer's energy usage.

The api is in two parts, one graphql, and one rest. They don't overlap perfectly, so we need to use both. We use the adriane-codegen project to generate the graphql client. Sadly the openapi spec is not complete, so we have to manually write the rest client.