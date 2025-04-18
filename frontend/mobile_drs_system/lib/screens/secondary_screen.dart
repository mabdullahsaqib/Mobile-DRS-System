import 'package:flutter/material.dart';
import 'package:mobile_drs_system/controllers/connection.dart';
import 'package:mobile_drs_system/providers/network/client.dart';
import 'package:provider/provider.dart';

class SecondaryScreen extends StatefulWidget {
  const SecondaryScreen({super.key});

  @override
  SecondaryScreenState createState() => SecondaryScreenState();
}

class SecondaryScreenState extends State<SecondaryScreen> {
  String receivedData = "(waiting for data...)";
  String ipAddress = "";
  final _controller = TextEditingController();
  @override
  Widget build(BuildContext context) {
    final connectionController = context.watch<ConnectionController>();
    final clientProvider = context.watch<ClientProvider>();
    receivedData = clientProvider.receivedData != null
        ? String.fromCharCodes(clientProvider.receivedData!)
        : "(waiting for data...)";
    return Scaffold(
      appBar: AppBar(title: const Text("Secondary (Leg Side)")),
      body: Center(
        child: Column(
          children: [
            const SizedBox(height: 10),
            clientProvider.isConnected
                ? const Text("Connected")
                : Column(
                    children: [
                      Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: TextField(
                          decoration: const InputDecoration(
                            labelText: "Enter IP Address (e.g 10.2.0.2)",
                            border: OutlineInputBorder(),
                          ),
                          controller: _controller,
                          onChanged: (value) {
                            ipAddress = value;
                          },
                        ),
                      ),
                      ElevatedButton(
                        onPressed: () {
                          connectionController
                              .connectToServer(ipAddress)
                              .then((_) {})
                              .catchError((error) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                  content: Text(
                                      "Error connecting to server: $error")),
                            );
                          });
                        },
                        child: const Text("Connect"),
                      ),
                    ],
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
