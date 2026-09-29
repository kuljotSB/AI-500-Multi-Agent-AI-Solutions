### HTTP Header Authentication for MCP Servers in APIM

### Lab Overview
In this lab, you will learn how to configure HTTP Header Authentication for MCP (Managed Cloud Platform) servers in Azure API Management (APIM). This involves setting up custom header checks to securely pass authentication information between APIM and your backend MCP services.

### Creating a Header policy in APIM for MCP Server Authentication
Open the `Policies` section of your APIM instance and add the following policy to the `inbound` section of your API:

```xml
<check-header name="Authorization" failed-check-httpcode="401" failed-check-error-message="Not authorized" ignore-case="false">
    <value>kuljot123</value>
</check-header>
```

This policy checks for the presence of an `Authorization` header with the value `kuljot123`. If the header is missing or does not match, a 401 Unauthorized response is returned.

The final policy xml should look like this:
```xml
<!--
    - Policies are applied in the order they appear.
    - Position <base/> inside a section to inherit policies from the outer scope.
    - Comments within policies are not preserved.
-->
<!-- Add policies as children to the <inbound>, <outbound>, <backend>, and <on-error> elements -->
<policies>
	<!-- Throttle, authorize, validate, cache, or transform the requests -->
	<inbound>
		<base />
		<check-header name="Authorization" failed-check-httpcode="401" failed-check-error-message="Not authorized" ignore-case="false">
          <value>kuljot123</value>
        </check-header>
	</inbound>
	<!-- Control if and how the requests are forwarded to services  -->
	<backend>
		<base />
	</backend>
	<!-- Customize the responses -->
	<outbound>
		<base />
	</outbound>
	<!-- Handle exceptions and customize error responses  -->
	<on-error>
		<base />
	</on-error>
</policies>
```

### Testing the Header Authentication
Run the jupyter notebook in the [MCP with AI Agent HTTP Auth](./mcp_with_ai_agent_http_auth/http_auth.ipynb) folder to test the header authentication setup using Azure AI Foundry Agent.

### Summary 
In this lab, you have successfully configured HTTP Header Authentication for MCP servers in Azure API Management. You created a policy to check for a specific authorization header and tested the setup using a Jupyter notebook. This ensures secure communication between APIM and your backend MCP services.
