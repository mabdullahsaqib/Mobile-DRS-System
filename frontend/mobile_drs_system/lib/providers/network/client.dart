import 'dart:convert';
import 'dart:io';

import 'package:flutter/widgets.dart';
import 'package:mobile_drs_system/models/status.dart';

class ClientProvider with ChangeNotifier {
  bool _isConnected = false;
  Map<String, dynamic>? _receivedData;
  Map<String, dynamic> get receivedData =>
      _receivedData == null ? {} : _receivedData!;
  bool get isConnected => _isConnected;

  Socket? _socket;
  Future<void> connect(String IP) async {
    if (_isConnected) {
      //print('Already connected to server');
      return;
    }

    //IF IP address isnt valid, throw an error
    if (InternetAddress.tryParse(IP) == null) {
      //print('Invalid IP address');
      throw Exception('Invalid IP address');
    }

    try {
      //Connect to the server using SecureSocket
      //print('Connecting to server...');
      _socket =
          await Socket.connect(IP, 4040, timeout: const Duration(seconds: 5));
      //print('Connected to server');
    } catch (e) {
      //print('Connection failed: $e');
      throw Exception('Connection failed: $e');
    }
    // Listen for incoming messages
    _socket?.listen((data) {
      String message = String.fromCharCodes(data);
      _receivedData = json.decode(message);
      notifyListeners();
    }, onDone: () {
      // Handle disconnection
      _isConnected = false;
      notifyListeners();
    });
    // Set the connection status to true
    _isConnected = true;
    notifyListeners();
  }

  Future<void> disconnect() async {
    if (_socket == null) return;
    await _socket?.close();
    _socket = null;
    _isConnected = false;
    notifyListeners();
  }

  void sendJSON(Map<String, dynamic> message) {
    if (_socket == null) return;
    // Convert the message to bytes and send it
    String jsonString = json.encode(message);
    _socket?.write(jsonString);
    notifyListeners();
  }

  void sendMessage(String message) {
    Map<String, dynamic> jsonMessage = {
      'status': Status.sendString,
      'message': message,
    };
    sendJSON(jsonMessage);
  }
}
