import 'dart:math';

import 'package:flutter/material.dart';
import 'package:mobile_drs_system/controllers/connection.dart';
import 'package:mobile_drs_system/providers/network/server.dart';
import 'package:provider/provider.dart';

class MasterScreen extends StatefulWidget {
  const MasterScreen({super.key});

  @override
  MasterScreenState createState() => MasterScreenState();
}

class MasterScreenState extends State<MasterScreen> {
  String input = "";
  String sentData = "";

  final _controller = TextEditingController();

  void handleSubmit(context) {
    if (input.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Please enter some data")),
      );
      return;
    }
    final serverProvider = Provider.of<ServerProvider>(context, listen: false);
    serverProvider.sendMessage(input);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Data sent successfully")),
    );
    setState(() {
      sentData = input;
      _controller.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    final connectionController = context.watch<ConnectionController>();
    final serverProvider = context.watch<ServerProvider>();
    connectionController
        .startServer(); // Start the server when the screen is built
    return Scaffold(
      appBar: AppBar(title: const Text("Master (Bowler's End)")),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            const SizedBox(height: 10),
            serverProvider.isRunning
                ? Text("Server is running on IP: ${serverProvider.ipAddress}",
                    style: const TextStyle(fontSize: 18))
                : ElevatedButton(
                    onPressed: () {
                      connectionController
                          .startServer()
                          .then((_) {})
                          .catchError((error) {
                        print(error);
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                              content: Text("Error starting server: $error")),
                        );
                      });
                    },
                    child: const Text("Start Server"),
                  ),
            const SizedBox(height: 10),
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
              onPressed: () => handleSubmit(context),
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
