import 'package:flutter/material.dart';

class AppTokens {
  static const Color bg = Color(0xFF0F1117);
  static const Color card = Color(0xFF171A23);
  static const Color elevated = Color(0xFF1E2230);
  static const Color border = Color(0xFF262B38);
  static const Color textPrimary = Color(0xFFE6E8EE);
  static const Color textSecondary = Color(0xFF8B93A7);
  static const Color purple = Color(0xFF7C5CFF);
  static const Color blue = Color(0xFF4F8CFF);
  static const Color success = Color(0xFF2ECC71);
  static const Color warning = Color(0xFFF5A524);
  static const Color error = Color(0xFFFF5C5C);

  static const double radius = 14.0;
  static const double minTouch = 48.0; // >= 44x44pt ergonomic touch target

  static const LinearGradient brandGradient = LinearGradient(
    colors: [purple, blue],
    begin: Alignment.centerLeft,
    end: Alignment.centerRight,
  );

  static ThemeData buildTheme() {
    return ThemeData.dark(useMaterial3: true).copyWith(
      scaffoldBackgroundColor: bg,
      cardColor: card,
      colorScheme: const ColorScheme.dark(
        primary: purple,
        secondary: blue,
        surface: card,
        error: error,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: bg,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(
          fontFamily: 'Inter',
          fontSize: 18,
          fontWeight: FontWeight.w800,
          color: textPrimary,
        ),
      ),
    );
  }
}
