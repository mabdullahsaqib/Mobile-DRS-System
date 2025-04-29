import 'package:flutter/material.dart';

class VideoPlayerScreen extends StatelessWidget {
  final String mainVideoPath;

  const VideoPlayerScreen({
    super.key,
    required this.mainVideoPath,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Video Player')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('Main Video Path: $mainVideoPath'),
          ],
        ),
      ),
    );
  }
}
