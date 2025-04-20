import 'dart:io';

import 'package:flutter/material.dart';
import 'package:mobile_drs_system/models/command_type.dart';
import 'package:mobile_drs_system/utils/utils.dart';
import 'package:network_info_plus/network_info_plus.dart';

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
    final info = NetworkInfo();
    _ipAddress = await info.getWifiIP() ?? "";
    _serverSocket = await ServerSocket.bind('0.0.0.0', 4040);
    // print('Server listening on port ${_serverSocket?.port}');

    _serverSocket?.listen((client) {
      if (_connectedClient != null) {
        client.close(); // Close the new client if another is already connected
        return;
      }
      _connectedClient = client;
      print('Client connected: ${client.remoteAddress.address}');
      final buffer = StringBuffer();
      client.listen((data) async {
        String message = String.fromCharCodes(data);
        buffer.write(message);

        try {
          // Try to parse the buffer content
          _receivedData = await parseJsonInIsolate(buffer.toString());
          // If successful, clear the buffer
          buffer.clear();
          debugPrint('Received data: $_receivedData');
          notifyListeners();
        } catch (e) {
          // If parsing fails, we have incomplete data - wait for more
          debugPrint('Received partial data, waiting for more...');
        }
      }, onError: (error) {
        // Handle error
        debugPrint('Error: $error');
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

  void sendJSON(Map<String, dynamic> message, {Function? callback}) {
    if (_serverSocket != null) {
      encodeJsonInIsolate(message).then((jsonString) {
        _connectedClient?.write(jsonString);
        if (callback != null) {
          callback();
        }
      });
    }
  }

  void sendMessage(String message) {
    Map<String, dynamic> data = {
      'type': CommandType.sendString.name,
      'message': message,
    };
    sendJSON(data);
  }

  void clearReceivedData() {
    _receivedData = null;
    notifyListeners();
  }
}
