import 'package:flutter/material.dart';

/// A reusable error view widget with retry functionality
class ErrorView extends StatelessWidget {
  const ErrorView({
    super.key,
    required this.error,
    this.onRetry,
    this.title = 'Error',
    this.showDetails = true,
  });

  final Object error;
  final VoidCallback? onRetry;
  final String title;
  final bool showDetails;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Card(
        elevation: 0,
        color: Colors.red.shade50,
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.error_outline,
                size: 64,
                color: Colors.red.shade400,
              ),
              const SizedBox(height: 16),
              Text(
                title,
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.red.shade700,
                ),
              ),
              if (showDetails) ...[
                const SizedBox(height: 8),
                ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 400),
                  child: Text(
                    _getErrorMessage(error),
                    style: TextStyle(
                      color: Colors.red.shade900,
                      fontSize: 14,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
              ],
              if (onRetry != null) ...[
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: onRetry,
                  icon: const Icon(Icons.refresh),
                  label: const Text('Retry'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red.shade600,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 24,
                      vertical: 12,
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  String _getErrorMessage(Object error) {
    if (error.toString().contains('SocketException') ||
        error.toString().contains('NetworkException')) {
      return 'Unable to connect to the server. Please check your internet connection and try again.';
    } else if (error.toString().contains('TimeoutException')) {
      return 'The request took too long. Please try again.';
    } else if (error.toString().contains('401') ||
        error.toString().contains('Unauthorized')) {
      return 'Authentication failed. Please log out and log in again.';
    } else if (error.toString().contains('403') ||
        error.toString().contains('Forbidden')) {
      return 'You do not have permission to access this resource.';
    } else if (error.toString().contains('404') ||
        error.toString().contains('Not Found')) {
      return 'The requested data was not found.';
    } else if (error.toString().contains('500') ||
        error.toString().contains('Internal Server')) {
      return 'A server error occurred. Please try again later.';
    } else {
      return 'An unexpected error occurred: ${error.toString()}';
    }
  }
}

/// A compact error widget for inline use
class InlineErrorView extends StatelessWidget {
  const InlineErrorView({
    super.key,
    required this.error,
    this.onRetry,
  });

  final Object error;
  final VoidCallback? onRetry;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.red.shade200),
      ),
      child: Row(
        children: [
          Icon(Icons.error_outline, color: Colors.red.shade600, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              error.toString(),
              style: TextStyle(
                color: Colors.red.shade900,
                fontSize: 13,
              ),
            ),
          ),
          if (onRetry != null) ...[
            const SizedBox(width: 12),
            IconButton(
              icon: const Icon(Icons.refresh, size: 20),
              onPressed: onRetry,
              color: Colors.red.shade600,
              tooltip: 'Retry',
            ),
          ],
        ],
      ),
    );
  }
}
