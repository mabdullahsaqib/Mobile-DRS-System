import 'package:flutter/material.dart';

class ProcessingScreen extends StatelessWidget {
  const ProcessingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A3F24),
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text(
                  'REVIEW IN PROGRESS',
                  style: TextStyle(
                    color: Colors.greenAccent,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1.5,
                  ),
                ),
                const SizedBox(height: 24),

                // Optional: Animated Icon / Logo
                const Icon(Icons.sports_cricket,
                    size: 64, color: Colors.greenAccent),

                const SizedBox(height: 24),
                const Text(
                  'Third umpire is watching carefully...',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Colors.greenAccent,
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 48),
                const CircularProgressIndicator(
                  color: Colors.greenAccent,
                  strokeWidth: 4,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
