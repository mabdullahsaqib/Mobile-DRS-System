import 'dart:async';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter_media_store/flutter_media_store.dart';
import 'package:mobile_drs_system/providers/video_save.dart';
import 'package:mobile_drs_system/routes/app_routes.dart';
import 'package:provider/provider.dart';

class VideoRecordingScreen extends StatefulWidget {
  const VideoRecordingScreen({super.key});
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

  @override
  void initState() {
    super.initState();
    initializeCameras();
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
    if (_isRecording ||
        _controller == null ||
        !_controller!.value.isInitialized) {
      throw Exception('Camera not ready');
    }

    //Tell client to start recording

    await _controller!.startVideoRecording();
    setState(() {
      _isRecording = true;
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
    if (!_isRecording || _controller == null) return;

    final file = await _controller!.stopVideoRecording();
    setState(() {
      _isRecording = false;
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
      Navigator.pushNamed(context, AppRoutes.videoPlayer);
    }
  }

  @override
  void dispose() {
    super.dispose();
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
