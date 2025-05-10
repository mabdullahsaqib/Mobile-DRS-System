import 'package:mobile_drs_system/screens/home_screen.dart';
import 'package:mobile_drs_system/screens/video_formatter_screen.dart';
import 'package:mobile_drs_system/screens/video_recording_screen.dart';
import 'package:mobile_drs_system/screens/video_player_screen.dart';
import 'package:flutter/material.dart';
import 'package:vector_math/vector_math_64.dart';


class AppRoutes {
  static const String splash = '/splash';
  static const String home = '/';
  static const String master = '/master';
  static const String kalanFilter = '/kalan-filter';
  static const String masterWaiting = '/master-waiting';
  static const String videoRecording = '/video-recording';
  static const String videoPlayer = '/video-player';
  static const String videoFormat = '/video-format';

  static final Map<String, WidgetBuilder> routes = {
    home: (context) => const HomeScreen(),
    videoRecording: (context) => const VideoRecordingScreen(),
  };

  static Route<dynamic>? onGenerateRoute(RouteSettings settings) {
    switch (settings.name) {
      case videoFormat:
        final args = settings.arguments as VideoFormatScreenArguments;
        return MaterialPageRoute(
          builder: (context) => VideoFormatScreen(
            mainVideoPath: args.mainVideoPath,
            cameraPositions: List<Vector3>.from(args.cameraPositions),
            cameraRotations: List<Vector3>.from(args.cameraRotations),
          ),
        );
      case videoPlayer:
        final args = settings.arguments as VideoPlayerScreenArguments;
        return MaterialPageRoute(
          builder: (context) => VideoPlayerScreen(
            mainVideoPath: args.mainVideoPath,
          ),
        );
      default:
        return null;
    }
  }
}

// Create a simple class to hold the arguments
class VideoFormatScreenArguments {
  final String mainVideoPath;
  final List cameraPositions;
  final List cameraRotations;

  VideoFormatScreenArguments({
    required this.mainVideoPath,
    required this.cameraPositions,
    required this.cameraRotations,
  });
}

class VideoPlayerScreenArguments {
  final String mainVideoPath;

  VideoPlayerScreenArguments({
    required this.mainVideoPath,
  });
}
