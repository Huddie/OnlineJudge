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


<?php
$target_dir = "../uploads/";
$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
$uploadOk = 1;
$codeFileType = strtolower(pathinfo($target_file, PATHINFO_EXTENSION));

// Check if file already exists
if (file_exists($target_file)) {
    echo "Sorry, file already exists.";
    $uploadOk = 0;
}
// Check file size
if ($_FILES["fileToUpload"]["size"] > 500000) {
    echo "Sorry, your file is too large.";
    $uploadOk = 0;
}
// Allow certain file formats
if($imageFileType != "cpp" && $imageFileType != "java" && $imageFileType != "py"
&& $imageFileType != "c" ) {
    echo "Sorry, only JPG, JPEG, PNG & GIF files are allowed.";
    $uploadOk = 0;
}
// Check if $uploadOk is set to 0 by an error
if ($uploadOk == 0) {
    echo "Sorry, your file was not uploaded.";
// if everything is ok, try to upload file
} else {
    if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file)) {
        echo "The file ". basename( $_FILES["fileToUpload"]["name"]). " has been uploaded.";
    } else {
        echo "Sorry, there was an error uploading your file.";
    }
}
?>
