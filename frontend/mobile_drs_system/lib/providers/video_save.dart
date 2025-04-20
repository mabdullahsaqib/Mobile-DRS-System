import 'package:flutter/foundation.dart';

class VideoSaveDataProvider with ChangeNotifier {
  String _mainVideoPath = '';
  String _secondaryVideoPath = '';
  bool isAtVideoPlayerScreen = false;

  String get mainVideoPath => _mainVideoPath;
  String get secondaryVideoPath => _secondaryVideoPath;

  void setMainVideoPath(String path) {
    _mainVideoPath = path;
    notifyListeners();
  }

  void clearMainVideoPath() {
    _mainVideoPath = '';
    notifyListeners();
  }

  void setSecondaryVideoPath(String path) {
    _secondaryVideoPath = path;
    notifyListeners();
  }

  void clearSecondaryVideoPath() {
    _secondaryVideoPath = '';
    notifyListeners();
  }
}
