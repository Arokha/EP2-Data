<?php

$files = glob("*.json");

foreach ($files as $file) {
	convert_file($file);
}

function convert_file($filename){
	$file = file_get_contents($filename);
	$json = json_decode($file,TRUE);

	foreach ($json as &$value) {
		$value['resource'] = "Eclipse Phase Second Edition";
		$value['reference'] = "";
		$value['id'] = generate_uuid();
	}

	file_put_contents($filename.'new', json_encode($json,JSON_PRETTY_PRINT));
}

function generate_uuid(){
	$data = $data ?? random_bytes(16);

    $data[6] = chr(ord($data[6]) & 0x0f | 0x40); // set version to 0100
    $data[8] = chr(ord($data[8]) & 0x3f | 0x80); // set bits 6-7 to 10

    return vsprintf('%s%s-%s-%s-%s-%s%s%s', str_split(bin2hex($data), 4));
}

?>