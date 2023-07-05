<?php include('server.php') ?>
<!DOCTYPE html>
<html>
<head>
  <title>SHODH - A Platform for missing Person</title>
  <link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>
		
  <h5>SHODH - A Platform for missing Person</h5>	
  <div class="header">
  	<h2>Login</h2>
  </div>
	 
  <form method="post" action="login.php"  class="f1">
  	<?php include('errors.php'); ?>
  	<div class="input-group">
  		<label>Username</label>
  		<input type="text" name="username" >
  	</div>
  	<div class="input-group">
  		<label>Password</label>
  		<input type="password" name="password">
  	</div>
  	<div class="input-group">
  		<button type="submit" class="btn" name="login_user">Login</button>
  	</div>
  	<p>
  		Not a User? <a href="login_admin.php">Login as Admin</a>
  	</p>
  </form>
</body>
</html>