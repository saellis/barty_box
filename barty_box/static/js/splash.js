$(document).ready(function() {
    getData('/auth_url', 'get')
})

function getData(url, type) {
    $.ajax({
        url: url,
        type: type,
        success: function(data) {
           $('#button_spot').html('<a type="button" class="btn btn-lg btn-default" href="' + data['auth_url'] + '"><span class="glyphicon glyphicon-flash"></span>Log in with Uber</a>')
        },
        failure: function(data) {
            failure(data);
        }
    });
}

function failure(data) {
    console.log('Had an error retrieving data');
    console.log(data);
}