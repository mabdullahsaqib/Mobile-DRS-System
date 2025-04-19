import 'package:flutter/material.dart';
import 'package:mobile_drs_system/providers/camera.dart';
import 'package:mobile_drs_system/controllers/connection.dart';
import 'package:mobile_drs_system/providers/network/client.dart';
import 'package:mobile_drs_system/providers/network/server.dart';
import 'package:provider/provider.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(MultiProvider(providers: [
    ChangeNotifierProvider(create: (_) => ServerProvider()),
    ChangeNotifierProvider(create: (_) => ClientProvider()),
    Provider(
        create: (_) => ConnectionController(
            Provider.of<ServerProvider>(_, listen: false),
            Provider.of<ClientProvider>(_, listen: false))),
    ChangeNotifierProvider(create: (_) => CameraService()),
  ], child: const MainApp()));
}

class MainApp extends StatelessWidget {
  const MainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Mobile DRS App',
      home: const HomeScreen(),
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      debugShowCheckedModeBanner: false,
    );
  }
}
