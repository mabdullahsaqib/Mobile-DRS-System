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
      startTime: Duration(milliseconds: (start * 1000.round()).toInt()),
      endTime: Duration(milliseconds: (end * 1000.round()).toInt()),
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
    String twoDigitMinutes = twoDigits(duration.inMinutes.remainder(60));
    String twoDigitSeconds = twoDigits(duration.inSeconds.remainder(60));
    return "$twoDigitMinutes:$twoDigitSeconds";
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
  Widget build(BuildContext context) {
    final isLandscape =
        MediaQuery.of(context).orientation == Orientation.landscape;
    return Scaffold(
      appBar: AppBar(title: const Text('Video Player')),
      body: Center(
        child: _controller.value.isInitialized
            ? Stack(
                children: [
                  isLandscape
                      ? SizedBox.expand(
                          child: FittedBox(
                            fit: BoxFit.cover,
                            child: SizedBox(
                              width: _controller.value.size.width,
                              height: _controller.value.size.height,
                              child: VideoPlayer(_controller),
                            ),
                          ),
                        )
                      : SizedBox.expand(
                          child: FittedBox(
                            fit: BoxFit.contain, // Or BoxFit.contain
                            child: SizedBox(
                              width: _controller.value.size.height,
                              height: _controller.value.size.width,
                              child: VideoPlayer(_controller),
                            ),
                          ),
                        ),
                  Column(
                    mainAxisAlignment: MainAxisAlignment.end,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const SizedBox(width: 20),
                          Text(
                              textAlign: TextAlign.left,
                              "${formatVideoDuration(_controller.value.position)} / ${formatVideoDuration(_controller.value.duration)}",
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 16,
                              )),
                        ],
                      ),
                      Stack(children: [
                        IgnorePointer(
                          child: SizedBox(
                            height: 15,
                            child: VideoProgressIndicator(
                              colors: const VideoProgressColors(
                                  playedColor: Colors.orange),
                              _controller,
                              allowScrubbing: true,
                            ),
                          ),
                        ),
                        // Custom duration highlight boxes
                        Positioned.fill(
                          child: LayoutBuilder(
                            builder: (context, constraints) {
                              final totalDuration =
                                  _controller.value.duration.inMilliseconds;

                              return Stack(
                                children: timeDurations.map((duration) {
                                  final startFraction =
                                      duration.startTime.inMilliseconds /
                                          totalDuration;
                                  final endFraction =
                                      duration.endTime.inMilliseconds /
                                          totalDuration;
                                  final left =
                                      constraints.maxWidth * startFraction;
                                  final width = constraints.maxWidth *
                                      (endFraction - startFraction);
                                  final height =
                                      50.0; // Set the desired height here

                                  return Positioned(
                                    left: left,
                                    top: 5, // Center the block vertically
                                    bottom: 0,
                                    width: width,
                                    child: Container(
                                      color: Colors.yellow,
                                      height:
                                          height, // Specify the height of the block here
                                    ),
                                  );
                                }).toList(),
                              );
                            },
                          ),
                        ),

                        Opacity(
                          opacity: 0.1,
                          child: SizedBox(
                            height: 15,
                            child: VideoProgressIndicator(
                              colors: const VideoProgressColors(
                                  playedColor: Colors.black),
                              _controller,
                              allowScrubbing: true,
                            ),
                          ),
                        ),
                      ]),
                      const SizedBox(height: 10),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        crossAxisAlignment: CrossAxisAlignment.center,
                        children: [
                          IconButton(
                            onPressed: () {
                              _controller.seekTo(Duration(
                                  seconds:
                                      _controller.value.position.inSeconds -
                                          1));
                            },
                            icon: const Icon(Icons.arrow_back),
                            color: Colors.white,
                          ),
                          const SizedBox(width: 10),
                          IconButton(
                            icon: Icon(
                              _controller.value.isPlaying
                                  ? Icons.pause
                                  : Icons.play_arrow,
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
                          const SizedBox(width: 10),
                          IconButton(
                            onPressed: () {
                              _controller.seekTo(Duration(
                                  seconds:
                                      _controller.value.position.inSeconds +
                                          1));
                            },
                            icon: const Icon(Icons.arrow_forward),
                            color: Colors.white,
                          )
                        ],
                      ),
                      const SizedBox(height: 30),
                    ],
                  ),
                ],
              )
            : const CircularProgressIndicator(),
      ),
    );
  }
}
