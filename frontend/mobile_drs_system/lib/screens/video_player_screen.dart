import 'package:flutter/material.dart';
import '../../providers/video_save.dart';
import 'package:video_player/video_player.dart';
import 'package:provider/provider.dart';
import 'dart:io';

class VideoPlayerScreen extends StatefulWidget {
  String mainVideoPath;
  String secondaryVideoPath;

  VideoPlayerScreen({
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

  @override
  void initState() {
    super.initState();
    _videoSaveDataProvider =
        Provider.of<VideoSaveDataProvider>(context, listen: false);
    if (widget.mainVideoPath.isEmpty) {
      widget.mainVideoPath =
          _videoSaveDataProvider.mainVideoPath; // Use the path from provider
    }
    _videoSaveDataProvider.clearMainVideoPath();
    _mainVideoController = VideoPlayerController.file(
      File(widget.mainVideoPath),
    )..initialize().then((_) {
        setState(() {});
      });
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
          if (_mainVideoController.value.isInitialized)
            AspectRatio(
              aspectRatio: _mainVideoController.value.aspectRatio,
              child: VideoPlayer(_mainVideoController),
            )
          else
            CircularProgressIndicator()
        ],
      ),
    );
  }
}
