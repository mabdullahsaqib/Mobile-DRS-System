import 'dart:async';
import 'package:camera/camera.dart';
import 'package:flutter/widgets.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart';

class CameraService with ChangeNotifier {
  CameraController? _controller;
  bool _isRecording = false;
  String? _lastVideoPath;

  bool get isRecording => _isRecording;
  String? get lastVideoPath => _lastVideoPath;

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
  }

  Future<void> delete() async {
    if (_controller != null) {
      await _controller!.dispose();
      _controller = null;
    }
  }

  Future<String> startRecording(int duration) async {
    if (_controller == null) {
      await initialize();
    }
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

    final directory = await getApplicationDocumentsDirectory();
    path = join(directory.path, '${DateTime.now().millisecondsSinceEpoch}.mp4');

    if (_recordingCompleter != null && !_recordingCompleter!.isCompleted) {
      _recordingCompleter!.complete();
    }
    _recordingTimer?.cancel();
    _recordingTimer = null;
    _recordingCompleter = null;

    await file.saveTo(path); // Save the video to the new path
    notifyListeners();
    await delete();
    return path;
  }
}
