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
	<div class="sponsor_div">
		<text class="sponsor_title">Sponsored by:</text><br>
		<text class="sponsor">Surprise..</text>
	</div>
	</center>
	<center>
    <form class="upload-email-wrapper" action="upload.php" method="post" enctype="multipart/form-data">
          <input type="file" name="fileToUpload" id="fileToUpload"><p></p>
          <input class="email" type="email" id="email" name="email" placeholder="Email Address">
          <input class="btn" type="submit" value="Submit" name="submit">
    </form>
	</center>
</body>
</html>
