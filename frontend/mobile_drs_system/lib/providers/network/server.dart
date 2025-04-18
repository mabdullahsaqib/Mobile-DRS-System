import 'dart:io';

import 'package:flutter/material.dart';
import 'package:network_info_plus/network_info_plus.dart';
import 'package:permission_handler/permission_handler.dart';

Future<void> requestPermissions() async {
  await Permission.location.request();
}

class ServerProvider with ChangeNotifier {
  bool _isRunning = false;

  bool get isRunning => _isRunning;
  SecureServerSocket? _serverSocket;

//Give IP Address of the server
  var _ipAddress = "";
  String get ipAddress => _ipAddress;
  final List<SecureSocket> _connectedClients = [];

  Future<void> startServer() async {
    if (_isRunning) {
      print('Server is already running');
      return;
    }
    print('Starting server...');
    requestPermissions();
    final info = NetworkInfo();
    _ipAddress = await info.getWifiIP() ?? "";
    _serverSocket = await SecureServerSocket.bind(
        '0.0.0.0', 4040, SecurityContext.defaultContext);
    print('Server listening on port ${_serverSocket?.port}');

    _serverSocket?.listen((client) {
      _connectedClients.add(client);
      client.listen((data) {
        final message = String.fromCharCodes(data);
        print('Received: $message');
      }, onDone: () {
        _connectedClients.remove(client);
      });
    });
    _isRunning = true;
    notifyListeners();
  }

  Future<void> stopServer() async {
    if (!_isRunning) {
      print('Server is not running');
      return;
    }
    await _serverSocket?.close();
    _isRunning = false;
    _connectedClients.clear();
    notifyListeners();
  }

  void sendMessage(String message) {
    if (_serverSocket != null) {
      for (var client in _connectedClients) {
        client.write(message);
      }
    }
  }
}
