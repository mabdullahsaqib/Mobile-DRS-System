import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';

class DecisionScreen extends StatefulWidget {
  final Map<String, dynamic> data;
  const DecisionScreen({super.key, required this.data});

  @override
  State<DecisionScreen> createState() => _DecisionScreenState();
}

class _DecisionScreenState extends State<DecisionScreen> {
  late VideoPlayerController _videoController;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _videoController = VideoPlayerController.network(widget.data['video_url'])
      ..initialize().then((_) {
        setState(() => isLoading = false);
      });
  }

  @override
  void dispose() {
    _videoController.dispose();
    super.dispose();
  }

  void _replayVideo() {
    _videoController.seekTo(Duration.zero);
    _videoController.play();
  }

  void _mockSaveVideo() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Video saved (mocked)!")),
    );
  }

  @override
  Widget build(BuildContext context) {
    final decision = widget.data['decision']?.toUpperCase() ?? 'PENDING';

    return Scaffold(
      backgroundColor: const Color(0xFF0A3F24),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: isLoading
              ? const Center(
                  child: CircularProgressIndicator(color: Colors.white),
                )
              : Column(
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

                    // Video Preview
                    AspectRatio(
                      aspectRatio: _videoController.value.aspectRatio,
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(12),
                        child: VideoPlayer(_videoController),
                      ),
                    ),

                    const SizedBox(height: 24),

                    // Decision Box
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 32, vertical: 16),
                      decoration: BoxDecoration(
                        color: decision == "OUT"
                            ? Colors.redAccent
                            : Colors.green,
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
                      onPressed: _replayVideo,
                      icon: const Icon(Icons.replay),
                      label: const Text("REPLAY VIDEO"),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF0B1D1B),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(
                            horizontal: 24, vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                    ),
                    const SizedBox(height: 12),

                    // Save Button (Mocked)
                    ElevatedButton.icon(
                      onPressed: _mockSaveVideo,
                      icon: const Icon(Icons.save),
                      label: const Text("SAVE VIDEO"),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF36B37E),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(
                            horizontal: 24, vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),

                    // Return to Home
                    TextButton(
                      onPressed: () => Navigator.popUntil(
                          context, ModalRoute.withName('/home')),
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
