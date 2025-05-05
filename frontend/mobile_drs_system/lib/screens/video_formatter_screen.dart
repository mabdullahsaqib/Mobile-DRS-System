import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:vector_math/vector_math_64.dart';
import '../utils/video_split_converter.dart';
import '../routes/app_routes.dart';
import 'dart:io';
import 'package:http/http.dart' as http;

Future<void> DeleteVideo(String videoPath) async {
  final videoFile = File(videoPath);
  if (await videoFile.exists()) {
    await videoFile.delete();
  } else {
    print("Video file does not exist: $videoPath");
  }
}

class VideoFormatScreen extends StatefulWidget {
  final String mainVideoPath;
  final List<Vector3> cameraPositions;
  final List<Vector3> cameraRotations;

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
  dynamic result;
  bool isProcessing = false;
  bool isSending = false;

  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Video Player')),
      body: Center(
        child: isProcessing
            ? Expanded(
                child: Column(
                  children: [
                    const CircularProgressIndicator(),
                    const SizedBox(height: 16),
                    const Text('Processing video...'),
                  ],
                ),
              )
            : isSending
                ? Expanded(
                    child: Column(
                      children: [
                        const CircularProgressIndicator(),
                        const SizedBox(height: 16),
                        Text("Making Decision..."),
                      ],
                    ),
                  )
                : Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text('Do you want a review?'),
                      ElevatedButton(
                        onPressed: () async {
                          if (isProcessing) return;
                          setState(() {
                            isProcessing = true;
                          });
                          result = await processVideo(widget.mainVideoPath,
                              widget.cameraPositions, widget.cameraRotations);
                          setState(() {
                            isSending = true;
                            isProcessing = false;
                          });
                          await DeleteVideo(widget.mainVideoPath);

                          try {
                            final response = await http
                                .post(
                                  Uri.parse(
                                      'http://10.0.2.2:8000/receive-json'),
                                  headers: {'Content-Type': 'application/json'},
                                  body: jsonEncode(result),
                                )
                                .timeout(Duration(
                                    seconds: 5)); // Prevent indefinite hangs

                            if (response.statusCode == 200) {
                              print('Success: ${response.body}');
                            } else {
                              print('Server error: ${response.statusCode}');
                            }
                          } catch (e) {
                            print('Request failed: $e');
                          }
                        },
                        child: const Text('Yes'),
                      ),
                      ElevatedButton(
                        onPressed: () async {
                          await DeleteVideo(widget.mainVideoPath);
                          Navigator.pop(context);
                        },
                        child: const Text('No'),
                      ),
                      ElevatedButton(
                        onPressed: () {
                          Navigator.pushNamed(
                            context,
                            AppRoutes.videoPlayer,
                            arguments: VideoPlayerScreenArguments(
                              mainVideoPath: widget.mainVideoPath,
                            ),
                          );
                        },
                        child: const Text('Watch Video'),
                      ),
                    ],
                  ),
      ),
    );
  }
}
