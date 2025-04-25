import 'package:flutter/widgets.dart';
import 'package:mobile_drs_system/screens/home_screen.dart';
import 'package:mobile_drs_system/screens/kalan_filter.dart';
import 'package:mobile_drs_system/screens/master_screen.dart';
import 'package:mobile_drs_system/screens/master/master_waiting_screen.dart';
import 'package:mobile_drs_system/screens/video_player_screen.dart';
import 'package:mobile_drs_system/screens/video_recording_screen.dart';

class AppRoutes {
  // Define route names as constants
  static const String home = '/';
  static const String master = '/master';
  static const String kalanFilter = '/kalan-filter';
  static const String masterWaiting = '/master-waiting';
  static const String videoRecording = '/video-recording';
  static const String videoPlayer = '/video-player';

  // Map route names to screen widgets
  static final Map<String, WidgetBuilder> routes = {
    home: (context) => const HomeScreen(),
    master: (context) => const MasterScreen(),
    kalanFilter: (context) => SensorFusionPositionScreen(),
    masterWaiting: (context) => const MasterWaitingScreen(),
    videoRecording: (context) => const VideoRecordingScreen(),
    videoPlayer: (context) => VideoPlayerScreen(
          mainVideoPath: '',
          secondaryVideoPath: '',
        ),
  };
}
