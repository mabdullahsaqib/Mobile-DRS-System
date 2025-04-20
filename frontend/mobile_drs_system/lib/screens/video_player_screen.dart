import 'package:flutter/material.dart';
import '../providers/video_save.dart';
import 'package:provider/provider.dart';

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

  @override
  void initState() {
    super.initState();
    _videoSaveDataProvider =
        Provider.of<VideoSaveDataProvider>(context, listen: false);
    _videoSaveDataProvider.clearMainVideoPath();
    _videoSaveDataProvider.clearSecondaryVideoPath();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      child: Center(
        child:
            Text('Video Player Screen'), // Placeholder for video player widget
      ),
    );
  }
}
