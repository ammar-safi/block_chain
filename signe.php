<?php

header("Content-Type: application/json");   

// إعدادات
$filePath = 'C:\\Users\\HP\\Desktop\\Screenshot(341).png'; // اسم الملف الذي تريد توقيعه
$privateKeyPath = 'private_key.pem'; // مسار المفتاح الخاص
$publicKeyPath = 'public_key.pem';   // مسار المفتاح العام
$blockIndex = 1; // رقم الكتلة التي تريد التوقيع عليها
$signerId = 'user123'; // معرف الموقّع
$flaskUrl = 'http://localhost:5000/sign_block';

// 1. قراءة الملف وحساب hash
$fileHash = hash_file('sha256', $filePath);

// 2. بناء سلسلة البيانات بنفس ترتيب البلوكشين
// يجب أن تحصل على بيانات الكتلة من Flask أولاً (GET /block/<index>)
$blockData = file_get_contents("http://localhost:5000/block/$blockIndex");
$block = json_decode($blockData, true)['data']['block'];
$timestamp = number_format($block['timestamp'], 7, '.', ''); // 6 أرقام عشرية
$blockString = $block['index'] . $block['previous_hash'] . $block['file_hash'] . $block['user_id'] . $timestamp;


// 3. تحميل المفتاح الخاص
$privateKey = openssl_pkey_get_private(file_get_contents($privateKeyPath));

// 4. توقيع سلسلة البيانات
openssl_sign($blockString, $signature, $privateKey, OPENSSL_ALGO_SHA256);
$signatureBase64 = base64_encode($signature);

// 5. تحميل المفتاح العام
$publicKey = file_get_contents($publicKeyPath);

// 6. تجهيز البيانات للإرسال
$postData = [
    'block_index' => $blockIndex,
    'signer_id'   => $signerId,
    'signature'   => $signatureBase64,
    'public_key'  => $publicKey
];
echo(json_encode($postData));
exit;

// 7. إرسال الطلب إلى Flask
$ch = curl_init($flaskUrl);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($postData));
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($ch);
curl_close($ch);
echo "Response from Flask:\n";
echo $response;