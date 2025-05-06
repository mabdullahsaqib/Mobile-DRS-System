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

  Widget buildReviewCard(String title) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: const Color(0xFF0B1D1B),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          const Icon(Icons.sports_cricket, size: 32, color: Colors.white),
          const SizedBox(width: 16),
          Text(
            title,
            style: const TextStyle(color: Colors.white, fontSize: 16),
          ),
        ],
      ),
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
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                children: [
                  // Image.asset("assets/cricket_ball.png", width: 32), // replace with your icon
                  const SizedBox(width: 12),
                  const Text(
                    "DRS Umpire",
                    style: TextStyle(
                      fontSize: 26,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 32),

              // Start Review Button
              Center(
                child: ElevatedButton.icon(
                  icon: const Icon(Icons.arrow_forward),
                  label: const Text("START NEW REVIEW"),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF36B37E),
                    foregroundColor: Colors.white,
                    textStyle: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                    padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  onPressed: startNewReview,
                ),
              ),

              const SizedBox(height: 32),

              const Text(
                "Recent Reviews",
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 16),

              // Recent Review Items
              buildReviewCard("Review 1"),
              buildReviewCard("Review 2"),
            ],
          ),
        ),
      ),
    );
  }
}
