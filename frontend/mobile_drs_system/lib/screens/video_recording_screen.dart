import 'dart:async';
import 'dart:io';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_media_store/flutter_media_store.dart';
import 'package:mobile_drs_system/main.dart';
import 'package:mobile_drs_system/models/command_type.dart';
import 'package:mobile_drs_system/providers/network/client.dart';
import 'package:mobile_drs_system/providers/network/server.dart';
import 'package:mobile_drs_system/providers/video_save.dart';
import 'package:mobile_drs_system/routes/app_routes.dart';
import 'package:mobile_drs_system/utils/utils.dart';
import 'package:provider/provider.dart';

class VideoRecordingScreen extends StatefulWidget {
  const VideoRecordingScreen({super.key, required this.isSecondary});
  final bool isSecondary;
  @override
  State<VideoRecordingScreen> createState() => _VideoRecordingScreenState();
}

class _VideoRecordingScreenState extends State<VideoRecordingScreen> {
  bool _isLoading = true;
  bool _isRecording = false;
  String _videoPath = '';
  final _duration = 10;
  CameraController? _controller;
  Completer<void>? _recordingCompleter;
  Timer? _recordingTimer;

  Map<String, dynamic>? _clientData;

  @override
  void initState() {
    super.initState();
    initializeCameras();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (widget.isSecondary) {
        _setupClientDataListener();
      }
    });
  }

  void _setupClientDataListener() {
    // Get provider without listening
    final clientProvider = Provider.of<ClientProvider>(context, listen: false);

    // Subscribe to changes
    clientProvider.addListener(_handleClientDataChanges);
  }

  void _handleClientDataChanges() {
    final clientProvider = Provider.of<ClientProvider>(context, listen: false);
    final newData = clientProvider.receivedData;

    if (newData.isNotEmpty && newData != _clientData) {
      _clientData = newData;
      // Process the data outside of build
      if (_clientData != null) {
        switch (commandFromString(_clientData!["type"])) {
          case CommandType.startRecording:
            clientStartRecording();
            break;
          case CommandType.stopRecording:
            clientStopRecording();
            break;
          default:
            break;
        }
      }

      // Clear data after processing
      clientProvider.clearReceivedData();
    }
  }

  void initializeCameras() async {
    if (_controller != null) return; // Already initialized
    final cameras = await availableCameras();
    _controller = CameraController(
      cameras.firstWhere(
          (camera) => camera.lensDirection == CameraLensDirection.back),
      ResolutionPreset.high,
    );
    await _controller!.initialize();
    await _controller!.prepareForVideoRecording();
    setState(() {
      _isLoading = false;
    });
  }

  Future<void> serverStartRecording() async {
    final serverProvider = context.read<ServerProvider>();
    if (_isRecording ||
        _controller == null ||
        !_controller!.value.isInitialized ||
        !serverProvider.isRunning) {
      throw Exception('Camera not ready');
    }

    //Tell client to start recording

    await _controller!.startVideoRecording();
    setState(() {
      _isRecording = true;
      serverProvider.sendJSON({
        "type": CommandType.startRecording.name,
      });
    });

    // Automatically stop after duration seconds
    _recordingCompleter = Completer<void>();
    _recordingTimer = Timer(Duration(seconds: _duration), () {
      _recordingCompleter?.complete();
    });

    await _recordingCompleter!.future;

    //If recording is stopped then stopRecording() was called before startRecording could finish;
    if (_isRecording) {
      await serverStopRecording();
    }
    _recordingTimer = null;
    _recordingCompleter = null;
  }

  Future<void> serverStopRecording() async {
    final serverProvider = context.read<ServerProvider>();
    if (!_isRecording || _controller == null) return;

    final file = await _controller!.stopVideoRecording();
    setState(() {
      _isRecording = false;
      serverProvider.sendJSON({
        "type": CommandType.stopRecording.name,
      });
    });
    //Once video recording is stopped, we save file to the device and then
    //return the path to the file
    final flutterMediaStore = FlutterMediaStore();
    await flutterMediaStore.saveFile(
      fileData: await file.readAsBytes(),
      fileName: '${DateTime.now().millisecondsSinceEpoch}.mp4',
      mimeType: "video/mp4",
      rootFolderName: "MobileDRS",
      folderName: "Videos",
      onError: (e) {
        throw Exception("Error saving video: $e");
      },
      onSuccess: (uri, filePath) {
        _videoPath = filePath;
      },
    );

    if (_recordingCompleter != null && !_recordingCompleter!.isCompleted) {
      _recordingCompleter!.complete();
    }
    _recordingTimer?.cancel();
    _recordingTimer = null;
    _recordingCompleter = null;

    //Pop the screen and start waiting in the waitingScreen for the secondary device to send the video
    //This is used to show the secondary video after the recording is done
    if (mounted) {
      final videoService = context.read<VideoSaveDataProvider>();
      videoService.setMainVideoPath(_videoPath);
      Navigator.pushNamed(context, AppRoutes.masterWaiting);
    }
  }

