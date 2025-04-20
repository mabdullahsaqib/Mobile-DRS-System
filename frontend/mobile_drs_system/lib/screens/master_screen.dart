import 'package:flutter/material.dart';
import 'package:mobile_drs_system/main.dart';
import 'package:mobile_drs_system/providers/camera.dart';
import 'package:mobile_drs_system/controllers/connection.dart';
import 'package:mobile_drs_system/models/command_type.dart';
import 'package:mobile_drs_system/providers/network/server.dart';
import 'package:mobile_drs_system/screens/master_waiting_screen.dart';
import 'package:provider/provider.dart';

class MasterScreen extends StatefulWidget {
  const MasterScreen({super.key});

  @override
  MasterScreenState createState() => MasterScreenState();
}

class MasterScreenState extends State<MasterScreen> {
  String input = "";
  String sentData = "";

  final _controller = TextEditingController();

  late ServerProvider _serverProvider; // For methods/dispose
  late CameraService _cameraService; // For methods/dispose

  void handleSubmit(BuildContext context) {
    if (input.isEmpty) {
      scaffoldMessengerKey.currentState?.showSnackBar(
        const SnackBar(content: Text("Please enter some data")),
      );
      return;
    }
    _serverProvider.sendJSON({
      "type": CommandType.sendString.name,
      "data": input,
    });
    scaffoldMessengerKey.currentState?.showSnackBar(
      const SnackBar(content: Text("Data sent successfully")),
    );
    setState(() {
      sentData = input;
      _controller.clear();
    });
  }

  void serverStartRecording() {
    if (_cameraService.isRecording) return;
    if (!_serverProvider.isRunning) return;
    _cameraService.startRecording(10).then((path) {
      scaffoldMessengerKey.currentState
          ?.showSnackBar(SnackBar(content: Text("Recording saved at: $path")));
      if (mounted) {
        _serverProvider.clearReceivedData();
        Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const MasterWaitingScreen(),
            ));
      }
    }).catchError((error) {
      scaffoldMessengerKey.currentState?.showSnackBar(
        SnackBar(content: Text("Error: $error")),
      );
    });
    setState(() {});
    _serverProvider.sendJSON({
      "type": CommandType.startRecording.name,
    });
  }

  //Once recording is stopped, we wait for the secondary device to send the recorded file so we need a waiting Screen
  void serverStopRecording() {
    _cameraService = Provider.of<CameraService>(context, listen: false);
    _serverProvider = Provider.of<ServerProvider>(context, listen: false);
    if (!_cameraService.isRecording) return;
    _cameraService.stopRecording().then((path) {}).catchError((error) {
      scaffoldMessengerKey.currentState?.showSnackBar(
        SnackBar(content: Text("Error: $error")),
      );
    });
    setState(() {});
    _serverProvider.sendJSON({
      "type": CommandType.stopRecording.name,
    });
  }

  //Called on init and every time the widget is rebuilt
  @override
  void initState() {
    super.initState();
    _serverProvider = Provider.of<ServerProvider>(context, listen: false);
    _cameraService = Provider.of<CameraService>(context, listen: false);
    _cameraService.initialize();
  }

  @override
  void dispose() {
    _controller.dispose();
    if (_serverProvider.isRunning) {
      _serverProvider.stopServer();
    }
    _cameraService.delete();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final connectionController = context.watch<ConnectionController>();
    final serverIsRunning = context.watch<ServerProvider>().isRunning;
    final serverIPAddress = context.watch<ServerProvider>().ipAddress;
    final isRecording = context.watch<CameraService>().isRecording;
    return Scaffold(
      appBar: AppBar(title: const Text("Master (Bowler's End)")),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: SingleChildScrollView(
          physics: const NeverScrollableScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const SizedBox(height: 10),
              serverIsRunning
                  ? Text("Server is running on IP: $serverIPAddress",
                      style: const TextStyle(fontSize: 18))
                  : ElevatedButton(
                      onPressed: () {
                        connectionController
                            .startServer()
                            .then((_) {})
                            .catchError((error) {
                          scaffoldMessengerKey.currentState?.showSnackBar(
                            SnackBar(
                                content: Text("Error starting server: $error")),
                          );
                        });
                      },
                      child: const Text("Start Server"),
                    ),
              const SizedBox(height: 10),
              TextField(
                controller: _controller,
                decoration: const InputDecoration(
                  labelText: "Enter some data",
                  border: OutlineInputBorder(),
                ),
                onChanged: (val) => input = val,
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () => handleSubmit(context),
                child: const Text("Send to Secondary"),
              ),
              const SizedBox(height: 30),
              const Text("Sent Data:", style: TextStyle(fontSize: 18)),
              Text(sentData,
                  style: const TextStyle(fontSize: 24, color: Colors.green)),
              const SizedBox(height: 30),
              isRecording
                  ? IconButton(
                      onPressed: () => serverStopRecording(),
                      icon: const Icon(Icons.stop))
                  : IconButton(
                      onPressed: () => serverStartRecording(),
                      icon: const Icon(Icons.play_arrow)),
            ],
          ),
        ),
      ),
    );
  }
}
