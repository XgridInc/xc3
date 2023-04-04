# Dynamic Text Panel in Grafana

The Grafana plugin called Dynamic Text visualization panels turns plain text and table data into colourful, readable information cards. Variables, Markdown, and Handlebars are supported by the panel.

You can define a text template using the information from your data source query in the Dynamic Text visualization panel.

## Content Panel

The content panel accepts any HTML code, Markdowns and Handlebars. This panel interprets the content and makes a frontend on the Grafana panel. The content is based on a render template in which we can select for all rows or render for every individual row from the data source.

**![](https://user-images.githubusercontent.com/105271892/222363293-857e4d4c-9e26-4af7-8e2f-fa664ca418c7.png)**

## Helpers Panel

The helpers panel accepts any JavaScript code and allows us to add handlebars and event based helpers. So, we can add our event for hitting the API for changing the state of the resource.

**![](https://user-images.githubusercontent.com/105271892/222363387-4ebfa290-6fcf-4ba5-9d23-6f2e341fb12f.png)**

# Output

The following image shows the output from the content and helper panel.

**![](https://lh3.googleusercontent.com/5GB4ayd4dxU7cO4Y6keMJL_Wimt-yDMHdXZnbEXQL9bE61K9HpnaJf5osPGb9L25XW3H6bzmoTI4wGW35It-MRJfIywYfHMp-y5dP8EqtJzbn42cHVLoGWP90tIVHgLmRpGSEq_gCx8mDl-KYv0PR0kcFg=s2048)**

## Explanation

### Content Panel Code

    <div id="table_data">
        {{#each data}}
    	    <table>
    		    <tr>
    			    <td  class="resourceid">{{iam_role_service_resource_id}}</td>
    			    <td>{{iam_role_service_cost}}</td>
    			    <td  class="status"><button  class="editbtn"  id="checking"  type="submit" >{{iam_role_service_state}}</button></td>
    		    </tr>
    	    </table>
        {{/each}}
    </div>

In this code we are making a table for displaying the **ResourceID**, **Cost of resource**, **Start/Stop** button to perform the action.

### Helpers Panel Code

```
$require("dotenv").config();

("#table_data").on('click', '.editbtn', function (e) {
    e.preventDefault();
    var currentRow = $(this).closest("tr");
    var $resource_id = currentRow.find(".resourceid").text();
    var $status = currentRow.find(".status").text();
    alert("Clicked!")
    var res_id = $resource_id,
        status = $status;
    var resource_id = res_id.split("/")[1];
    alert(resource_id);
    $.ajax({
        type: "POST",
        url: process.env.API_ENDPOINT,
        contentType: 'application/json',
        data: JSON.stringify({
            'resource_id': resource_id,
            'status': status
        }),
        success: function (res) {
            alert("Success");
        },
        error: function () {
            alert("Something went wrong!!")
        }
    })
        .done(function (res) {
            console.log(res)
        });
})
```

In this code we are getting the `resourceid` and `status` from the frontend and passing it to the API using `POST` method and executing the lambda function which **starts/stops** the instance.

### Passing the API Endpoint

For passing the API Endpoint we use **.env** file and use the `API_ENDPOINT` variable to get our endpoint.

## License

Copyright (c) 2023, Xgrid Inc, https://xgrid.co

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
