import 'package:flutter/material.dart';
import 'package:mobile_drs_system/routes/app_routes.dart';

class MasterScreen extends StatefulWidget {
  const MasterScreen({super.key});

  @override
  MasterScreenState createState() => MasterScreenState();
}

class MasterScreenState extends State<MasterScreen> {
  final _controller = TextEditingController();

  void gotoRecordingScreen() async {
    await Navigator.pushNamed(context, AppRoutes.videoRecording);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Master (Bowler's End)")),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: SingleChildScrollView(
          physics: const NeverScrollableScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const SizedBox(height: 10),
              IconButton(
                  onPressed: () => gotoRecordingScreen(),
                  icon: const Icon(Icons.play_arrow)),
            ],
          ),
        ),
      ),
    );
  }
}
