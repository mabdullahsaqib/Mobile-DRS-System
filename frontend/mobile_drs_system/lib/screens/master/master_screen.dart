import 'package:flutter/material.dart';
import 'package:mobile_drs_system/main.dart';
import 'package:mobile_drs_system/controllers/connection.dart';
import 'package:mobile_drs_system/models/command_type.dart';
import 'package:mobile_drs_system/providers/network/server.dart';
import 'package:mobile_drs_system/screens/video_recording_screen.dart';
import 'package:provider/provider.dart';
import '../../providers/video_save.dart';

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
  late VideoSaveDataProvider _videoSaveDataProvider; // For methods/dispose
  bool isSecondaryVideoSaved = false; // to go to video player screen

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

  // void serverStartRecording() {
  //   //Start Recording if camera service isnt recording and server is running
  //   if (_cameraService.isRecording) return;
  //   if (!_serverProvider.isRunning) return;

  //   _cameraService.startRecording(10).then((path) {
  //     //Once camera service is done recording, show the path in a snackbar
  //     //and navigate to the waiting screen
  //     scaffoldMessengerKey.currentState
  //         ?.showSnackBar(SnackBar(content: Text("Recording saved at: $path")));
  //     if (mounted) {
  //       //Clear the recieved data so waitingScreen recieves fresh data of recording
  //       _serverProvider.clearReceivedData();

  //       Navigator.pushNamed(context, AppRoutes.masterWaiting);
  //     }
  //     //Set the main video path in the provider so it can be used in the waiting screen
  //     _videoSaveDataProvider.setMainVideoPath(path);
  //     //If the secondary video path is not empty, navigate to the video player screen
  //     //This is used to show the secondary video after the recording is done
  //     if (_videoSaveDataProvider.secondaryVideoPath.isNotEmpty && mounted) {
  //       Navigator.push(
  //           context,
  //           MaterialPageRoute(
  //             builder: (context) => VideoPlayerScreen(
  //               mainVideoPath: _videoSaveDataProvider.mainVideoPath,
  //               secondaryVideoPath: _videoSaveDataProvider.secondaryVideoPath,
  //             ),
  //           ));
  //     }
  //   }).catchError((error) {
  //     scaffoldMessengerKey.currentState?.showSnackBar(
  //       SnackBar(content: Text("Error: $error")),
  //     );
  //   });
  //   setState(() {});
  //   _serverProvider.sendJSON({
  //     "type": CommandType.startRecording.name,
  //   });
  // }

  // //Once recording is stopped, we wait for the secondary device to send the recorded file so we need a waiting Screen
  // void serverStopRecording() {
  //   _cameraService = Provider.of<CameraService>(context, listen: false);
  //   _serverProvider = Provider.of<ServerProvider>(context, listen: false);
  //   if (!_cameraService.isRecording) return;
  //   _cameraService.stopRecording().then((path) {}).catchError((error) {
  //     scaffoldMessengerKey.currentState?.showSnackBar(
  //       SnackBar(content: Text("Error: $error")),
  //     );
  //   });
  //   setState(() {});
  //   _serverProvider.sendJSON({
  //     "type": CommandType.stopRecording.name,
  //   });
  // }

  void gotoRecordingScreen() async {
    _serverProvider.sendJSON({
      "type": CommandType.switchToCamera.name,
    });
    await Navigator.push<String>(
        context,
        MaterialPageRoute(
            builder: (context) => const VideoRecordingScreen(
                  isSecondary: false,
                )));
  }

  //Called on init and every time the widget is rebuilt
  @override
  void initState() {
    super.initState();
    _serverProvider = Provider.of<ServerProvider>(context, listen: false);
    _videoSaveDataProvider =
        Provider.of<VideoSaveDataProvider>(context, listen: false);
    isSecondaryVideoSaved =
        _videoSaveDataProvider.secondaryVideoPath.isNotEmpty;
  }

  @override
  void dispose() {
    _controller.dispose();
    if (_serverProvider.isRunning) {
      _serverProvider.stopServer();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final connectionController = context.watch<ConnectionController>();
    final serverIsRunning = context.watch<ServerProvider>().isRunning;
    final serverIPAddress = context.watch<ServerProvider>().ipAddress;
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
              IconButton(
                  onPressed: () => gotoRecordingScreen(),
                  icon: const Icon(Icons.play_arrow)),
            ],
          ),
        ),
      ),
    );
  }
}
