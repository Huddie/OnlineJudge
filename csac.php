<!DOCTYPE html>
<html>
<head>
  <title>Upload your files</title>
<link href="csac.css" rel="stylesheet" type="text/css">
<link href="https://fonts.googleapis.com/css?family=Roboto+Mono:700" rel="stylesheet">
 <body>
	<center>
 		<text class="main_title">CSAC 2019</text>
 		<br>
  		<ul>
	  		<li><a href="news.asp">Rules</a></li>
	  		<li><a href="contact.asp">Prizes</a></li>
		</ul>
	</center>
	<center>
	<div class="upload-email-wrapper">
		 <input class="email" type="email">
	</div>
	<br>
 	<div class="upload-btn-wrapper">
	  	<button class="btn">Upload code</button>
	  	<input type="file" name="fileToUpload" id="fileToUpload" />
	</div>
 	<br>
	<div class="upload-btn-wrapper">
  	<form action="upload.php" method="post" enctype="multipart/form-data">
	  	<button class="btn">Submit</button>
	</form>
	</div>
	</center>
</body>
</html>