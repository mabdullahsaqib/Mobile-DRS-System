import 'package:flutter/material.dart';

class RoleButton extends StatelessWidget {
  final String label;
  final VoidCallback onTap;

  const RoleButton({
    super.key,
    required this.label,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      style: ElevatedButton.styleFrom(
        padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 20),
        textStyle: const TextStyle(fontSize: 18),
      ),
      onPressed: onTap,
      child: Text(label),
    );
  }
}
