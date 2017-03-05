var QUEUE_URL = 'https://twilio-plays-roomba.herokuapp.com/queue';
var QUEUE_INTERVAL = 5000;

var bumperData;
var cliffData;
var encoderData;
var sensorsData;
var velocityData;
var wheelDropData;

var config = {
	apiKey: "AIzaSyD7Br51b3F296kpbD3PcvRbaz1jYaL_Oi8",
	authDomain: "hacktech2017-2d0d8.firebaseapp.com",
	databaseURL: "https://hacktech2017-2d0d8.firebaseio.com",
	storageBucket: "hacktech2017-2d0d8.appspot.com",
	messagingSenderId: "761159996237"
};

$(document).ready(function() {
	firebase.initializeApp(config);
	var db = firebase.database();

	retrieveQueue();
	setInterval(retrieveQueue, QUEUE_INTERVAL);

	db.ref('bumper/').on('value', function(snapshot) {
		console.log(snapshot.val());
		bumperData = snapshot.val();

		$('#bumper_center_left').html(bumperData.bumper_center_left.toString());
		$('#bumper_center_right').html(bumperData.bumper_center_right.toString());
		$('#bumper_front_left').html(bumperData.bumper_front_left.toString());
		$('#bumper_front_right').html(bumperData.bumper_front_right.toString());
		$('#bumper_left').html(bumperData.bumper_left.toString());
		$('#bumper_right').html(bumperData.bumper_right.toString());
	});

	db.ref('cliff/').on('value', function(snapshot) {
		console.log(snapshot.val());
		cliffData = snapshot.val();

		$('#cliff_front_left').html(cliffData.cliff_front_left.toString());
		$('#cliff_front_right').html(cliffData.cliff_front_right.toString());
		$('#cliff_left').html(cliffData.cliff_left.toString());
		$('#cliff_right').html(cliffData.cliff_right.toString());
	});

	db.ref('encoder/').on('value', function(snapshot) {
		console.log(snapshot.val());
		encoderData = snapshot.val();

		$('#encoder_left').html(encoderData.encoder_left.toString());
		$('#encoder_right').html(encoderData.encoder_right.toString());
	});

	db.ref('sensors/').on('value', function(snapshot) {
		console.log(snapshot.val());
		sensorsData = snapshot.val();

		$('#distance').html(sensorsData.distance.toString());
		$('#angle').html(sensorsData.angle.toString());
	});

	db.ref('velocity/').on('value', function(snapshot) {
		console.log(snapshot.val());
		velocityData = snapshot.val();

		$('#wheel_left_velocity').html(velocityData.wheel_left_velocity.toString());
		$('#wheel_right_velocity').html(velocityData.wheel_right_velocity.toString());
	});

	db.ref('wheel_drop/').on('value', function(snapshot) {
		console.log(snapshot.val());
		wheelDropData = snapshot.val();

		$('#wheel_drop_left').html(wheelDropData.wheel_drop_left.toString());
		$('#wheel_drop_right').html(wheelDropData.wheel_drop_right.toString());
	});
});

function retrieveQueue() {
	console.log('Retrieving queue...');
	$.get(QUEUE_URL, function(data) {
		$('#commands').empty();
		if(data.length == 0) {
			$("#commands").append('<li class="list-group-item">No commands have been submitted</li>');
		} else {
			data.forEach(function(command) {
				$("#commands").append('<li class="list-group-item"><b>' + command + '<b/></li>');
			});
		}
	});
}
