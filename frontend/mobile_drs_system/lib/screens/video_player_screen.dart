import 'package:flutter/cupertino.dart';

class VideoPlayerScreen extends StatelessWidget {
  final String mainVideoPath;
  final String secondaryVideoPath;

  const VideoPlayerScreen({
    super.key,
    required this.mainVideoPath,
    required this.secondaryVideoPath,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      child: Center(
        child: Text('Video Player Screen'),
      ),
    );
  }
}
