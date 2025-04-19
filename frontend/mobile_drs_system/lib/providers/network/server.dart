import 'dart:convert';
import 'dart:io';
import 'dart:nativewrappers/_internal/vm/lib/typed_data_patch.dart';

import 'package:flutter/material.dart';
import 'package:mobile_drs_system/models/status.dart';
import 'package:network_info_plus/network_info_plus.dart';
import 'package:permission_handler/permission_handler.dart';

Future<void> requestPermissions() async {
  await Permission.location.request();
}

class ServerProvider with ChangeNotifier {
  bool _isRunning = false;

  bool get isRunning => _isRunning;
  ServerSocket? _serverSocket;

  Map<String, dynamic>? _receivedData;
  Map<String, dynamic> get receivedData => _receivedData == null
      ? {}
      : _receivedData!; // Return an empty map if _receivedData is null
//Give IP Address of the server
  var _ipAddress = "";
  String get ipAddress => _ipAddress;
  Socket? _connectedClient;

  Future<void> startServer() async {
    if (_isRunning) {
      // print('Server is already running');
      return;
    }
    //print('Starting server...');
    requestPermissions();
    final info = NetworkInfo();
    _ipAddress = await info.getWifiIP() ?? "";
    _serverSocket = await ServerSocket.bind('0.0.0.0', 4040);
    // print('Server listening on port ${_serverSocket?.port}');

    _serverSocket?.listen((client) {
      _connectedClient = client;
      client.listen((data) {
        String dataString = String.fromCharCodes(data);
        _receivedData = json.decode(dataString);
        notifyListeners();
        // print('Received data: ${String.fromCharCodes(data)}');
      }, onError: (error) {
        // Handle error
        //print('Error: $error');
      }, onDone: () {
        _connectedClient?.close();
        _connectedClient = null;
      });
    });
    _isRunning = true;
    notifyListeners();
  }

  Future<void> stopServer() async {
    if (!_isRunning) {
      //print('Server is not running');
      return;
    }
    await _serverSocket?.close();
    _isRunning = false;
    _connectedClient?.close();
    _connectedClient = null;
    notifyListeners();
  }

  void sendJSON(Map<String, dynamic> message) {
    if (_serverSocket != null) {
      _connectedClient?.write(json.encode(message));
    }
  }

  void sendMessage(String message) {
    Map<String, dynamic> data = {
      'status': Status.SendString,
      'message': message,
    };
    sendJSON(data);
  }
}
