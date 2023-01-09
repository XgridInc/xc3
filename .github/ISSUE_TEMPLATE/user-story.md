---
name: Custom User Story Template
about: Sample Template for creating GitHub User Stories
title: GitHub User Story Template
labels: ""
assignees: ""
---

**User stories**

#1 As a _persona_, I want to <_what do you want to do_> so that <_why do you want to do it_>

_Example:_ As an XCBG Cloud Engineer, I want to set up a python flask API server on AWS, so that I can build API endpoints for a web application.

_Add more as required_

**Acceptance Criteria**

What must be achieved to consider this story complete?
Example: The API server should be up and running, all required code must be reviewed, approved, and merged, and manual and/or automated testing done.

- [ ] Which open-source libraries are you using to implement this user story? (Answer cannot be empty or N/A)

- [ ] Functional requirements

<!--
Here's an example of a functional requirement section

Use OpenAPISpec to define the API.
The Flask API server should be dockerized and launched in an EC2 instance. There should be a stubAPI endpoint implemented on the server as defined by the OpenAPISpec. The API server should not be publicly exposed.
There should be a way to trigger the stubAPI endpoint internally (maybe a small test script)to test the API server.
All API calls to the API server should be logged locally.
-->

- [ ] Inputs

<!--
The input format should be like

inputParameters:
  - <stubAPIParameter1> Example = stubSampleParam="caller_id"
  - <stubAPIParameterN>
-->

- [ ] Outputs
<!-- 
The input format should be like

output response:

- <stubAPIOutPutResponse1> Example = stubSampleResponse="HTTP 200 OK"
- <stubAPIOutPutResponseN> Example = stubSampleResponse="HTTP 403 Forbidden"
  -->

- [ ] Testing

<!--
Must have unit tests for the API endpoints
Must have negative unit tests for the API endpoints
Must have an integration test (as applicable)
-->

- [ ] Metrics
<!--
Must have read metrics (counters for incoming read requests, successes, errors, etc)
Must have write metrics (counters for incoming write requests, successes, errors, etc)
Must have integration with cloud watch and or other metrics and alerting solutions e-g Prometheus
-->

- [ ] Documentation
<!--
OpenAPISpec doc for the API endpoints. OpenAPISpec (fka Swagger): https://swagger.io/specification/
Example Spec = https://swagger.io/docs/specification/adding-examples/
-->
