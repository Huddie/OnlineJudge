<?php
    $arr = array();
    $message = '';
    $target_dir = "uploads/";
    $target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
    $target_file = dirname(__DIR__).'/'.$target_file;
    $uploadOk = 1;
    $codeFileType = strtolower(pathinfo($target_file, PATHINFO_EXTENSION));
    $cmd = 'python3 judge.py --filepath='.$target_file.' --email='.$_POST["email"].' --problem_code='.$_POST["problem_code"];
    echo $cmd;
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
    if($codeFileType != "cpp" && $codeFileType != "java" && $codeFileType != "py"
       && $codeFileType != "c" ) {
        echo "Sorry, only C, Cpp, Java or Python files are allowed.";
        $uploadOk = 0;
    }
        // Check if $uploadOk is set to 0 by an error
    if ($uploadOk == 0) {
        echo "Sorry, your file was not uploaded.";
            // if everything is ok, try to upload file
    } else {
        echo $_FILES["fileToUpload"]["tmp_name"];
        echo $target_file;
        if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file)) {
            echo "The file ". basename( $_FILES["fileToUpload"]["name"]). " has been uploaded.";
            $message = exec($cmd, $arr);
            echo $message;
            for ($x = 0; $x < count($arr); $x++) {
                echo $arr[$x];
            }
        } else {
            echo "Sorry, there was an error uploading your file.";
        }
    }
?>

