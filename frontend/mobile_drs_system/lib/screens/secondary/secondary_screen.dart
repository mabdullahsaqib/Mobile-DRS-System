import 'package:flutter/material.dart';
import 'package:mobile_drs_system/controllers/connection.dart';
import 'package:mobile_drs_system/main.dart';
import 'package:mobile_drs_system/models/command_type.dart';
import 'package:mobile_drs_system/providers/network/client.dart';
import 'package:mobile_drs_system/screens/video_recording_screen.dart';
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

  void updateReceivedData(Map<String, dynamic> data) {
    setState(() {
      receivedData = data;
      switch (commandFromString(data["type"])) {
        case CommandType.switchToCamera:
          recievedMsg = "Recording started";
          clientStartRecording();
          break;
        case CommandType.stopRecording:
          recievedMsg = "Recording stopped";
          break;
        case CommandType.sendString:
          recievedMsg = "String received: ${data["data"]}";
          break;
        default:
          recievedMsg = "Unknown command";
      }
    });
  }

  void clientStartRecording() async {
    if (!_clientProvider.isConnected) return;
    await Navigator.push(
        context,
        MaterialPageRoute(
            builder: (context) => VideoRecordingScreen(isSecondary: true)));
  }

  void _setupClientDataListener() {
    _clientProvider.addListener(() {
      if (_clientProvider.receivedData.isNotEmpty) {
        updateReceivedData(_clientProvider.receivedData);
      }
    });
  }

  @override
  void initState() {
    super.initState();
    _clientProvider = Provider.of<ClientProvider>(context, listen: false);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _setupClientDataListener();
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    if (_clientProvider.isConnected) {
      _clientProvider.disconnect();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final connectionController = context.watch<ConnectionController>();
    final isConnected = context.watch<ClientProvider>().isConnected;
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
                            scaffoldMessengerKey.currentState?.showSnackBar(
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
