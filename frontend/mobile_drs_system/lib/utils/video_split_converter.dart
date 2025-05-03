import 'dart:convert';
import 'dart:io';
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';
import 'package:vector_math/vector_math_64.dart';

class VideoFrameExtractor {
  static const platform = MethodChannel('com.example.video_frames_extractor');

  static Future<List<String>> extractFrames({
    required String videoPath,
    required String outputDir,
  }) async {
    try {
      final List<dynamic> frames = await platform.invokeMethod(
        'extractFrames',
        {
          'videoPath': videoPath,
          'outputDir': outputDir,
        },
      );
      return frames.cast<String>();
    } on PlatformException catch (e) {
      throw Exception("Failed to extract frames: ${e.message}");
    }
  }

  static Future<List<String>> extractAudio({
    required String videoPath,
    required String outputDir,
  }) async {
    try {
      final List<dynamic> audios = await platform.invokeMethod(
        'extractAudio',
        {
          'videoPath': videoPath,
          'outputDir': outputDir,
        },
      );
      return audios.cast<String>();
    } on PlatformException catch (e) {
      throw Exception("Failed to extract frames: ${e.message}");
    }
  }
}

Future<List<Map<String, dynamic>>> processVideo(
    String videoPath, List<Vector3> positions, List<Vector3> rotations) async {
  final tempDir = await getTemporaryDirectory();
  final framesDir = Directory('${tempDir.path}/frames');
  final audioDir = Directory('${tempDir.path}/audio');

  if (await framesDir.exists()) await framesDir.delete(recursive: true);
  if (await audioDir.exists()) await audioDir.delete(recursive: true);

  await framesDir.create(recursive: true);
  await audioDir.create(recursive: true);

  List<Map<String, dynamic>> result = [];

  try {
    final frames = await VideoFrameExtractor.extractFrames(
      videoPath: videoPath,
      outputDir: framesDir.path,
    );

    final audios = await VideoFrameExtractor.extractAudio(
      videoPath: videoPath,
      outputDir: audioDir.path,
    );

    for (int i = 0; i < frames.length; i++) {
      final frameFile = File(frames[i]);

      if (!await frameFile.exists()) {
        print("Frame file does not exist: ${frames[i]}");
        continue;
      }

      final base64Frame = base64Encode(await frameFile.readAsBytes());

      String base64Audio = '';
      if (i < audios.length && audios[i].isNotEmpty) {
        final audioFile = File(audios[i]);
        if (await audioFile.exists()) {
          base64Audio = base64Encode(await audioFile.readAsBytes());
          await audioFile.delete(); // Clean up audio file
        }
      }

      result.add({
        'frameId': i,
        'frameData': base64Frame,
        'audioData': base64Audio,
        'cameraRotation': {
          'x': rotations[i].x,
          'y': rotations[i].y,
          'z': rotations[i].z,
        },
        'cameraPosition': {
          'x': positions[i].x,
          'y': positions[i].y,
          'z': positions[i].z,
        },
      });

      await frameFile.delete();
    }
  } catch (e) {
    print("Error processing video: $e");
  }

  await framesDir.delete(recursive: true);
  await audioDir.delete(recursive: true);

  return result;
}
