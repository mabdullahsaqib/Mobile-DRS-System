import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/widgets.dart';

class ClientProvider with ChangeNotifier {
  bool _isConnected = false;
  Uint8List? _receivedData;
  Uint8List? get receivedData => _receivedData;
  bool get isConnected => _isConnected;

  SecureSocket? _socket;
  Future<void> connect(String IP) async {
    if (_isConnected) {
      print('Already connected to server');
      return;
    }

    //IF IP address isnt valid, throw an error
    if (InternetAddress.tryParse(IP) == null) {
      print('Invalid IP address');
      throw Exception('Invalid IP address');
    }

    try {
      //Connect to the server using SecureSocket
      print('Connecting to server...');
      _socket = await SecureSocket.connect(IP, 4040,
          timeout: const Duration(seconds: 5));
      print('Connected to server');
    } catch (e) {
      print('Connection failed: $e');
      throw Exception('Connection failed: $e');
    }
    // Listen for incoming messages
    _socket?.listen((data) {
      _receivedData = data;
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

  void sendMessage(String message) {
    if (_socket == null) return;
    // Convert the message to bytes and send it
    final data = Uint8List.fromList(message.codeUnits);
    _socket?.write(data);
    print('Sent: $message');
    notifyListeners();
  }
}
