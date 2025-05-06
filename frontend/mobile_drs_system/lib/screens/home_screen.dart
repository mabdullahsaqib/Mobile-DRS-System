import 'package:flutter/material.dart';
import 'package:mobile_drs_system/routes/app_routes.dart';
import 'package:mobile_drs_system/utils/utils.dart';
import 'dart:io';
import 'package:flutter_media_store/flutter_media_store.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    requestPermissions();
  }

  void showToast(String message) {
    final snackBar = SnackBar(content: Text(message));
    ScaffoldMessenger.of(context).showSnackBar(snackBar);
  }

  void startNewReview() {
    Navigator.pushNamed(context, AppRoutes.videoRecording);
  }

  void pickVideosFromStorage() {
    FlutterMediaStore().pickFile(
      multipleSelect: false,
      // mimeType: "video/mp4",
      onFilesPicked: (List<String> uris) {
        if (uris.isNotEmpty) {
          final file = File(uris.first);
          Navigator.pushNamed(
            context,
            AppRoutes.videoPlayer,
            arguments: VideoPlayerScreenArguments(mainVideoPath: file.path),
          );
        } else {
          showToast("No video selected.");
        }
      },
      onError: (String error) {
        showToast("Failed to pick video: $error");
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A3F24),
      appBar: AppBar(
        title: const Text("Review Center"),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Center(
              child: ElevatedButton.icon(
                icon: const Icon(Icons.play_circle_fill),
                label: const Text("START NEW REVIEW"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.tealAccent.shade700,
                  foregroundColor: Colors.white,
                  textStyle: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                ),
                onPressed: startNewReview,
              ),
            ),
            const SizedBox(height: 32),
            ElevatedButton.icon(
              icon: const Icon(Icons.folder_open),
              label: const Text("OPEN SAVED VIDEO"),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.white10,
                foregroundColor: Colors.white,
                textStyle: const TextStyle(fontSize: 16),
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
              ),
              onPressed: pickVideosFromStorage,
            ),
          ],
        ),
      ),
    );
  }
}
