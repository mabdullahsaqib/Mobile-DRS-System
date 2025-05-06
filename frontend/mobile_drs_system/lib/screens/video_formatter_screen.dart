import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:vector_math/vector_math_64.dart' as vm;
import '../utils/video_split_converter.dart';
import '../routes/app_routes.dart';
import 'package:http/http.dart' as http;
import 'package:video_player/video_player.dart';
import 'package:mobile_drs_system/screens/processing_screen.dart';

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
  bool isProcessing = false;
  bool isSending = false;
  dynamic result;

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

Future<void> handleRequestReview() async {
  if (isProcessing) return;

  setState(() => isProcessing = true);

  result = await processVideo(
    widget.mainVideoPath,
    widget.cameraPositions,
    widget.cameraRotations,
  );

  try {
    final response = await http.post(
      Uri.parse('http://10.0.2.2:8000/submit-review'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(result),
    ).timeout(const Duration(seconds: 10));

    if (response.statusCode == 200) {
      final Map<String, dynamic> data = jsonDecode(response.body);
      final String reviewId = data['review_id'];

      await DeleteVideo(widget.mainVideoPath);

      if (mounted) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => ProcessingScreen(reviewId: reviewId),
          ),
        );
      }
    } else {
      print('Server error: ${response.statusCode}');
    }
  } catch (e) {
    print('Request failed: $e');
  }

  setState(() => isProcessing = false);
}


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A3F24),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: isProcessing || isSending
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const CircularProgressIndicator(color: Colors.white),
                      const SizedBox(height: 16),
                      Text(
                        isSending ? "Making Decision..." : "Processing video...",
                        style: const TextStyle(color: Colors.white),
                      ),
                    ],
                  ),
                )
              : Column(
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

                    // Video preview box
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

                    // Buttons
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
    );
  }
}
