require("dotenv").config();

("#table_data").on('click', '.editbtn', function (e) {
    e.preventDefault();
    var currentRow = $(this).closest("tr");
    var $resource_id = currentRow.find(".resourceid").text();
    var $status = currentRow.find(".status").text();
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
