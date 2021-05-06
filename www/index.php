<?php

if (!empty($_POST["username"])){
    echo "<h1>hello " . $_POST["username"] . "</h1>";
}

echo '
<form method="post" action="">
<label>enter your username and click on submit button:</label>
<input type="text" name="username" value="'.$_POST["username"].'">
<button>submit</button>
</form>';
