import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:mobile_drs_system/models/command_type.dart';
import 'package:mobile_drs_system/utils/utils.dart';

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
      print('Connecting to server...');
      _socket =
          await Socket.connect(IP, 4040, timeout: const Duration(seconds: 5));
      _socket?.setOption(SocketOption.tcpNoDelay, true);
      print('Connected to server');
    } catch (e) {
      print('Connection failed: $e');
      throw Exception('Connection failed: $e');
    }
    // Listen for incoming messages
    final _buffer = StringBuffer();

    _socket?.listen((data) async {
      String message = String.fromCharCodes(data);
      _buffer.write(message);

      try {
        // Try to parse the buffer content

        _receivedData = await parseJsonInIsolate(_buffer.toString());
        // If successful, clear the buffer
        _buffer.clear();
        print('Received data: $_receivedData');
        notifyListeners();
      } catch (e) {
        // If parsing fails, we have incomplete data - wait for more
        debugPrint('Received partial data, waiting for more...');
      }
    }, onDone: () {
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

  Future<void> sendJSON(Map<String, dynamic> message,
      {Function? callback}) async {
    if (_socket == null) return;
    // Convert the message to bytes and send it
    encodeJsonInIsolate(message).then((jsonString) {
      debugPrint('Sending data: $jsonString');
      _socket?.write(jsonString);
      if (callback != null) {
        callback();
      }
      return;
    });
  }

  void sendMessage(String message) {
    Map<String, dynamic> jsonMessage = {
      'type': CommandType.sendString.name,
      'message': message,
    };
    sendJSON(jsonMessage);
  }

  void clearReceivedData() {
    _receivedData = null;
    notifyListeners();
  }
}
