import 'dart:convert';
import 'dart:typed_data';
import 'package:vector_math/vector_math_64.dart';
import 'package:video_thumbnail/video_thumbnail.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';

Future<List<Map<String, dynamic>>> processVideo(String videoPath, int fps,
    List<Vector3> cameraPositions, List<Vector3> cameraRotations) async {
  // Step 1: Extract frames
  List<Map<String, dynamic>> result = [];
  final totalFrames = await _getTotalFrames(videoPath, fps);

  for (int i = 0; i < totalFrames; i++) {
    // Extract frame
    final timeMs = (i * (1000 / fps)).toInt();
    final frameData = await _extractFrame(videoPath, timeMs);

    // Extract audio chunk corresponding to frame
    final audioData = await _extractAudioChunk(videoPath, i, fps);

    result.add({
      'frameId': i + 1,
      'frameData': base64Encode(frameData),
      'audio': base64Encode(audioData),
      'cameraRotation': {
        'x': cameraRotations[i].x,
        'y': cameraRotations[i].y,
        'z': cameraRotations[i].z,
      },
      'cameraPosition': {
        'x': cameraPositions[i].x,
        'y': cameraPositions[i].y,
        'z': cameraPositions[i].z,
      },
    });
  }

  return result;
}

// Get total frames based on the video's duration and frame rate (fps)
Future<int> _getTotalFrames(String videoPath, int fps) async {
  final videoFile = File(videoPath);

  // This is a workaround to calculate total frames
  final fileDuration = await _getVideoDuration(videoFile);
  final totalFrames = (fileDuration * fps).ceil();
  return totalFrames;
}

// Extract frame using video_thumbnail package
Future<Uint8List> _extractFrame(String videoPath, int timeMs) async {
  return (await VideoThumbnail.thumbnailData(
    video: videoPath,
    imageFormat: ImageFormat.PNG,
    timeMs: timeMs,
    quality: 100,
  ))!;
}

// Extract audio chunk for a frame
Future<Uint8List> _extractAudioChunk(
    String videoPath, int frameId, int fps) async {
  final startTime = frameId * (1 / fps); // Time in seconds
  final duration = 1 / fps; // Duration of each frame in seconds

  final tempDir = await getTemporaryDirectory();
  final audioFile =
      await _extractAudio(videoPath, startTime, duration, tempDir.path);

  // Read the extracted audio data
  final audioData = await audioFile.readAsBytes();
  return audioData;
}

// Extract audio chunk for a specific start time and duration
Future<File> _extractAudio(String videoPath, double startTime, double duration,
    String outputDir) async {
  final tempFile =
      File('$outputDir/audio_chunk_${startTime.toStringAsFixed(3)}.wav');

  // Here we simulate audio extraction using a simple approach. Normally you need to use libraries like ffmpeg.
  // As we cannot use ffmpeg, this is only a placeholder, not an actual working solution without ffmpeg.

  // For now, let’s assume you have an audio file per frame in real scenario
  return tempFile;
}

// Get the video duration in seconds (simplified here)
Future<double> _getVideoDuration(File videoFile) async {
  // Normally you would use ffmpeg here, but for now we’ll estimate based on the file's length
  // or you could use another package to fetch duration.
  final file = videoFile.lengthSync();
  final durationInSeconds =
      file / 1000; // Assuming 1KB = 1 second (just for simulation)
  return durationInSeconds;
}
