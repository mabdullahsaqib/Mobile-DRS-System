import 'package:flutter/material.dart';

class MasterScreen extends StatefulWidget {
  const MasterScreen({super.key});

  @override
  MasterScreenState createState() => MasterScreenState();
}

class MasterScreenState extends State<MasterScreen> {
  String code = "ABC123"; // hardcoded for now
  String input = "";
  String sentData = "";

  final _controller = TextEditingController();

  void handleSubmit() {
    setState(() {
      sentData = input;
      _controller.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Master (Bowler's End)")),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            const Text("Connection Code", style: TextStyle(fontSize: 20)),
            const SizedBox(height: 10),
            Text(code,
                style:
                    const TextStyle(fontSize: 32, fontWeight: FontWeight.bold)),
            const SizedBox(height: 30),
            TextField(
              controller: _controller,
              decoration: const InputDecoration(
                labelText: "Enter some data",
                border: OutlineInputBorder(),
              ),
              onChanged: (val) => input = val,
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: handleSubmit,
              child: const Text("Send to Secondary"),
            ),
            const SizedBox(height: 30),
            const Text("Sent Data:", style: TextStyle(fontSize: 18)),
            Text(sentData,
                style: const TextStyle(fontSize: 24, color: Colors.green)),
          ],
        ),
      ),
    );
  }
}
