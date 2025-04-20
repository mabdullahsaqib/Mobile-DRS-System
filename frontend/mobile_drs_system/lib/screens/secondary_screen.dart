import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:mobile_drs_system/controllers/connection.dart';
import 'package:mobile_drs_system/main.dart';
import 'package:mobile_drs_system/models/command_type.dart';
import 'package:mobile_drs_system/providers/camera.dart';
import 'package:mobile_drs_system/providers/network/client.dart';
import 'package:mobile_drs_system/utils/utils.dart';
import 'package:provider/provider.dart';

class SecondaryScreen extends StatefulWidget {
  const SecondaryScreen({super.key});

  @override
  SecondaryScreenState createState() => SecondaryScreenState();
}

class SecondaryScreenState extends State<SecondaryScreen> {
  String recievedMsg = "(waiting for data...)";
  String ipAddress = "";
  Map<String, dynamic>? receivedData;
  final _controller = TextEditingController();

  late ClientProvider _clientProvider; // For methods/dispose
  late CameraService _cameraService; // For methods/dispose

  void updateReceivedData(Map<String, dynamic> data) {
    setState(() {
      receivedData = data;
      switch (commandFromString(data["type"])) {
        case CommandType.startRecording:
          recievedMsg = "Recording started";
          clientStartRecording();
          break;
        case CommandType.stopRecording:
          recievedMsg = "Recording stopped";
          clientStopRecording();
          break;
        case CommandType.sendString:
          recievedMsg = "String received: ${data["data"]}";
          break;
        default:
          recievedMsg = "Unknown command";
      }
    });
  }

  void clientStartRecording() {
    if (!_clientProvider.isConnected) return;
    final cameraService = context.read<CameraService>();
    cameraService.initialize().then(
      (_) {
        if (cameraService.isRecording) return;
        cameraService.startRecording(10).then((path) {
          //send recording to server
          sendRecordingToServer(path);
        }).catchError((error) {
          scaffoldMessengerKey.currentState?.showSnackBar(
            SnackBar(content: Text("Error during recording: $error")),
          );
        });
      },
    );
  }

  void clientStopRecording() {
    if (!_cameraService.isRecording) return;
    //Once we stop camera service recording our startRecording method can send video to server
    _cameraService.stopRecording().catchError((error) {
      scaffoldMessengerKey.currentState?.showSnackBar(
        SnackBar(content: Text("Error: $error")),
      );
      return error;
    });
  }

  void sendRecordingToServer(String filePath) async {
    //Encode file as base64 string and send it and the filename
    if (!_clientProvider.isConnected) return;
    final file = File(filePath);
    if (!await file.exists()) {
      print("File does not exist: $filePath");
      scaffoldMessengerKey.currentState?.showSnackBar(
        SnackBar(content: Text("File does not exist :$filePath")),
      );
      return;
    }
    Uint8List bytes = await file.readAsBytes();
    debugPrint("Encoding String");
    final String base64String = await encodeBase64InIsolate(bytes);
    final filename = file.path.split("/").last;
    final data = {
      "type": CommandType.sendRecording.name,
      "data": await encodeJsonInIsolate({
        "videoBase64": base64String,
        "filename": filename,
      }),
    };
    try {
      _clientProvider.sendJSON(data, callback: () {
        scaffoldMessengerKey.currentState?.showSnackBar(
          const SnackBar(content: Text("Recording sent to server")),
        );
      });
    } catch (error) {
      scaffoldMessengerKey.currentState?.showSnackBar(
        SnackBar(content: Text("Error sending recording: $error")),
      );
    }
  }

  @override
  void initState() {
    super.initState();
    _clientProvider = Provider.of<ClientProvider>(context, listen: false);
    _cameraService = Provider.of<CameraService>(context, listen: false);
    _cameraService.initialize();
  }

  @override
  void dispose() {
    _controller.dispose();
    if (_clientProvider.isConnected) {
      _clientProvider.disconnect();
    }
    _cameraService.delete();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final connectionController = context.watch<ConnectionController>();
    final data = context.watch<ClientProvider>().receivedData;
    final isConnected = context.watch<ClientProvider>().isConnected;
    updateReceivedData(data);
    return Scaffold(
      appBar: AppBar(title: const Text("Secondary (Leg Side)")),
      body: Center(
        child: Column(
          children: [
            const SizedBox(height: 10),
            isConnected
                ? const Text("Connected")
                : Column(
                    children: [
                      Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: TextField(
                          decoration: const InputDecoration(
                            labelText: "Enter IP Address (e.g 10.2.0.2)",
                            border: OutlineInputBorder(),
                          ),
                          keyboardType: TextInputType.number,
                          controller: _controller,
                          onChanged: (value) {
                            ipAddress = value;
                          },
                        ),
                      ),
                      ElevatedButton(
                        onPressed: () {
                          connectionController
                              .connectToServer(ipAddress)
                              .then((_) {})
                              .catchError((error) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                  content: Text(
                                      "Error connecting to server: $error")),
                            );
                          });
                        },
                        child: const Text("Connect"),
                      ),
                    ],
                  ),
            const SizedBox(height: 30),
            const Text("Received Data:", style: TextStyle(fontSize: 18)),
            Text(recievedMsg,
                style: const TextStyle(fontSize: 24, color: Colors.blue)),
            const SizedBox(height: 30),
          ],
        ),
      ),
    );
  }
}
