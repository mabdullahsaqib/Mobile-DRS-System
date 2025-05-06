import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:permission_handler/permission_handler.dart';

Future<void> requestPermissions() async {
  await Permission.location.request();
  await Permission.camera.request();
  await Permission.microphone.request();
  await Permission.storage.request();
}

Future<Map<String, dynamic>> parseJsonInIsolate(String jsonString) async {
  return await compute(
      (message) => json.decode(message) as Map<String, dynamic>, jsonString);
}

Future<String> encodeJsonInIsolate(Map<String, dynamic> jsonMap) async {
  return await compute((message) => json.encode(message), jsonMap);
}

Future<Uint8List> decodeBase64InIsolate(String base64String) async {
  return await compute((message) => base64.decode(message), base64String);
}

Future<String> encodeBase64InIsolate(Uint8List base64Binary) async {
  return await compute((message) => base64.encode(message), base64Binary);
}
