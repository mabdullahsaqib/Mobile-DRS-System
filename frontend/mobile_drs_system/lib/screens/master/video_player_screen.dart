import 'package:flutter/material.dart';
import '../../providers/video_save.dart';
import 'package:video_player/video_player.dart';
import 'package:provider/provider.dart';
import 'dart:io';

class VideoPlayerScreen extends StatefulWidget {
  final String mainVideoPath;
  final String secondaryVideoPath;

  const VideoPlayerScreen({
    super.key,
    required this.mainVideoPath,
    required this.secondaryVideoPath,
  });

  @override
  State<VideoPlayerScreen> createState() => _VideoPlayerScreenState();
}

class _VideoPlayerScreenState extends State<VideoPlayerScreen> {
  late VideoSaveDataProvider _videoSaveDataProvider;

  late VideoPlayerController _mainVideoController;
  late VideoPlayerController _secondaryVideoController;

  @override
  void initState() {
    super.initState();
    _videoSaveDataProvider =
        Provider.of<VideoSaveDataProvider>(context, listen: false);
    _videoSaveDataProvider.clearMainVideoPath();
    _videoSaveDataProvider.clearSecondaryVideoPath();

    _mainVideoController = VideoPlayerController.file(
      File(widget.mainVideoPath),
    )..initialize().then((_) {
        setState(() {});
      });

    _secondaryVideoController = VideoPlayerController.file(
      File(widget.secondaryVideoPath),
    )..initialize().then((_) {
        setState(() {});
      });
  }

  @override
  void dispose() {
    _mainVideoController.dispose();
    _secondaryVideoController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Video Player')),
      body: Column(
        children: [
          if (_mainVideoController.value.isInitialized)
            AspectRatio(
              aspectRatio: _mainVideoController.value.aspectRatio,
              child: VideoPlayer(_mainVideoController),
            )
          else
            CircularProgressIndicator(),
          const SizedBox(height: 20),
          if (_secondaryVideoController.value.isInitialized)
            AspectRatio(
              aspectRatio: _secondaryVideoController.value.aspectRatio,
              child: VideoPlayer(_secondaryVideoController),
            )
          else
            CircularProgressIndicator(),
        ],
      ),
    );
  }
}
