const express = require('express');
const mysql2 = require ('mysql2/promise');

const pool = mysql2.createPool ({
	host: 'localhost',
	user: 'root',
	database: 'fp_groups',
	password: '',
});
							
const app = express();

app.get('/groups', function(req, res) {
	pool.query('SELECT * FROM tg_group').then(function(data) {
		const tg_group = data[0];
		res.send(`<!DOCTYPE html>
		<html>
			<head>
				<span>Groups list</span>
			</head>
			<body>
				<ul>
					${tg_group.map(group => `<li> <b>Name:</b> ${group.group_name} , <b>ID:</b> ${group.group_id} , <b>Theme:</b> ${group.
					theme}</li>`).join('')}
				</ul>
			</body>
		</html>`);
	});
});

app.get('/users', function(req, res) {
	pool.query('SELECT * FROM tg_users').then(function(data) {
		const tg_users = data[0];
		res.send(`<!DOCTYPE html>
		<html>
			<head>
				<span>Users list</span>
			</head>
			<body>
				<ul>
					${tg_users.map(user => `<li> <b>Username:</b> ${user.user_name} , <b>User TG ID:</b> ${user.user_tgid} </li>`).join('')}
				</ul>
			</body>
		</html>`);
	});
});

app.get('/messages', function(req, res) {
	pool.query('SELECT * FROM tg_message').then(function(data) {
		const tg_message = data[0];
		res.send(`<!DOCTYPE html>
		<html>
			<head>
				<span>Messages list</span>
			</head>
			<body>
				<ul>
					${tg_message.map(message => `<li> <b>Message theme:</b> ${message.message_theme} , <b>Username:</b> ${message.user_name} , <b>User TG ID:</b> ${message.user_tgid} , <b>Message 'text':</b> ${message.message_text} , <b>Source group:</b> ${message.group_name}</li>`).join('')}
				</ul>
			</body>
		</html>`);
	});
});

app.listen(3000, function() {
	console.log ('server started');
});

/*
pool.query('SELECT * FROM tg_group').then(function(data) {
		const tg_group = data[0];
		res.send(`<!doctype html>
		<html>
			<body>
				<ul>
					${tg_group.map(group => `<li>${group.name}</li>`).join('')}
				</ul>
			</body>
		</html>
		`);
	});
*/