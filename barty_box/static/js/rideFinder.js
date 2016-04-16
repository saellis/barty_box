var terms = ['Wasted',
    'Trashed',
    'Shit-faced',
    'Plastered',
    'Fucked',
    'Fucked up',
    'Hammered',
    'Destroyed',
    'Messed up',
    'Gone',
    'Faded (Cross-Faded)',
    'Shit-hammered',
    'Shit-housed',
    'Scrone\'d',
    'Drunk',
    'Inebriated',
    'Under the influence',
    'Intoxicated',
    'Irresponsible',
    'Wild',
    'Over the limit',
    'Loaded',
    'Stupid',
    'Rowdy',
    'Turn\'t up (Turn\'t)',
    'Blacked out',
    'Sloshed',
    'Smashed',
    'Slizzard',
    'Lit',
    'Blasted',
    'Obliterated',
    'Schwastyyy',
    'Bombed',
    'Twisted',
    'Weird',
    'Juiced',
    'Belligerent',
    'Impaired',
    'Buzzed',
    'Sozzled',
    'Slozzled',
    'Sauced',
    'Wrecked',
    'Tanked',
    'Shmaacked',
    'Glazed',
    'hammy'
];

$(document).ready(function() {
    if ($( "#go" ).length) {
        var idx = Math.floor(Math.random() * terms.length)
        $("#go").html('Let\'s get ' + terms[idx]+ '!');
    } else {
        window.setInterval(function(){
            updateRideStatus()
        }, 10000);
    }
})

var radius = -1;
var product_choice = 'lyft';

function mile(rad) {
    radius = rad;
    console.log('set radius to ' + radius);
    if(radius !== -1 && product_choice !== 'lyft') {
        $('#message').html('An ' + product_choice + ' will bring you and your friends to a random bar within ' + radius + ' miles of your location.')
    }
}

function product(prod) {
    product_choice = prod;
    console.log('set product_choice to ' + product_choice);
    if(radius !== -1 && product_choice !== 'lyft') {
        $('#message').html('An ' + product_choice + ' will bring you and your friends to a random bar within ' + radius + ' miles of your location.')
    }
}

function request() {
    if(radius == -1) {
        alert('You need to pick a mile radius first!');
    } else if(product_choice === 'lyft') {
        alert('You need to pick an Uber type!');
    } else {
        $('#dialog').html('<h3>Requesting a ride...</h3>')
        getLocationAndCallAFuckingRide();
    }
}

function getLocationAndCallAFuckingRide() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(callRide);
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

function updateRideStatus() {
    url = window.location.href
    if( url.indexOf('ride_id') > -1) {
        var ride_id = url.match(/ride_id=([^&]+)/)[1]
        params = {'ride_id': ride_id}
        requestInfo('get', '/get_ride_update', params, function(data) {
            if(data['status'] === 'processing') {
                var status = 'Nobody has accepted the ride yet. Hang tight!'
            } else {
                var min_eta = parseInt(data['eta']) / 60
                var status = 'Ride accepted!\n' + data['driver'] + ' will arrive in ' + min_eta + ' minutes.'
            }
            $('#output').html(status)
        });
    } else {
        requestInfo('get', '/get_ride_request', {}, function(data) {
            location.href = '/wait?' + 'ride_id=' + data['request_id']
        })
    }

}

function callRide(position) {
    requestInfo('get', '/caller', {
        'latitude': position.coords.latitude,
        'longitude': position.coords.longitude,
        'radius': radius,
        'url': window.location.href,
        'product': product_choice,
    }, function(data) {
        ride_id = data['request_id']
        if (!('surge_url' in data)) {
            params = {
                'ride_id': data['request_id']
            }
            location.href = '/wait' + '?' + $.param(params)
        } else {
            location.href = data['surge_url']
        }
    });
}

function requestInfo(type, url, parameters, success) {
	parametersString = $.param(parameters);
	$.ajax({
        url: url + "?" + parametersString,
        type: type,
        success: function(response) {
            success(response);
		},
        failure: function(data) {
            console.log('error');
        }
    });
}

function failure(data) {
    console.log('Had an error retrieving data');
    console.log(data);
}