import 'dart:async';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter_media_store/flutter_media_store.dart';
import 'package:mobile_drs_system/routes/app_routes.dart';
import 'package:mobile_drs_system/utils/kalan_filter.dart';
import 'package:sensors_plus/sensors_plus.dart';
import 'package:vector_math/vector_math_64.dart' as vm;

class VideoRecordingScreen extends StatefulWidget {
  const VideoRecordingScreen({super.key});

  @override
  State<VideoRecordingScreen> createState() => _VideoRecordingScreenState();
}

class _VideoRecordingScreenState extends State<VideoRecordingScreen> {
  bool _isLoading = true;
  bool _isRecording = false;
  String _videoPath = '';
  final int _duration = 10;
  CameraController? _controller;
  Completer<void>? _recordingCompleter;
  Timer? _recordingTimer;
  Duration _recordingTime = Duration.zero;

  vm.Vector3 _accel = vm.Vector3.zero();
  vm.Vector3 _gyro = vm.Vector3.zero();
  vm.Vector3 _mag = vm.Vector3.zero();
  DateTime? _last;
  final KalmanFilter _kf = KalmanFilter();
  final List<vm.Vector3> _positions = [];
  final List<vm.Vector3> _rotations = [];
  Timer? _savingTimer;
  bool _shouldSave = false;

  @override
  void initState() {
    super.initState();
    initializeCameras();
    _calibrateGyro();

    accelerometerEvents.listen((e) => _accel = vm.Vector3(e.x, e.y, e.z));
    gyroscopeEvents.listen((e) => _gyro = vm.Vector3(e.x, e.y, e.z));
    magnetometerEvents.listen((e) => _mag = vm.Vector3(e.x, e.y, e.z));

    Future.delayed(const Duration(seconds: 1), () {
      _kf.initializeFromAccel(_accel);
    });

    Timer.periodic(const Duration(milliseconds: 20), (_) => _updateFusion());
  }

  void _calibrateGyro() {
    vm.Vector3 sum = vm.Vector3.zero();
    int count = 0;
    StreamSubscription<GyroscopeEvent>? sub;
    sub = gyroscopeEvents.listen((e) {
      if (count < 100) {
        sum += vm.Vector3(e.x, e.y, e.z);
        count++;
      } else {
        _kf.calibrateGyroBias(sum / count.toDouble());
        sub?.cancel();
      }
    });
  }

  void _updateFusion() {
    final now = DateTime.now();
    if (_last == null) {
      _last = now;
      return;
    }
    double dt = now.difference(_last!).inMilliseconds.clamp(1, 50) / 1000.0;
    _last = now;
    _kf.update(dt: dt, accel: _accel, gyro: _gyro, mag: _mag);
  }

  Future<void> initializeCameras() async {
    if (_controller != null) return;
    final cameras = await availableCameras();
    _controller = CameraController(
      cameras.firstWhere((camera) => camera.lensDirection == CameraLensDirection.back),
      ResolutionPreset.high,
    );
    await _controller!.initialize();
    await _controller!.prepareForVideoRecording();
    setState(() {
      _isLoading = false;
    });
  }

  Future<void> serverStartRecording() async {
    if (_isRecording || _controller == null || !_controller!.value.isInitialized) {
      throw Exception('Camera not ready');
    }

    await _controller!.startVideoRecording();
    _shouldSave = true;
    _recordingTime = Duration.zero;

    _savingTimer = Timer.periodic(const Duration(milliseconds: 33), (_) {
      if (_shouldSave) {
        _positions.add(vm.Vector3(
          double.parse(_kf.position.x.toStringAsFixed(2)),
          double.parse(_kf.position.y.toStringAsFixed(2)),
          double.parse(_kf.position.z.toStringAsFixed(2)),
        ));
        _rotations.add(vm.Vector3(
          double.parse(_kf.rotation.x.toStringAsFixed(2)),
          double.parse(_kf.rotation.y.toStringAsFixed(2)),
          double.parse(_kf.rotation.z.toStringAsFixed(2)),
        ));
      }
    });

    _recordingCompleter = Completer<void>();
    _recordingTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      setState(() {
        _recordingTime += const Duration(seconds: 1);
      });
      if (_recordingTime.inSeconds >= _duration) {
        _recordingCompleter?.complete();
      }
    });

    setState(() {
      _isRecording = true;
    });

    await _recordingCompleter!.future;
    if (_isRecording) {
      await serverStopRecording();
    }
  }

  Future<void> serverStopRecording() async {
    if (!_isRecording || _controller == null) return;

    final file = await _controller!.stopVideoRecording();
    _shouldSave = false;
    _savingTimer?.cancel();
    _savingTimer = null;
    _recordingTimer?.cancel();
    _recordingTime = Duration.zero;

    setState(() {
      _isRecording = false;
    });

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

    if (mounted) {
      Navigator.pushNamed(
        context,
        AppRoutes.videoFormat,
        arguments: VideoFormatScreenArguments(
          mainVideoPath: _videoPath,
          cameraPositions: _positions,
          cameraRotations: _rotations,
        ),
      );
    }
  }

  @override
  void dispose() {
    _controller?.dispose();
    _recordingTimer?.cancel();
    _savingTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    String formattedTime = _recordingTime.toString().split('.').first.padLeft(5, "0");

    return Scaffold(
      backgroundColor: Colors.black,
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(color: Colors.white),
            )
          : Stack(
              children: [
                // Camera Preview
                Positioned.fill(
                  child: Container(
                    decoration: BoxDecoration(
                      border: Border.all(
                        color: const Color(0xFF0A3F24), // theme-colored border
                        width: 6,
                      ),
                    ),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(0),
                      child: CameraPreview(_controller!),
                    ),
                  ),
                ),

                // Timer
                Positioned(
                  top: 48,
                  left: 0,
                  right: 0,
                  child: Center(
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.4),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        formattedTime,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 1.5,
                        ),
                      ),
                    ),
                  ),
                ),

                // Record Button
                Positioned(
                  bottom: 40,
                  left: 0,
                  right: 0,
                  child: Center(
                    child: GestureDetector(
                      onTap: _isRecording ? serverStopRecording : serverStartRecording,
                      child: Container(
                        width: 80,
                        height: 80,
                        decoration: BoxDecoration(
                          color: Colors.redAccent,
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.white, width: 6),
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
    );
  }
}
