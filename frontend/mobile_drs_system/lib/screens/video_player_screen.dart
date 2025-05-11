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

class TimeDuration {
  final Duration startTime;
  final Duration endTime;

  TimeDuration({
    required this.startTime,
    required this.endTime,
  });

  factory TimeDuration.fromDouble(double start, double end) {
    return TimeDuration(
      startTime: Duration(milliseconds: (start * 1000).round()),
      endTime: Duration(milliseconds: (end * 1000).round()),
    );
  }
}

class _VideoPlayerScreenState extends State<VideoPlayerScreen> {
  late VideoPlayerController _controller;

  List<TimeDuration> timeDurations = [
    TimeDuration.fromDouble(0.2, 0.8),
    TimeDuration.fromDouble(1.3, 2.35),
    TimeDuration.fromDouble(5.4, 6.45)
  ];

  String formatVideoDuration(Duration duration) {
    String twoDigits(int n) => n.toString().padLeft(2, '0');
    return "${twoDigits(duration.inMinutes)}:${twoDigits(duration.inSeconds.remainder(60))}";
  }

  @override
  void initState() {
    super.initState();
    _controller = VideoPlayerController.file(File(widget.mainVideoPath))
      ..initialize().then((_) {
        setState(() {});
      });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {

    return Scaffold(
      backgroundColor: const Color(0xFF0A3F24),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0A3F24),
        elevation: 0,
        title: const Text(
          'Video Player',
          style: TextStyle(color: Colors.white),
        ),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: Center(
        child: _controller.value.isInitialized
            ? Stack(
                children: [
                  Center(
                    child: AspectRatio(
                      aspectRatio: _controller.value.aspectRatio,
                      child: VideoPlayer(_controller),
                    ),
                  ),
                  Column(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      // Time indicator
                      Padding(
                        padding: const EdgeInsets.only(left: 16, bottom: 6),
                        child: Align(
                          alignment: Alignment.centerLeft,
                          child: Text(
                            "${formatVideoDuration(_controller.value.position)} / ${formatVideoDuration(_controller.value.duration)}",
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 14,
                            ),
                          ),
                        ),
                      ),

                      // Progress Bar with highlights
                      Stack(
                        children: [
                          SizedBox(
                            height: 15,
                            child: VideoProgressIndicator(
                              _controller,
                              allowScrubbing: true,
                              colors: const VideoProgressColors(
                                playedColor: Colors.greenAccent,
                                bufferedColor: Colors.white30,
                                backgroundColor: Colors.white10,
                              ),
                            ),
                          ),
                          Positioned.fill(
                            child: LayoutBuilder(
                              builder: (context, constraints) {
                                final total = _controller.value.duration.inMilliseconds;
                                return Stack(
                                  children: timeDurations.map((t) {
                                    final start = t.startTime.inMilliseconds / total;
                                    final end = t.endTime.inMilliseconds / total;
                                    return Positioned(
                                      left: constraints.maxWidth * start,
                                      width: constraints.maxWidth * (end - start),
                                      top: 2,
                                      height: 10,
                                      child: Container(
                                        color: Colors.yellow,
                                      ),
                                    );
                                  }).toList(),
                                );
                              },
                            ),
                          ),
                        ],
                      ),

                      const SizedBox(height: 10),

                      // Playback controls
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          IconButton(
                            onPressed: () {
                              final newPos = _controller.value.position - const Duration(seconds: 1);
                              _controller.seekTo(newPos < Duration.zero ? Duration.zero : newPos);
                            },
                            icon: const Icon(Icons.replay_10),
                            color: Colors.white,
                          ),
                          IconButton(
                            icon: Icon(
                              _controller.value.isPlaying ? Icons.pause : Icons.play_arrow,
                              color: Colors.white,
                            ),
                            onPressed: () {
                              setState(() {
                                _controller.value.isPlaying
                                    ? _controller.pause()
                                    : _controller.play();
                              });
                            },
                          ),
                          IconButton(
                            onPressed: () {
                              final max = _controller.value.duration;
                              final newPos = _controller.value.position + const Duration(seconds: 1);
                              _controller.seekTo(newPos > max ? max : newPos);
                            },
                            icon: const Icon(Icons.forward_10),
                            color: Colors.white,
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),

                      // Done button
                      TextButton(
                        onPressed: () => Navigator.pop(context),
                        child: const Text(
                          "Done",
                          style: TextStyle(color: Colors.white70),
                        ),
                      ),
                      const SizedBox(height: 12),
                    ],
                  ),
                ],
              )
            : const CircularProgressIndicator(color: Colors.white),
      ),
    );
  }
}
