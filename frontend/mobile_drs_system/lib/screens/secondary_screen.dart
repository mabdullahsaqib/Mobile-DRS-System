import 'package:flutter/material.dart';

class SecondaryScreen extends StatefulWidget {
  const SecondaryScreen({super.key});

  @override
  SecondaryScreenState createState() => SecondaryScreenState();
}

class SecondaryScreenState extends State<SecondaryScreen> {
  final _codeController = TextEditingController();
  String receivedData = "(waiting for data...)";

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Secondary (Leg Side)")),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            const Text("Enter Connection Code", style: TextStyle(fontSize: 18)),
            const SizedBox(height: 10),
            TextField(
              controller: _codeController,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                labelText: "e.g. ABC123",
              ),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                // For now we simulate the "connection"
                setState(() {
                  receivedData = "Connected! Waiting for input...";
                });
              },
              child: const Text("Connect"),
            ),
            const SizedBox(height: 30),
            const Text("Received Data:", style: TextStyle(fontSize: 18)),
            Text(receivedData,
                style: const TextStyle(fontSize: 24, color: Colors.blue)),
          ],
        ),
      ),
    );
  }
}
