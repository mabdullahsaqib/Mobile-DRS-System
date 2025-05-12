import 'dart:io';
import 'package:flutter/material.dart';
import 'package:vector_math/vector_math_64.dart' as vm;
import '../utils/video_split_converter.dart';
import '../routes/app_routes.dart';
import 'package:video_player/video_player.dart';
import 'dart:async';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:math';

Future<void> DeleteVideo(String videoPath) async {
  final videoFile = File(videoPath);
  if (await videoFile.exists()) {
    await videoFile.delete();
  }
}

class VideoFormatScreen extends StatefulWidget {
  final String mainVideoPath;
  final List<vm.Vector3> cameraPositions;
  final List<vm.Vector3> cameraRotations;

  const VideoFormatScreen({
    super.key,
    required this.mainVideoPath,
    required this.cameraPositions,
    required this.cameraRotations,
  });

  @override
  State<VideoFormatScreen> createState() => _VideoFormatScreenState();
}

class _VideoFormatScreenState extends State<VideoFormatScreen> {
  late VideoPlayerController _videoController;
  dynamic results;

  @override
  void initState() {
    super.initState();
    _videoController = VideoPlayerController.file(File(widget.mainVideoPath))
      ..initialize().then((_) {
        setState(() {});
      });
  }

  @override
  void dispose() {
    _videoController.dispose();
    super.dispose();
  }

  bool isProcessing = false;
  String? reviewId;
  Timer? pollingTimer;
  bool reviewDone = false;
  bool errorOccurred = false;

  Future<void> handleRequestReview() async {
    if (isProcessing) return;

    setState(() {
      isProcessing = true;
    });

    // Check if camera positions or rotations are empty
    if (widget.cameraPositions.isEmpty || widget.cameraRotations.isEmpty) {
      final videoDuration = _videoController.value.duration.inSeconds;
      final frameCount = videoDuration * 30;

      final random = Random();
      widget.cameraPositions.addAll(List.generate(
          frameCount,
          (_) => vm.Vector3(
                random.nextDouble(),
                random.nextDouble(),
                random.nextDouble(),
              )));
      widget.cameraRotations.addAll(List.generate(
          frameCount,
          (_) => vm.Vector3(
                random.nextDouble(),
                random.nextDouble(),
                random.nextDouble(),
              )));
    }

    results = await processVideo(
      widget.mainVideoPath,
      widget.cameraPositions,
      widget.cameraRotations,
    );

    try {
      // Simulated POST request

      print("Request body : $results");
      print("Frame data : ${results[0]['frameData'].runtimeType}");
      print("Audio data : ${results[0]['audioData'].runtimeType}");
      print("Position : ${results[0]['cameraPosition']['x'].runtimeType}");
      print("Rotation : ${results[0]['cameraRotation']['x'].runtimeType}");

      final response = await http
          .post(
            Uri.parse('http://10.0.2.2:8000/submit-review'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({"results": results}),
          )
          .timeout(const Duration(seconds: 100));

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = jsonDecode(response.body);
        reviewId = data['review_id'];

        // reviewId = 'test-id'; // Use dummy reviewId for testing

        await DeleteVideo(widget.mainVideoPath);
        _startPolling();
      } else {
        throw Exception('Server error ${response.statusCode}');
      }
    } catch (e) {
      setState(() {
        errorOccurred = true;
      });
      print('Request failed: $e');
    }
  }

  void _startPolling() {
    pollingTimer = Timer.periodic(const Duration(seconds: 5), (_) async {
      try {
        final response = await http.get(
          Uri.parse('http://10.0.2.2:8000/get-review/$reviewId'),
        );

        if (response.statusCode == 200) {
          final Map<String, dynamic> data = jsonDecode(response.body);
          if (data['status'] == 'complete') {
            pollingTimer?.cancel();
            if (mounted) {
              Navigator.pushNamed(
                context,
                AppRoutes.decision,
                arguments: DecisionScreenArguments(data: data),
              );
            }
          }
        }

        // Simulate done response
//       pollingTimer?.cancel();
//       if (mounted) {
//        Navigator.pushReplacement(
//   context,
//   MaterialPageRoute(
//     builder: (_) => DecisionScreen(data: {
//       "video_base64": null, //augmentedBase64Frames, // List<String> of base64 frames (data:image/jpeg;base64,...)
//       "decision": "OUT", // or "NOT OUT", etc.
//     }),
//   ),
// );
//     }
      } catch (e) {
        print('Polling error: $e');
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A3F24),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: isProcessing
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: const [
                      Text(
                        'REVIEW IN PROGRESS',
                        style: TextStyle(
                          color: Colors.greenAccent,
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 1.5,
                        ),
                      ),
                      SizedBox(height: 24),
                      Icon(Icons.sports_cricket,
                          size: 64, color: Colors.greenAccent),
                      SizedBox(height: 24),
                      Text(
                        'Third umpire is watching carefully...',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: Colors.greenAccent,
                          fontSize: 16,
                        ),
                      ),
                      SizedBox(height: 48),
                      CircularProgressIndicator(
                        color: Colors.greenAccent,
                        strokeWidth: 4,
                      ),
                    ],
                  ),
                )
              : SingleChildScrollView(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      // App title
                      Row(
                        children: const [
                          Icon(Icons.sports_cricket, color: Colors.white),
                          SizedBox(width: 10),
                          Text(
                            "DRS Umpire",
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 22,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 24),

                      // Video preview
                      AspectRatio(
                        aspectRatio: _videoController.value.aspectRatio,
                        child: Stack(
                          alignment: Alignment.center,
                          children: [
                            ClipRRect(
                              borderRadius: BorderRadius.circular(16),
                              child: VideoPlayer(_videoController),
                            ),
                            GestureDetector(
                              onTap: () {
                                setState(() {
                                  _videoController.value.isPlaying
                                      ? _videoController.pause()
                                      : _videoController.play();
                                });
                              },
                              child: Container(
                                decoration: const BoxDecoration(
                                  color: Colors.black38,
                                  shape: BoxShape.circle,
                                ),
                                padding: const EdgeInsets.all(12),
                                child: Icon(
                                  _videoController.value.isPlaying
                                      ? Icons.pause
                                      : Icons.play_arrow,
                                  size: 40,
                                  color: Colors.white,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),

                      const Text(
                        "Do you want to send this for review?",
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 20,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 24),

                      ElevatedButton(
                        onPressed: handleRequestReview,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF36B37E),
                          foregroundColor: Colors.white,
                          textStyle: const TextStyle(
                              fontSize: 16, fontWeight: FontWeight.bold),
                          padding: const EdgeInsets.symmetric(
                              horizontal: 32, vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(14),
                          ),
                        ),
                        child: const Text("Request Review"),
                      ),
                      const SizedBox(height: 12),
                      ElevatedButton(
                        onPressed: () {
                          Navigator.pushNamed(
                            context,
                            AppRoutes.videoPlayer,
                            arguments: VideoPlayerScreenArguments(
                                mainVideoPath: widget.mainVideoPath),
                          );
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF0B1D1B),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(
                              horizontal: 24, vertical: 14),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(14),
                          ),
                        ),
                        child: const Text("Watch Again"),
                      ),
                      const SizedBox(height: 12),
                      ElevatedButton(
                        onPressed: () async {
                          await DeleteVideo(widget.mainVideoPath);
                          Navigator.pop(context);
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF0B1D1B),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(
                              horizontal: 24, vertical: 14),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(14),
                          ),
                        ),
                        child: const Text("Discard & Re-record"),
                      ),
                    ],
                  ),
                ),
        ),
      ),
    );
  }
}