//Client side functions
  Future<void> clientStartRecording() async {
    if (_isRecording || _controller == null) return;
    await _controller!.startVideoRecording();
    setState(() {
      _isRecording = true;
    });
    _recordingCompleter = Completer<void>();
    _recordingTimer = Timer(Duration(seconds: _duration), () {
      _recordingCompleter?.complete();
    });

    await _recordingCompleter!.future;
    if (_isRecording) {
      await serverStopRecording();
    }
    _recordingTimer = null;
    _recordingCompleter = null;
  }

  Future<void> clientStopRecording() async {
    if (!_isRecording || _controller == null) return;
    final file = await _controller!.stopVideoRecording();
    print("Client stopped recording");
    setState(() {
      _isRecording = false;
    });
    //Once video recording is stopped, we save file to the device and then
    //turn it to base64 and send it to the server
    final flutterMediaStore = FlutterMediaStore();
    await flutterMediaStore.saveFile(
      fileData: await file.readAsBytes(),
      fileName: '${DateTime.now().millisecondsSinceEpoch}_2.mp4',
      mimeType: "video/mp4",
      rootFolderName: "MobileDRS",
      folderName: "Videos",
      onError: (e) {
        throw Exception("Error saving video: $e");
      },
      onSuccess: (uri, filePath) async {
        _videoPath = filePath;
      },
    );

    //Show a loading dialog while sending the video and pop it when done

    // if (mounted) {
    //   try {
    //     await showDialog(
    //       context: context,
    //       barrierDismissible: false,
    //       builder: (_) => AlertDialog(
    //         content: Row(
    //           children: [
    //             const CircularProgressIndicator(),
    //             const SizedBox(width: 16),
    //             const Text("Sending video..."),
    //           ],
    //         ),
    //       ),
    //     );
    //   } catch (e) {
    //     print("Error showing dialog: $e");
    //     return;
    //   }
    // }
    // Send the recording to server after showing the dialog
    await sendRecordingToServer(_videoPath);
  }

  Future<void> sendRecordingToServer(String filePath) async {
    //Encode file as base64 string and send it and the filename
    final clientProvider = context.read<ClientProvider>();
    if (!clientProvider.isConnected) return;
    final file = File(filePath);
    if (!await file.exists()) {
      print("File does not exist: $filePath");
      scaffoldMessengerKey.currentState?.showSnackBar(
        SnackBar(content: Text("File does not exist :$filePath")),
      );
      return;
    }
    Uint8List bytes = await file.readAsBytes();
    print("Encoding String");
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
      await clientProvider.sendJSON(data);
      scaffoldMessengerKey.currentState?.showSnackBar(
        const SnackBar(content: Text("Recording sent to server")),
      );
      clientPopScreen();
    } catch (error) {
      scaffoldMessengerKey.currentState?.showSnackBar(
        SnackBar(content: Text("Error sending recording: $error")),
      );
    }
  }

  void clientPopScreen() {
    if (!mounted) return;

    // Schedule navigation for the next frame, after any pending UI updates
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;

      // Schedule outside the current execution cycle with a microtask
      Future.microtask(() {
        if (!mounted) return;

        try {
          // Just do a simple pop instead of complex navigation
          if (Navigator.canPop(context)) {
            Navigator.pop(context);
          }
        } catch (e) {
          print("Navigation error: $e");
        }
      });
    });
  }

  @override
  void dispose() {
    super.dispose();
    if (widget.isSecondary) {
      final clientProvider =
          Provider.of<ClientProvider>(context, listen: false);
      clientProvider.removeListener(_handleClientDataChanges);
    }
    if (_controller != null) {
      _controller!.dispose();
    }
  }

  @override
  Widget build(BuildContext context) {
    //If its secondary then we stop recording based on incoming clientProvider messages
    Widget buttons = Padding(
        padding: const EdgeInsets.only(bottom: 16.0),
        child: _isRecording
            ? FloatingActionButton(
                onPressed: serverStopRecording,
                backgroundColor: Colors.white,
                foregroundColor: Colors.black,
                child: Icon(Icons.stop),
              )
            : FloatingActionButton(
                onPressed: serverStartRecording,
                backgroundColor: Colors.white,
                foregroundColor: Colors.black,
                child: Icon(Icons.play_arrow),
              ));

    if (widget.isSecondary) {
      //Secondary case
      //If the secondary device is recording show no buttons
      buttons = Padding(
          padding: const EdgeInsets.only(bottom: 16.0),
          child: _isRecording
              ? FloatingActionButton(
                  onPressed: () {},
                  backgroundColor: Colors.white,
                  foregroundColor: Colors.black,
                  child: Icon(Icons.stop),
                )
              : FloatingActionButton(
                  onPressed: () {},
                  backgroundColor: Colors.white,
                  foregroundColor: Colors.black,
                  child: Icon(Icons.play_arrow),
                ));
      final clientProvider = context.watch<ClientProvider>();
      if (!clientProvider.isConnected) {
        WidgetsBinding.instance.addPostFrameCallback((_) {
          Navigator.pop(context);
          scaffoldMessengerKey.currentState?.showSnackBar(
            const SnackBar(content: Text("No connection to primary device")),
          );
        });
      }
    } else {
      //Primary case
      final serverProvider = context.watch<ServerProvider>();
      if (!serverProvider.isRunning) {
        WidgetsBinding.instance.addPostFrameCallback((_) {
          Navigator.pop(context);
          scaffoldMessengerKey.currentState?.showSnackBar(
            const SnackBar(content: Text("No connection to secondary device")),
          );
        });
      }
    }
    return Scaffold(
        appBar: AppBar(
          title: const Text('Video Recording'),
        ),
        body: _isLoading
            ? Center(
                child: Column(
                  children: [
                    const CircularProgressIndicator(),
                    const SizedBox(height: 16),
                    const Text('Loading camera...'),
                  ],
                ),
              )
            : Stack(
                children: <Widget>[
                  CameraPreview(_controller!),
                  Align(alignment: Alignment.bottomCenter, child: buttons),
                ],
              ));
  }
}
