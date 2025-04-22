import 'package:flutter/widgets.dart';
import 'package:mobile_drs_system/screens/home_screen.dart';
import 'package:mobile_drs_system/screens/kalan_filter.dart';
import 'package:mobile_drs_system/screens/master/master_screen.dart';
import 'package:mobile_drs_system/screens/master/master_waiting_screen.dart';
import 'package:mobile_drs_system/screens/secondary/secondary_screen.dart';

class AppRoutes {
  // Define route names as constants
  static const String home = '/';
  static const String master = '/master';
  static const String secondary = '/secondary';
  static const String kalanFilter = '/kalan-filter';
  static const String masterWaiting = '/master-waiting';

  // Map route names to screen widgets
  static final Map<String, WidgetBuilder> routes = {
    home: (context) => const HomeScreen(),
    master: (context) => const MasterScreen(),
    secondary: (context) => const SecondaryScreen(),
    kalanFilter: (context) => SensorFusionPositionScreen(),
    masterWaiting: (context) => const MasterWaitingScreen(),
  };
}
