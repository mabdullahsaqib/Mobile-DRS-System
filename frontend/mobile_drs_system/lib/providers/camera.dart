import 'dart:async';
import 'package:camera/camera.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_media_store/flutter_media_store.dart';

class CameraService with ChangeNotifier {
  CameraController? _controller;
  bool _isRecording = false;

  bool get isRecording => _isRecording;

  Completer<void>? _recordingCompleter;
  Timer? _recordingTimer;
  String path = ""; // Path to the current video being recorded

  Future<void> initialize() async {
    if (_controller != null) return; // Already initialized
    final cameras = await availableCameras();
    _controller = CameraController(
      cameras.firstWhere(
          (camera) => camera.lensDirection == CameraLensDirection.back),
      ResolutionPreset.high,
    );
    await _controller!.initialize();
    await _controller!.prepareForVideoRecording();
  }

  Future<void> delete() async {
    if (_controller != null) {
      await _controller!.dispose();
      _controller = null;
    }
  }

  @override
  Future<void> dispose() async {
    await delete();
    super.dispose();
  }

  Future<String> startRecording(int duration) async {
    if (_isRecording ||
        _controller == null ||
        !_controller!.value.isInitialized) {
      throw Exception('Camera not ready');
    }

    await _controller!.startVideoRecording();
    _isRecording = true;

    notifyListeners();
    // Automatically stop after duration seconds
    _recordingCompleter = Completer<void>();
    _recordingTimer = Timer(Duration(seconds: duration), () {
      _recordingCompleter?.complete();
    });

    await _recordingCompleter!.future;

    if (!_isRecording) await stopRecording();
    _recordingTimer = null;
    _recordingCompleter = null;
    return path; // Return the last video path
  }

  Future<String?> stopRecording() async {
    if (!_isRecording || _controller == null) return null;

    final file = await _controller!.stopVideoRecording();
    _isRecording = false;

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
        path = filePath;
      },
    );

    if (_recordingCompleter != null && !_recordingCompleter!.isCompleted) {
      _recordingCompleter!.complete();
    }
    _recordingTimer?.cancel();
    _recordingTimer = null;
    _recordingCompleter = null;

    notifyListeners();
    return path;
  }
}
