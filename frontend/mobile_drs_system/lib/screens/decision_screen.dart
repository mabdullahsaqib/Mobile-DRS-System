import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:video_player/video_player.dart';
import 'package:mobile_drs_system/screens/video_player_screen.dart';
import 'package:flutter_media_store/flutter_media_store.dart';


class DecisionScreen extends StatefulWidget {
  final Map<String, dynamic> data;
  const DecisionScreen({super.key, required this.data});

  @override
  State<DecisionScreen> createState() => _DecisionScreenState();
}

class _DecisionScreenState extends State<DecisionScreen> {
  String? _tempVideoPath;
  bool _isSaving = false;
  late VideoPlayerController _previewController;
  bool _isPreviewReady = false;

  @override
  void initState() {
    super.initState();
    _decodeAndSaveTempVideo();
  }

  Future<void> _decodeAndSaveTempVideo() async {
    try {
      final base64Video = widget.data['video_base64'];
      if (base64Video == null) return;

      final Uint8List bytes = base64Decode(base64Video);
      final tempDir = await getTemporaryDirectory();
      final filePath = "${tempDir.path}/review_${DateTime.now().millisecondsSinceEpoch}.mp4";
      final file = File(filePath);
      await file.writeAsBytes(bytes);
      _tempVideoPath = filePath;

      _previewController = VideoPlayerController.file(file)
        ..initialize().then((_) {
          setState(() => _isPreviewReady = true);
        });
    } catch (e) {
      print("Failed to decode/save temp video: $e");
    }
  }

  Future<void> _saveToGallery() async {
    if (_tempVideoPath == null) return;

    setState(() => _isSaving = true);
    try {
      final file = File(_tempVideoPath!);
      final flutterMediaStore = FlutterMediaStore();
      String? savedPath;

      await flutterMediaStore.saveFile(
        fileData: await file.readAsBytes(),
        fileName: '${DateTime.now().millisecondsSinceEpoch}.mp4',
        mimeType: "video/mp4",
        rootFolderName: "MobileDRS",
        folderName: "Videos",
        onError: (e) {
          throw Exception("Error saving video: $e");
        },
        onSuccess: (uri, filePath) {
          savedPath = filePath;
        },
      );

      setState(() => _isSaving = false);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(savedPath != null
              ? 'Video saved to gallery! Path: $savedPath'
              : 'Failed to save video.'),
        ),
      );
    } catch (e) {
      setState(() => _isSaving = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error saving video: $e')),
      );
    }
  }

  void _replayVideo() {
    if (_tempVideoPath != null) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => VideoPlayerScreen(mainVideoPath: _tempVideoPath!),
        ),
      );
    }
  }

  @override
  void dispose() {
    if (_isPreviewReady) _previewController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final decision = widget.data['decision']?.toUpperCase() ?? 'PENDING';
    final Color decisionColor = decision == "OUT" ? Colors.redAccent : Colors.green;

    return Scaffold(
      backgroundColor: const Color(0xFF0A3F24),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const Text(
                'REVIEW RESULT',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 26,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                ),
              ),
              const SizedBox(height: 20),

              // Video preview card
              Container(
                height: 200,
                width: double.infinity,
                decoration: BoxDecoration(
                  color: Colors.black,
                  border: Border.all(color: Colors.white30, width: 2),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: _isPreviewReady
                    ? ClipRRect(
                        borderRadius: BorderRadius.circular(16),
                        child: AspectRatio(
                          aspectRatio: _previewController.value.aspectRatio,
                          child: VideoPlayer(_previewController),
                        ),
                      )
                    : const Center(
                        child: CircularProgressIndicator(color: Colors.white),
                      ),
              ),

              const SizedBox(height: 24),

              // Decision box
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                decoration: BoxDecoration(
                  color: decisionColor,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  decision,
                  style: const TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                    letterSpacing: 1.5,
                  ),
                ),
              ),

              const SizedBox(height: 24),

              // Replay Button
              ElevatedButton.icon(
                onPressed: _tempVideoPath != null ? _replayVideo : null,
                icon: const Icon(Icons.replay),
                label: const Text("REPLAY VIDEO"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0B1D1B),
                  foregroundColor: Colors.white,
                  minimumSize: const Size.fromHeight(50),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
              ),

              const SizedBox(height: 12),

              // Save Button
              ElevatedButton.icon(
                onPressed: _isSaving ? null : _saveToGallery,
                icon: const Icon(Icons.save),
                label: Text(_isSaving ? "SAVING..." : "SAVE VIDEO"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF36B37E),
                  foregroundColor: Colors.white,
                  minimumSize: const Size.fromHeight(50),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
              ),

              const Spacer(),

              // Return Home
              TextButton(
                onPressed: () => Navigator.popUntil(context, ModalRoute.withName('/')),
                child: const Text(
                  "Return to Home",
                  style: TextStyle(color: Colors.white70),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
