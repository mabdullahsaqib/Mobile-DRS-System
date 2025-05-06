import 'dart:async';
import 'package:flutter/material.dart';

class ProcessingScreen extends StatefulWidget {
  final String reviewId;
  const ProcessingScreen({super.key, required this.reviewId});

  @override
  State<ProcessingScreen> createState() => _ProcessingScreenState();
}

class _ProcessingScreenState extends State<ProcessingScreen> {
  Timer? _pollingTimer;

  @override
  void initState() {
    super.initState();
    _startPolling();
  }

void _startPolling() {
  // _pollingTimer = Timer.periodic(const Duration(seconds: 5), (_) async {
  //   try {
  //     final response = await http.get(
  //       Uri.parse('http://10.0.2.2:8000/get-review/${widget.reviewId}'),
  //     );

  //     if (response.statusCode == 200) {
  //       final Map<String, dynamic> data = jsonDecode(response.body);
  //       if (data['status'] == 'done') {
  //         _pollingTimer?.cancel();

  //         Navigator.pushReplacementNamed(
  //           context,
  //           '/decision',
  //           arguments: data,
  //         );
  //       }
  //     }
  //   } catch (e) {
  //     print('Polling error: $e');
  //   }
  // });

  print('Mock polling started for reviewId: ${widget.reviewId}');
}


  @override
  void dispose() {
    _pollingTimer?.cancel();
    super.dispose();
  }

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
              children: const [
                Text(
                  'REVIEW IN PROGRESS',
                  style: TextStyle(
                    color: Colors.greenAccent,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1.5,
                  ),
                ),
                SizedBox(height: 24),
                Icon(Icons.sports_cricket,
                    size: 64, color: Colors.greenAccent),
                SizedBox(height: 24),
                Text(
                  'Third umpire is watching carefully...',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Colors.greenAccent,
                    fontSize: 16,
                  ),
                ),
                SizedBox(height: 48),
                CircularProgressIndicator(
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
