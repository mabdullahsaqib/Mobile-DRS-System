import 'package:flutter/material.dart';
import 'package:vector_math/vector_math_64.dart';
import '../utils/video_split_converter.dart';
import 'dart:convert';

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
  dynamic result;

  @override
  void initState() {
    super.initState();
    processVideo(widget.mainVideoPath, 30, widget.cameraPositions,
            widget.cameraRotations)
        .then((value) {
      setState(() {
        result = value;
      });
    }).catchError((error) {
      print("Error processing video: $error");
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Video Player')),
      body: result == null
          ? Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: result.length,
              itemBuilder: (context, index) {
                return ListTile(
                  title: Text('Frame ${result[index]['frameId']}'),
                  subtitle: Column(
                    children: [
                      Text(
                          'Camera Rotation: ${result[index]['cameraRotation']}'),
                      Text(
                          'Camera Position: ${result[index]['cameraPosition']}'),
                    ],
                  ),
                  leading:
                      Image.memory(base64Decode(result[index]['frameData'])),
                );
              },
            ),
    );
  }
}
