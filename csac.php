<!DOCTYPE html>
<html>
<head>
  <title>Upload your files</title>
<link href="csac.css" rel="stylesheet" type="text/css">
<script type="text/javascript" src="script.js"></script>
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
 	<div class="upload-btn-wrapper">
	  <button class="btn">Upload code</button>
	  <input type="file" name="myfile" />
	</div>
	</center>
<!--
  	<form enctype="multipart/form-data" action="upload.php" method="POST">
    	<input type="file" name="uploaded_file"></input><br/>
    	<input type="submit" value="Upload"></input>
  	</form>
-->
</body>
</html>


<?PHP
  if(!empty($_FILES['uploaded_file']))
  {
    $path = "uploads/";
    $path = $path . basename( $_FILES['uploaded_file']['name']);
    if(move_uploaded_file($_FILES['uploaded_file']['tmp_name'], $path)) {
      echo "The file ".  basename( $_FILES['uploaded_file']['name']). 
      " has been uploaded";
    } else{
        echo "There was an error uploading the file, please try again!";
    }
  }
?>