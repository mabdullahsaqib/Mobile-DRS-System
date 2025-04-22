// import 'package:flutter/material.dart';
// import 'package:vector_math/vector_math_64.dart' as vector;

// class ArScreen extends StatefulWidget {
//   const ArScreen({super.key});

//   @override
//   State<ArScreen> createState() => _ArScreenState();
// }

// class _ArScreenState extends State<ArScreen> {
//   ArCoreController? arCoreController;

//   void _onArCoreViewCreated(ArCoreController controller) {
//     arCoreController = controller;

//     // Delay the addition of ARCore nodes to ensure OpenGL context is ready
//     Future.delayed(Duration(milliseconds: 500), () {
//       final material = ArCoreMaterial(color: Colors.green);
//       final sphere = ArCoreSphere(materials: [material], radius: 0.1);
//       final node = ArCoreNode(
//         shape: sphere,
//         position: vector.Vector3(0, 0, -1), // 1 meter in front
//       );

//       arCoreController?.addArCoreNode(node);
//     });
//   }

//   @override
//   void dispose() {
//     arCoreController?.dispose();
//     super.dispose();
//   }

//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       appBar: AppBar(title: const Text('AR View')),
//       body: ArCoreView(onArCoreViewCreated: _onArCoreViewCreated),
//     );
//   }
// }
