import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';
import 'dart:io';

class VideoPlayerScreen extends StatefulWidget {
  final String mainVideoPath;

  const VideoPlayerScreen({
    super.key,
    required this.mainVideoPath,
  });

  @override
  State<VideoPlayerScreen> createState() => _VideoPlayerScreenState();
}

class _VideoPlayerScreenState extends State<VideoPlayerScreen> {
  late VideoPlayerController _controller;

  @override
  void initState() {
    super.initState();
    _controller = VideoPlayerController.file(File(widget.mainVideoPath))
      ..initialize().then((_) {
        setState(() {});
      });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Video Player')),
      body: Center(
        child: _controller.value.isInitialized
            ? Column(
                children: [
                  AspectRatio(
                    aspectRatio: _controller.value.aspectRatio,
                    child: VideoPlayer(_controller),
                  ),
                  VideoProgressIndicator(
                    _controller,
                    allowScrubbing: true,
                  ),
                  Row(
                    children: [
                      IconButton(
                          onPressed: () {
                            _controller.seekTo(Duration(
                                seconds:
                                    _controller.value.position.inSeconds - 1));
                          },
                          icon: const Icon(Icons.arrow_back)),
                      const SizedBox(width: 10),
                      IconButton(
                        icon: Icon(
                          _controller.value.isPlaying
                              ? Icons.pause
                              : Icons.play_arrow,
                        ),
                        onPressed: () {
                          setState(() {
                            _controller.value.isPlaying
                                ? _controller.pause()
                                : _controller.play();
                          });
                        },
                      ),
                      const SizedBox(width: 10),
                      IconButton(
                        onPressed: () {
                          _controller.seekTo(Duration(
                              seconds:
                                  _controller.value.position.inSeconds + 1));
                        },
                        icon: const Icon(Icons.arrow_forward),
                      )
                    ],
                  ),
                ],
              )
            : const CircularProgressIndicator(),
      ),
    );
  }
}
