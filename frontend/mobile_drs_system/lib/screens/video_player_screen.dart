import 'package:flutter/material.dart';
import 'package:vector_math/vector_math_64.dart';
import 'package:video_player/video_player.dart';
import 'dart:io';

class VideoPlayerScreen extends StatefulWidget {
  final String mainVideoPath;
  final List<Vector3> cameraPositions;
  final List<Vector3> cameraRotations;

  const VideoPlayerScreen({
    super.key,
    required this.mainVideoPath,
    required this.cameraPositions,
    required this.cameraRotations,
  });

  @override
  State<VideoPlayerScreen> createState() => _VideoPlayerScreenState();
}

class _VideoPlayerScreenState extends State<VideoPlayerScreen> {
  late VideoPlayerController _mainVideoController;

  @override
  void initState() {
    super.initState();
    _mainVideoController = VideoPlayerController.file(
      File(widget.mainVideoPath),
    );
  }

  @override
  void dispose() {
    _mainVideoController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Video Player')),
      body: Column(
        children: [
          Text("Main Video Path: ${widget.mainVideoPath}"),
          Text("Camera Positions: ${widget.cameraPositions}"),
          Text("Camera Rotatations: ${widget.cameraRotations}"),
        ],
      ),
    );
  }
}
