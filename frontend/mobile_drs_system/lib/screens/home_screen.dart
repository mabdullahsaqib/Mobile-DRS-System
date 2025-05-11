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

  void pickVideoFromGallery() {
    FlutterMediaStore().pickFile(
      multipleSelect: false,
      onFilesPicked: (List<String> uris) {
        if (uris.isNotEmpty) {
          final file = File(uris.first);
          Navigator.pushNamed(
            context,
            AppRoutes.videoFormat,
            arguments: VideoFormatScreenArguments(
              mainVideoPath: file.path,
              cameraPositions: [],
              cameraRotations: [],
            ),
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
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const SizedBox(height: 12),
              Row(
                children: const [
                  Icon(Icons.sports_cricket, color: Colors.white, size: 28),
                  SizedBox(width: 12),
                  Text(
                    "DRS Umpire",
                    style: TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 48),

              // Button 1: Start Review via Recording
              ElevatedButton.icon(
                icon: const Icon(Icons.videocam),
                label: const Text("RECORD NEW VIDEO"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF36B37E),
                  foregroundColor: Colors.white,
                  textStyle: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                  padding: const EdgeInsets.symmetric(
                      horizontal: 24, vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
                onPressed: startNewReview,
              ),

              const SizedBox(height: 16),

              // Button 2: Pick from Gallery
              ElevatedButton.icon(
                icon: const Icon(Icons.video_library),
                label: const Text("PICK VIDEO FROM GALLERY"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0B1D1B),
                  foregroundColor: Colors.white,
                  textStyle: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                  padding: const EdgeInsets.symmetric(
                      horizontal: 24, vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
                onPressed: pickVideoFromGallery,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
